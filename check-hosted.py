"""Exercise the hosted build the way a visitor does, and fail on any console error.

This exists because the hosted site had a broken Validate & build ZIP button
while every other guard passed. app.js used AOO_MIN_VERSION without importing
it. The standalone concatenates core.js and app.js into one scope, so the name
resolved and the download worked perfectly; the hosted build loads app.js as a
real module, where the same line throws ReferenceError and the publish screen
never opens.

Every other guard reads the standalone. None of them could have seen it, and
none of them clicked anything. So this one does both: it drives docs/app.html,
which has the module topology the site actually ships, and it clicks through
the flow a writer uses.

Two checks that matter more than they look:

  console errors   a ReferenceError inside a click handler is silent to the
                   user - the button simply does nothing - so the console is
                   the only place it shows up
  import audit     the same class of bug, caught statically before it runs

    python check-hosted.py
"""
import http.server, os, pathlib, re, shutil, socketserver, subprocess, sys, tempfile, threading

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SRC = ROOT / "source"
PORT = 8291
CHROME_CANDIDATES = [
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def import_audit():
    """Every core.js export app.js references must be imported."""
    core = (SRC / "core.js").read_text(encoding="utf-8")
    app = (SRC / "app.js").read_text(encoding="utf-8")
    decl = r"(?m)^export\s+(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)"
    exports = set(re.findall(decl, core))
    m = re.search(r"^import\s*\{([^}]*)\}\s*from", app, re.M)
    imported = set(x.strip() for x in m.group(1).split(",")) if m else set()
    own = set(re.findall(r"(?m)^(?:function|const|let|var|class)\s+([A-Za-z_$][\w$]*)", app))
    used = set()
    for name in exports:
        if re.search(r"(?<![\w$.])" + re.escape(name) + r"(?![\w$])", app):
            used.add(name)
    missing = sorted(used - imported - own)
    return imported, missing


PROBE = """<script>
window.__err=[];
addEventListener("error",function(e){window.__err.push(e.message)});
addEventListener("unhandledrejection",function(e){window.__err.push("rejection: "+e.reason)});
addEventListener("load",function(){
 var out=[];
 function done(){
   out.push("console errors: "+(window.__err.length?window.__err.join(" | "):"none"));
   document.title="HS7"+out.join(" ;; ")+"HS7END";
 }
 setTimeout(function(){
  ["keydown","keyup"].forEach(function(t){
    document.dispatchEvent(new KeyboardEvent(t,{key:"Enter",bubbles:true}));});
  setTimeout(function(){
   var w=document.getElementById("welcomeScreen");
   if(w&&!w.hidden){var c=document.getElementById("welcomeClose");if(c)c.click();}
   var ex=document.getElementById("exampleSelect");
   if(ex&&ex.options.length>2){ex.value=ex.options[2].value;
     ex.dispatchEvent(new Event("change",{bubbles:true}));}
   setTimeout(function(){
     out.push("example loaded: "+(document.querySelectorAll("#workList .nav-item").length>0));
     var b=document.getElementById("buildBtn");
     if(!b){out.push("buildBtn: MISSING");return done()}
     b.click();
     setTimeout(function(){
       var ps=document.getElementById("publishScreen");
       out.push("publish screen opens: "+(ps&&!ps.hidden));
       out.push("nexus text generated: "
         +(!!document.getElementById("nexusText")
           &&document.getElementById("nexusText").value.length>200));
       out.push("diff panel filled: "
         +(!!document.getElementById("diffLede")
           &&document.getElementById("diffLede").textContent.length>20));
       done();
     },1200);
   },1500);
  },600);
 },2900);
});
</script>"""


def main():
    if not DOCS.exists():
        sys.exit("FAIL: docs/ not built; run build-web.py first")

    imported, missing = import_audit()
    if missing:
        sys.exit("FAIL: app.js uses %s from core.js without importing it.\n"
                 "  The standalone would still work - it shares one scope - but the\n"
                 "  hosted build loads app.js as a module and throws."
                 % ", ".join(missing))
    print("  module imports: %d names, none missing" % len(imported))

    chrome = next((c for c in CHROME_CANDIDATES if os.path.exists(c)), None)
    if not chrome:
        sys.exit("FAIL: no Chrome or Edge found")

    # The probe page has to be served from the site, not loaded as a local file
    # with a <base> tag: ES module imports resolve against the module's own URL,
    # so app.js would look for core.js beside the temp file and silently never
    # boot. Copy the built site, drop the probe page into it, serve that.
    stage = pathlib.Path(tempfile.mkdtemp(prefix="hosted-"))
    site = stage / "site"
    shutil.copytree(DOCS, site)
    app_html = (site / "app.html").read_text(encoding="utf-8")
    (site / "_probe.html").write_text(app_html.replace("</body>", PROBE + "</body>"),
                                      encoding="utf-8")

    os.chdir(site)
    quiet = type("Quiet", (http.server.SimpleHTTPRequestHandler,),
                 {"log_message": lambda *a, **k: None})
    srv = socketserver.TCPServer(("127.0.0.1", PORT), quiet)
    srv.allow_reuse_address = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run",
                              "--window-size=1440,900", "--virtual-time-budget=18000",
                              "--user-data-dir=%s" % (stage / "prof"), "--dump-dom",
                              "http://127.0.0.1:%d/_probe.html" % PORT],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=300).stdout
    finally:
        srv.shutdown()
        os.chdir(ROOT)
        shutil.rmtree(stage, ignore_errors=True)

    m = re.search(r"HS7(.*?)HS7END", dom, re.S)
    if not m:
        sys.exit("FAIL: the hosted page never reported; it threw before finishing")

    bad = []
    for line in m.group(1).split(" ;; "):
        print("  " + line)
        if line.startswith("console errors:") and "none" not in line:
            bad.append(line)
        if ": false" in line or ": MISSING" in line:
            bad.append(line)

    if bad:
        sys.exit("FAIL: the hosted build is broken:\n  " + "\n  ".join(bad))
    print("SUMMARY hosted build works end to end")
    return 0


if __name__ == "__main__":
    sys.exit(main())
