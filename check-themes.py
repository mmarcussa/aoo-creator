"""Audit every theme for unreadable colour pairs.

Three separate themes shipped with the same defect: a label rendered in a muted
tone on a selection bar, legible in the theme it was designed against and
invisible in another. Eyeballing does not scale past a handful of themes.

For each theme this walks the real interface and computes WCAG contrast for the
pairs that have actually broken before, plus the ones most likely to.

Getting the measurement right mattered more than expected:
  * rgb() is 0-255 while color(srgb ...) is 0-1; assuming one inverts the other
  * translucent backgrounds (color-mix with transparent) must be composited over
    their ancestors, or foreground and background read as the same hue and every
    theme reports a perfect 1.00 failure
  * an element painted with a gradient reports no background-color at all, so it
    is reported as unmeasurable rather than measured against the wrong surface

    python check-themes.py

Exits 0 if every measurable pair clears its threshold, 1 otherwise.
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
PAGE = ROOT / "AOO-Creator-v0.2.0-standalone.html"

THRESHOLD_TEXT = 4.5   # WCAG AA, body text
THRESHOLD_UI = 3.0     # WCAG AA, large text and UI components

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

PROBE = r"""
<script>
function parse(c){
  var sc = /^color\(/.test(c) ? 1 : 255;
  var m = (c.match(/[\d.]+/g) || ["0","0","0"]).map(parseFloat);
  return {r:m[0]/sc, g:m[1]/sc, b:m[2]/sc, a:(m.length>3?m[3]:1)};
}
function over(fg,bg){
  return {r:fg.r*fg.a+bg.r*(1-fg.a), g:fg.g*fg.a+bg.g*(1-fg.a), b:fg.b*fg.a+bg.b*(1-fg.a), a:1};
}
function lum(p){
  function ch(v){ return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4); }
  return 0.2126*ch(p.r)+0.7152*ch(p.g)+0.0722*ch(p.b);
}
function ratio(a,b){
  var l1=lum(a), l2=lum(b);
  return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
}
function paintedBg(el){
  var stack=[], n=el;
  while(n){
    var cs=getComputedStyle(n);
    if(/gradient/.test(cs.backgroundImage)) return null;
    var p=parse(cs.backgroundColor);
    if(p.a>0) stack.push(p);
    if(p.a>=1) break;
    n=n.parentElement;
  }
  var base = stack.length ? stack.pop() : parse(getComputedStyle(document.body).backgroundColor);
  if(base.a<1) base = over(base, parse(getComputedStyle(document.documentElement).backgroundColor));
  while(stack.length) base = over(stack.pop(), base);
  return base;
}
function fmt(p){ return "rgb("+[p.r,p.g,p.b].map(function(v){return Math.round(v*255);}).join(",")+")"; }
function pair(name,sel,kind){
  var el=document.querySelector(sel); if(!el) return null;
  var fg=parse(getComputedStyle(el).color);
  var bg=paintedBg(el);
  if(!bg) return {name:name,kind:kind,r:null,fg:fmt(fg),bg:"gradient"};
  if(fg.a<1) fg=over(fg,bg);
  return {name:name,kind:kind,r:+ratio(fg,bg).toFixed(2),fg:fmt(fg),bg:fmt(bg)};
}
window.addEventListener("load",function(){setTimeout(function(){
 try{
  var w=document.getElementById("welcomeScreen"); if(w) w.hidden=true;
  var sel=document.getElementById("themeSelect");
  var themes=[].map.call(sel.querySelectorAll("option"),function(o){return o.value;});
  function set(s,v){var e=document.querySelector(s);if(e){e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}}
  set('[data-bind="title"]',"A Work");
  set('[data-chapter-field="body"]',"Some text.");
  document.getElementById("addChapterBtn").click();
  var results={};
  function step(i){
    if(i>=themes.length){document.getElementById("out").textContent="@AUDIT@"+JSON.stringify(results)+"@END@";return;}
    sel.value=themes[i]; sel.dispatchEvent(new Event("change",{bubbles:true}));
    setTimeout(function(){
      results[themes[i]]=[
        pair("body text","#workHeading","text"),
        pair("muted rail text",".author-summary span","text"),
        pair("selected work title","#workList .nav-item.active .work-title","text"),
        pair("selected work byline","#workList .nav-item.active .work-by","text"),
        pair("selected chapter name",".strip-item.active .strip-name","text"),
        pair("selected chapter count",".strip-item.active small","ui"),
        pair("selected chapter number",".strip-item.active .strip-num","ui"),
        pair("tab badge",".editor-tabs .badge","ui"),
        pair("backup chip","#backupState","ui"),
        pair("primary button","#buildBtn","text"),
        pair("status text","#statusBar","text"),
        pair("section label",".section-title h2","ui"),
        pair("works attention","#worksAttention","ui")
      ].filter(Boolean);
      step(i+1);
    },90);
  }
  step(0);
 }catch(e){document.getElementById("out").textContent='@AUDIT@{"error":"'+e.message+'"}@END@';}
},700);});</script>
"""


def main():
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("FAIL: no Edge or Chrome found")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aoo-themes-"))
    try:
        page = tmp / "audit.html"
        page.write_text(PAGE.read_text(encoding="utf-8") +
                        '<pre id="out" style="display:none"></pre>' + PROBE, encoding="utf-8")
        out = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--no-first-run",
             "--virtual-time-budget=30000", f"--user-data-dir={tmp/'p'}", "--dump-dom", page.as_uri()],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300).stdout
        m = re.search(r"@AUDIT@(.*?)@END@", out, re.S)
        if not m:
            sys.exit("FAIL: audit did not report")
        data = json.loads(m.group(1))
        if "error" in data:
            sys.exit("FAIL: " + data["error"])

        failures = 0
        for theme, checks in sorted(data.items()):
            bad = [c for c in checks if c["r"] is not None and
                   c["r"] < (THRESHOLD_TEXT if c["kind"] == "text" else THRESHOLD_UI)]
            if bad:
                failures += len(bad)
                print("FAIL  %-9s %s" % (theme, ", ".join(
                    "%s %.2f (%s on %s)" % (c["name"], c["r"], c["fg"], c["bg"]) for c in bad)))
        skipped = sum(1 for cs in data.values() for c in cs if c["r"] is None)
        print("SUMMARY %d themes, %d failure(s), %d gradient pair(s) unmeasurable"
              % (len(data), failures, skipped))
        return 1 if failures else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
