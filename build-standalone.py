# Builds a dependency-free, single-file AOO Creator that runs on file:// (double-click).
#
# This is the download artifact. Its sibling build-web.py produces web/ for hosting.
# Both read source/, which is the only source of truth.
#
#     python build-standalone.py                 # source/ -> AOO-Creator-v<VERSION>-standalone.html
#     python build-standalone.py SRC OUT         # explicit paths
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source"
if len(sys.argv) > 2:
    OUT = pathlib.Path(sys.argv[2])
else:
    OUT = ROOT / ("AOO-Creator-v%s-standalone.html" % (SRC / "VERSION").read_text(encoding="utf-8").strip())

html  = (SRC / "index.html").read_text(encoding="utf-8")
css   = (SRC / "styles.css").read_text(encoding="utf-8")
core  = (SRC / "core.js").read_text(encoding="utf-8")
app   = (SRC / "app.js").read_text(encoding="utf-8")
logo  = base64.b64encode((SRC / "assets" / "aoo-logo.png").read_bytes()).decode("ascii")

# --- embed the WOFF2 faces: the whole point of the standalone is that it opens
# from a desktop with no server, so a font referenced by path would simply not
# load. base64 costs 33% over the wire but there is no wire here. ---
n_fonts = 0
for woff in sorted((SRC / "assets" / "fonts").glob("*.woff2")):
    ref = "url('assets/fonts/%s')" % woff.name
    if ref not in css:
        sys.exit("FAIL: %s is on disk but no @font-face references it" % woff.name)
    data = base64.b64encode(woff.read_bytes()).decode("ascii")
    css = css.replace(ref, "url(data:font/woff2;base64,%s)" % data)
    n_fonts += 1
# test for an unresolved url(), not for the bare path text: the licence
# attribution comment legitimately names assets/fonts/OFL-*.txt
if re.search(r"url\([^)]*assets/fonts/", css):
    sys.exit("FAIL: a font url() survived embedding")

# --- de-module core.js: strip the `export ` keyword only in declaration position ---
core_n, n_core = re.subn(r'(?m)^export\s+(?=(const|let|var|function|class|async)\b)', '', core)
if re.search(r'(?m)^\s*export\b', core_n):
    sys.exit("FAIL: unhandled export form left in core.js")

# --- de-module app.js: drop the import line ---
app_n, n_imp = re.subn(r'(?m)^import\s*\{[^}]*\}\s*from\s*["\']\./core\.js["\'];?\s*\n', '', app)
if n_imp != 1:
    sys.exit(f"FAIL: expected exactly 1 import in app.js, removed {n_imp}")
if re.search(r'(?m)^\s*(import|export)\b', app_n):
    sys.exit("FAIL: unhandled import/export left in app.js")

# --- file:// hardening: storage may be denied, randomUUID may be absent ---
for name in ("core", "app"):
    pass
core_n = core_n.replace("crypto.randomUUID()", "aooUUID()")
app_n  = app_n.replace("crypto.randomUUID()", "aooUUID()")
# Top-level names from core.js and app.js share one scope once concatenated.
# Two ES modules tolerate a duplicate; this file does not - it is a fatal
# redeclaration that stops the app booting, and it only appears here. That
# happened once with countWords, so it is checked rather than remembered.
core_names = set(re.findall(r'(?m)^(?:export\s+)?(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', core_n))
app_names = set(re.findall(r'(?m)^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)', app_n))
clash = sorted(core_names & app_names)
if clash:
    sys.exit('FAIL: core.js and app.js both declare %s at top level; one scope '
             'in the standalone means this will not boot' % ', '.join(clash))

n_ls = len(re.findall(r'\blocalStorage\.', app_n))
app_n = re.sub(r'\blocalStorage\.', 'AOOStore.', app_n)
if n_ls < 6:
    sys.exit(f"FAIL: expected at least 6 localStorage uses, found {n_ls}")

PRELUDE = '''/* --- single-file shims: keep the app alive on file:// --- */
var AOOStorePersistent = false;
var AOOStore = (function () {
  var mem = {}, ok = false;
  try { var k = "__aoo_probe__"; localStorage.setItem(k, "1"); localStorage.removeItem(k); ok = true; } catch (e) { ok = false; }
  AOOStorePersistent = ok;
  return ok ? localStorage : {
    getItem: function (k) { return Object.prototype.hasOwnProperty.call(mem, k) ? mem[k] : null; },
    setItem: function (k, v) { mem[k] = String(v); },
    removeItem: function (k) { delete mem[k]; }
  };
})();
function aooUUID() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
  var b = new Uint8Array(16);
  if (typeof crypto !== "undefined" && crypto.getRandomValues) crypto.getRandomValues(b);
  else for (var i = 0; i < 16; i++) b[i] = Math.floor(Math.random() * 256);
  b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
  var h = []; for (var j = 0; j < 16; j++) h.push((b[j] + 0x100).toString(16).slice(1));
  return h.slice(0,4).join("")+"-"+h.slice(4,6).join("")+"-"+h.slice(6,8).join("")+"-"+h.slice(8,10).join("")+"-"+h.slice(10,16).join("");
}
if (typeof structuredClone !== "function") {
  var structuredClone = function (v) { return JSON.parse(JSON.stringify(v)); };
}
'''

bundle = "(function(){\n\"use strict\";\n" + PRELUDE + "\n/* ===== core.js ===== */\n" + core_n + "\n/* ===== app.js ===== */\n" + app_n + "\n})();\n"

for frag, label in ((css, "css"), (bundle, "js")):
    if "</script" in frag.lower() or "</style" in frag.lower():
        sys.exit(f"FAIL: {label} contains a tag-closing sequence unsafe to inline")

# --- rewrite index.html: inline stylesheet, logo, script ---
html_n, n1 = re.subn(r'<link rel="stylesheet" href="styles\.css">',
                     lambda m: "<style>\n" + css + "\n</style>", html, count=1)
# the logo is declared once as a CSS custom property and referenced from there,
# so the base64 is embedded a single time however many places display it
html_n, n2 = re.subn(r'url\("assets/aoo-logo\.png"\)',
                     lambda m: 'url("data:image/png;base64,' + logo + '")', html_n)
html_n, n3 = re.subn(r'<script type="module" src="app\.js"></script>',
                     lambda m: "<script>\n" + bundle + "</script>", html_n, count=1)
if n1 != 1 or n2 < 1 or n3 != 1:
    sys.exit(f"FAIL: html rewrite counts were {(n1, n2, n3)}; expected 1 stylesheet, >=1 logo, 1 script")

# fonts are tested as url() rather than bare text: the OFL attribution comment
# legitimately names assets/fonts/OFL-*.txt inside the inlined stylesheet
if ("styles.css" in html_n or 'src="app.js"' in html_n
        or "assets/aoo-logo.png" in html_n
        or re.search(r"url\([^)]*assets/fonts/", html_n)):
    sys.exit("FAIL: an external reference survived inlining")

OUT.write_text(html_n, encoding="utf-8")
print(f"OK  exports stripped: {n_core}  localStorage rewired: {n_ls}  fonts embedded: {n_fonts}")
print(f"OK  wrote {OUT}  ({OUT.stat().st_size:,} bytes)")
