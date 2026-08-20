"""Measure the writing surface across every theme.

This is a writer's tool, so the manuscript is the one surface that must stay
comfortable to read no matter which theme is on. The levers that decide that
are measurable, so they are measured rather than eyeballed:

  measure      characters per line. 45-75 is the comfortable band for prose;
               past ~85 the eye loses its place returning to the next line.
  leading      line-height. Below ~1.5 long prose gets cramped.
  size         computed px. Below 16px is tiring for sustained reading; this is a
               writer's tool, so it holds a stricter floor than a generic page.
  contrast     text against the manuscript's own background, WCAG ratio.
  family       a proportional face reads faster than a monospace one for prose.

Reports every theme and fails on the ones that fall outside the band.
"""
import os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
VERSION = (ROOT / "source" / "VERSION").read_text(encoding="utf-8").strip()
PAGE = ROOT / ("AOO-Creator-v%s-standalone.html" % VERSION)

MIN_SIZE, MIN_LEADING, MAX_MEASURE, MIN_CONTRAST = 16.0, 1.5, 85.0, 4.5

probe = """<script>
addEventListener("load", function () {
  function lum(c) {
    var m = c.match(/[\\d.]+/g).map(Number);
    var a = m.slice(0, 3).map(function (v) {
      v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4);
    });
    return .2126 * a[0] + .7152 * a[1] + .0722 * a[2];
  }
  function ratio(f, b) {
    var x = lum(f), y = lum(b);
    return ((Math.max(x, y) + .05) / (Math.min(x, y) + .05));
  }
  function solid(el) {
    // walk up until something is not transparent
    while (el) {
      var b = getComputedStyle(el).backgroundColor;
      if (b && !/rgba\\(0, 0, 0, 0\\)|transparent/.test(b)) return b;
      el = el.parentElement;
    }
    return "rgb(0,0,0)";
  }
  setTimeout(function () {
    ["keydown","keyup"].forEach(function (t) {
      document.dispatchEvent(new KeyboardEvent(t,{key:"Enter",bubbles:true}));
    });
    setTimeout(function () {
      var w = document.getElementById("welcomeScreen");
      if (w && !w.hidden) { var c = document.getElementById("welcomeClose"); if (c) c.click(); }
      var sel = document.getElementById("themeSelect");
      var themes = Array.prototype.map.call(sel.options, function (o) { return o.value; });
      // measuring before document.fonts.ready races the loader and
      // reports fallback metrics for every theme
      document.fonts.ready.then(function () {
      var i = 0, out = [];
      (function nxt() {
        if (i >= themes.length) {
          document.title = "RD9" + out.join(" ;; ") + "RD9END";
          return;
        }
        var th = themes[i++];
        sel.value = th;
        sel.dispatchEvent(new Event("change", {bubbles: true}));
        setTimeout(function () {
          var m = document.querySelector(".manuscript");
          var cs = getComputedStyle(m);
          var size = parseFloat(cs.fontSize);
          var lh = parseFloat(cs.lineHeight) / size;
          // width of one '0' in the manuscript's own face gives characters/line
          var span = document.createElement("span");
          span.textContent = "00000000000000000000";
          span.style.cssText = "position:absolute;visibility:hidden;white-space:pre;font:" +
            cs.fontWeight + " " + cs.fontSize + "/" + cs.lineHeight + " " + cs.fontFamily;
          document.body.appendChild(span);
          var ch = span.getBoundingClientRect().width / 20;
          span.remove();
          var inner = m.clientWidth
            - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
          var fam = cs.fontFamily.split(",")[0].replace(/["']/g, "");
          // the stack's first name is what was ASKED for. With embedded faces
          // that is not proof it arrived: a missing woff2 silently renders in
          // the fallback, and reporting the request would hide it.
          var ok = document.fonts.check(cs.fontSize + " '" + fam + "'");
          out.push([th, size.toFixed(1), lh.toFixed(2), (inner / ch).toFixed(0),
                    ratio(cs.color, solid(m)).toFixed(2), fam,
                    ok ? "loaded" : "MISSING"].join("|"));
          nxt();
        }, 90);
      })();
      });
    }, 500);
  }, 2900);
});
</script>"""

stage = pathlib.Path(tempfile.mkdtemp(prefix="read-"))
try:
    page = stage / "p.html"
    page.write_text(PAGE.read_text(encoding="utf-8").replace("</body>", probe + "</body>"),
                    encoding="utf-8")
    chrome = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run",
                          "--virtual-time-budget=25000", "--window-size=1440,900",
                          f"--user-data-dir={stage / 'p'}", "--dump-dom", page.as_uri()],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=300).stdout
finally:
    shutil.rmtree(stage, ignore_errors=True)

m = re.search(r"RD9(.*?)RD9END", dom, re.S)
if not m:
    sys.exit("FAIL: readability probe did not report; the page likely threw")

print("  %-10s %6s %8s %9s %9s  %-20s %s"
      % ("theme", "size", "leading", "measure", "contrast", "family", "face"))
fails = []
for row in m.group(1).split(" ;; "):
    th, size, lh, meas, con, fam, loaded = row.split("|")
    flags = []
    if float(size) < MIN_SIZE:      flags.append("size")
    if float(lh) < MIN_LEADING:     flags.append("leading")
    if float(meas) > MAX_MEASURE:   flags.append("measure")
    if float(con) < MIN_CONTRAST:   flags.append("contrast")
    if loaded != "loaded":          flags.append("font-not-loaded")
    mark = "  <-- " + ",".join(flags) if flags else ""
    print("  %-10s %6s %8s %9s %9s  %-20s %-8s%s"
          % (th, size, lh, meas, con, fam[:20], loaded, mark))
    if flags:
        fails.append("%s (%s)" % (th, ",".join(flags)))

print()
if fails:
    sys.exit("FAIL: writing surface outside the readable band in %d theme(s): %s"
             % (len(fails), "; ".join(fails)))
print("SUMMARY writing surface readable in every theme")
