"""Capture the tool frames that open the landing-page sequence.

The sequence only works if both halves show the same fic, so this loads the
bundled ghostpocket example and sets the chapter titles and summary to match the
in-game pack. The tool is genuinely rendering that content - nothing is painted
on afterwards.

Frames are shot at the same aspect as the in-game frames (1280x573, 2.234:1) so
the sequence container never resizes between steps.

Animations are frozen for the capture: virtual time can strand a re-render's
fade at its opacity:0 start frame, which reads as a blank pane.
"""
import os, pathlib, shutil, subprocess, sys, tempfile
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
VERSION = (ROOT / "source" / "VERSION").read_text(encoding="utf-8").strip()
PAGE = ROOT / ("AOO-Creator-v%s-standalone.html" % VERSION)
OUT = ROOT / "source" / "assets" / "ingame"
CHROME = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")

W, H = 1600, 716          # 2.234:1, matching the in-game frames
FINAL_W = 1280

FREEZE = ("<style>*,*::before,*::after{animation:none!important;"
          "transition:none!important}</style>")

# match the in-game pack so the same fic appears on both sides
CH1 = "Signal One: Brokered"
CH2 = "Signal Two: Buried"
SUMMARY = ("two fragments of the same transmission: one brokered, one left "
           "where the signal died.")

BASE = """<script>
function fire(el, type) { el.dispatchEvent(new Event(type, {bubbles: true})); }
function setField(el, value) { el.value = value; fire(el, "input"); fire(el, "change"); }
addEventListener("load", function () {
  setTimeout(function () {
    ["keydown","keyup"].forEach(function (t) {
      document.dispatchEvent(new KeyboardEvent(t, {key: "Enter", bubbles: true}));
    });
    setTimeout(function () {
      var w = document.getElementById("welcomeScreen");
      if (w && !w.hidden) { var c = document.getElementById("welcomeClose"); if (c) c.click(); }
      var ex = document.getElementById("exampleSelect");
      if (ex && ex.options.length > 2) {
        ex.value = ex.options[2].value;
        fire(ex, "change");
      }
      setTimeout(function () {
        var first = document.querySelector("#workList .nav-item");
        if (first) first.click();
        setTimeout(function () {
          // Rename the chapters to match the in-game pack. Selecting a
          // chapter re-renders the strip, so a NodeList captured up front goes
          // stale and every write lands on the same chapter - re-query each
          // time and let the render settle between steps.
          var titles = ["__CH1__", "__CH2__"];
          function rename(i, done) {
            if (i >= titles.length) return done();
            var items = document.querySelectorAll(".strip-item");
            if (i >= items.length) return done();
            items[i].click();
            setTimeout(function () {
              var t = document.querySelector('[data-chapter-field="title"]');
              if (t) setField(t, titles[i]);
              setTimeout(function () { rename(i + 1, done); }, 250);
            }, 250);
          }
          rename(0, function () {
            var items = document.querySelectorAll(".strip-item");
            if (items.length) items[0].click();
            var sum = document.querySelector('[data-bind="summary"]');
            if (sum) setField(sum, "__SUMMARY__");
            setTimeout(function () { __STEP__ }, 500);
          });
        }, 400);
      }, 500);
    }, 400);
  }, 2900);
});
</script>"""

FRAMES = [
    ("tool-write", "", "You write the fic here"),
    ("tool-build", 'var b=document.getElementById("buildBtn"); if(b) b.click();',
     "Validation passes, and it builds the mod"),
]


def shoot(step_js, dest):
    probe = (BASE.replace("__CH1__", CH1).replace("__CH2__", CH2)
                 .replace("__SUMMARY__", SUMMARY).replace("__STEP__", step_js))
    stage = pathlib.Path(tempfile.mkdtemp(prefix="toolshot-"))
    try:
        page = stage / "p.html"
        page.write_text(PAGE.read_text(encoding="utf-8")
                        .replace("</body>", FREEZE + probe + "</body>"), encoding="utf-8")
        raw = stage / "raw.png"
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-first-run",
                        "--hide-scrollbars", f"--user-data-dir={stage / 'p'}",
                        f"--screenshot={raw}", f"--window-size={W},{H}",
                        "--virtual-time-budget=22000", page.as_uri()],
                       capture_output=True, timeout=300)
        if not raw.exists():
            sys.exit("FAIL: chrome produced no screenshot for %s" % dest.name)
        im = Image.open(raw).convert("RGB")
        im = im.resize((FINAL_W, round(im.height * FINAL_W / im.width)), Image.LANCZOS)
        im.save(dest, "WEBP", quality=82, method=6)
        return im.size, dest.stat().st_size
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, step, caption in FRAMES:
        dest = OUT / ("%s.webp" % name)
        (w, h), size = shoot(step, dest)
        print("  %-12s %4dx%-4d %6.1f KB   %s" % (name, w, h, size / 1024, caption))
    return 0


if __name__ == "__main__":
    sys.exit(main())
