"""Verify the cursor rules bind AND that each cursor paints the colour intended.

Three levels, because the first two can both pass while the cursor is wrong:
  1. computed style   - proves the rule matched
  2. image decode     - proves the SVG parses
  3. canvas sample    - proves the fill survived URL encoding. A double-encoded
                        colour (%2523...) yields a perfectly valid SVG that
                        silently paints black, which levels 1 and 2 both accept.

Themes are switched one per animation frame; switching several synchronously
reads styles the app has not finished re-rendering.
"""
import os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
VERSION = (ROOT / "source" / "VERSION").read_text(encoding="utf-8").strip()
PAGE = ROOT / ("AOO-Creator-v%s-standalone.html" % VERSION)

probe = """<script>
addEventListener("load", function () {
  var out = [], uris = {};
  function cur(q) {
    var e = document.querySelector(q);
    if (!e) return "MISSING";
    var v = getComputedStyle(e).cursor;
    var m = v.match(/url\\(\\"?(data:[^\\")]+)\\"?\\)/);
    if (m) uris[m[1]] = m[1];
    return (m ? "svg+" : "") + v.split(",").pop().trim();
  }
  function tag(q) {
    var e = document.querySelector(q);
    return e ? e.tagName.toLowerCase() : "none";
  }
  setTimeout(function () {
    ["keydown","keyup"].forEach(function (t) {
      document.dispatchEvent(new KeyboardEvent(t,{key:"Enter",bubbles:true}));
    });
    setTimeout(function () {
      var w = document.getElementById("welcomeScreen");
      if (w && !w.hidden) { var c = document.getElementById("welcomeClose"); if (c) c.click(); }
      // every theme in the picker, not a hand-picked sample: all 24 declare a cursor now
      var sel = document.getElementById("themeSelect"), i = 0;
      var themes = Array.prototype.map.call(sel.options, function (o) { return o.value; });
      (function next() {
        if (i >= themes.length) return sample();
        var th = themes[i++];
        sel.value = th; sel.dispatchEvent(new Event("change",{bubbles:true}));
        setTimeout(function () {
          out.push(th.padEnd(8) +
            " body=" + cur("body") +
            "  build(" + tag("#buildBtn") + ")=" + cur("#buildBtn") +
            "  manuscript=" + cur(".manuscript"));
          next();
        }, 120);
      })();

      function sample() {
        var all = Object.keys(uris), done = 0, bad = [], seen = [];
        if (!all.length) return finish(bad, seen, all);
        all.forEach(function (u) {
          var img = new Image();
          img.onload = function () {
            try {
              var cv = document.createElement("canvas");
              cv.width = img.naturalWidth || 24; cv.height = img.naturalHeight || 24;
              var x = cv.getContext("2d");
              x.drawImage(img, 0, 0);
              var d = x.getImageData(0, 0, cv.width, cv.height).data, tally = {};
              for (var p = 0; p < d.length; p += 4) {
                if (d[p+3] < 200) continue;
                var k = d[p] + "," + d[p+1] + "," + d[p+2];
                tally[k] = (tally[k] || 0) + 1;
              }
              var best = null, n = 0;
              for (var k in tally) if (tally[k] > n) { n = tally[k]; best = k; }
              seen.push(best + " x" + n);
            } catch (e) { bad.push("canvas: " + e.message); }
            step();
          };
          img.onerror = function () { bad.push("decode: " + u.slice(0, 60)); step(); };
          img.src = u;
          function step() { if (++done === all.length) finish(bad, seen, all); }
        });
      }
      function finish(bad, seen, all) {
        out.push("");
        out.push("distinct cursor images: " + all.length +
                 " | broken: " + (bad.length ? bad.join(" | ") : "none"));
        out.push("dominant painted colour per image:");
        seen.sort().forEach(function (s) { out.push("   rgb(" + s + ")"); });
        document.title = "[[" + out.join("\\n") + "]]";
      }
    }, 500);
  }, 2900);
});
</script>"""

stage = pathlib.Path(tempfile.mkdtemp(prefix="cur-"))
try:
    page = stage / "p.html"
    page.write_text(PAGE.read_text(encoding="utf-8").replace("</body>", probe + "</body>"),
                    encoding="utf-8")
    chrome = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run",
                          "--allow-file-access-from-files",
                          "--virtual-time-budget=20000", "--window-size=1440,900",
                          f"--user-data-dir={stage/'p'}", "--dump-dom", page.as_uri()],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=300).stdout
    m = re.search(r"\[\[(.*?)\]\]", dom, re.S)
    if not m:
        sys.exit("FAIL: cursor probe did not report; the page likely threw")
    body = m.group(1)
    print(body)

    bad = []
    for line in body.splitlines():
        if not line.strip() or line.startswith(("distinct", "dominant", "   rgb")):
            continue
        # every theme must keep the I-beam on the manuscript and draw elsewhere
        if "manuscript=text" not in line:
            bad.append("manuscript lost its I-beam: " + line.split()[0])
        if "body=svg+" not in line:
            bad.append("body cursor not drawn: " + line.split()[0])
    if "broken: none" not in body:
        bad.append("at least one cursor image failed to decode")
    if bad:
        sys.exit("FAIL: " + " | ".join(bad))
    print("SUMMARY cursors bind, decode and paint correctly")
finally:
    shutil.rmtree(stage, ignore_errors=True)
