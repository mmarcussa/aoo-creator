"""A control study: the current buttons beside three treatments that actually decide something.

Same AOO palette throughout, so the only variable is the treatment.

    python build-buttons.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

ROW = """
<div class="row">
  <button class="primary">Validate &amp; build ZIP</button>
  <button class="secondary">Save project</button>
  <button class="ghost">Tutorial</button>
  <button class="danger">Delete</button>
  <button class="danger-strong">Delete collection</button>
  <button class="icon-button">+</button>
  <span class="chip">Not saved to a file</span>
</div>
<div class="row tabs">
  <button class="tab active">Write <span class="badge">3</span></button>
  <button class="tab">Details</button>
  <button class="tab">Comments <span class="badge">4</span></button>
</div>
<div class="row nav">
  <button class="nav-item active"><span>An Omelet of Passion II</span><small>3 ch</small></button>
  <button class="nav-item"><span>Delamain Takes the Long Way</span><small>1 ch</small></button>
</div>
"""

BASE = """
:root{--bg:#090d10;--panel:#111a1f;--panel2:#182228;--line:#26454b;--text:#dce9e7;--muted:#8ba3a1;
--cyan:#31d5d6;--yellow:#f0c94a;--red:#ef5867;--green:#38d28d}
*{box-sizing:border-box}
body{margin:0;padding:2rem 2.5rem;background:var(--bg);color:var(--text);font:15px/1.45 "Segoe UI",sans-serif}
h1{font-size:1.1rem;margin:0 0 1.6rem;color:var(--yellow);letter-spacing:.02em}
h2{font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;color:var(--red);margin:2rem 0 .3rem}
h2 em{font-style:normal;color:var(--muted);letter-spacing:.02em;text-transform:none;font-weight:400;font-size:.8rem;margin-left:.6rem}
.row{display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;padding:.9rem 0}
.row.nav{max-width:300px;display:grid;gap:.3rem}
button{font:inherit;color:inherit;cursor:pointer}
.badge{display:inline-flex;min-width:1.3rem;height:1.3rem;align-items:center;justify-content:center;padding:0 .3rem;font-size:.68rem;font-weight:700}
.nav-item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.4rem;text-align:left}
.nav-item span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nav-item small{color:var(--muted);font-weight:400;font-size:.72rem}
.chip{display:inline-flex;align-items:center;gap:.35rem;font-size:.68rem;font-weight:700}
.chip::before{content:"";width:.5rem;height:.5rem;border-radius:50%;background:var(--yellow)}
"""

# ---------------------------------------------------------------- 0. what ships today
CURRENT = """
button{border:1px solid var(--line);background:var(--panel2);padding:.55rem .85rem;border-radius:4px;font-weight:600;font-size:.84rem}
.primary{border-color:var(--yellow);background:linear-gradient(180deg,#f0c94a26,#f0c94a0d);color:var(--yellow);font-weight:800}
.secondary{border-color:#7b8f8d;color:var(--text);font-weight:700;background:var(--panel2)}
.ghost{background:transparent}
.danger{border-color:#8a3a44;background:transparent;color:var(--red)}
.danger-strong{background:#ef58672a;border-color:var(--red);color:var(--red);font-weight:800}
.icon-button{width:2rem;height:2rem;padding:0}
.chip{padding:.22rem .6rem;border:1px solid var(--yellow);border-radius:99px;color:var(--yellow);background:#f0c94a1a}
.tab{border-bottom:0;border-radius:5px 5px 0 0;background:transparent;color:var(--muted)}
.tab.active{color:var(--yellow);background:var(--panel2);border-color:var(--line);box-shadow:inset 0 2px 0 var(--yellow)}
.badge{background:#31d5d61f;color:var(--cyan);border-radius:99px}
.nav-item{padding:.46rem .55rem;background:transparent;border-color:transparent}
.nav-item.active{background:linear-gradient(90deg,#f0c94a29,#f0c94a08);border-color:transparent;box-shadow:inset 3px 0 0 var(--yellow)}
"""

# ---------------------------------------------------------------- 1. quiet: borders earn their place
QUIET = """
button{border:1px solid transparent;background:transparent;padding:.5rem .8rem;border-radius:3px;font-weight:600;font-size:.83rem;color:var(--muted)}
button:hover{color:var(--text);background:var(--panel2)}
.primary{background:var(--yellow);color:#0b1114;font-weight:700}
.secondary{background:var(--panel2);border-color:var(--line);color:var(--text)}
.ghost{color:var(--muted)}
.danger{color:var(--red)}
.danger-strong{background:var(--red);color:#1a0c0f;font-weight:700}
.icon-button{width:1.9rem;height:1.9rem;padding:0;color:var(--muted)}
.chip{padding:.22rem .5rem;border-radius:3px;color:var(--yellow);background:#f0c94a17}
.tab{border-radius:3px 3px 0 0;color:var(--muted);padding:.5rem .75rem}
.tab.active{color:var(--text);background:var(--panel2);box-shadow:inset 0 -2px 0 var(--yellow)}
.badge{background:transparent;border:1px solid var(--line);color:var(--muted);border-radius:3px}
.nav-item{padding:.44rem .5rem;color:var(--text);font-weight:400}
.nav-item.active{background:var(--panel2);box-shadow:inset 2px 0 0 var(--yellow);font-weight:600}
"""

# ---------------------------------------------------------------- 2. cut: a shape language
CUT = """
:root{--cut:polygon(0 0,calc(100% - 9px) 0,100% 9px,100% 100%,9px 100%,0 calc(100% - 9px))}
button{border:1px solid var(--line);background:var(--panel2);padding:.52rem .9rem;font-weight:700;font-size:.8rem;letter-spacing:.05em;clip-path:var(--cut)}
button:hover{border-color:var(--cyan);color:var(--cyan)}
.primary{background:var(--yellow);border-color:var(--yellow);color:#0b1114;font-weight:800}
.secondary{border-color:var(--text);color:var(--text)}
.ghost{background:transparent;color:var(--muted)}
.danger{background:transparent;border-color:#8a3a44;color:var(--red)}
.danger-strong{background:var(--red);border-color:var(--red);color:#1a0c0f;font-weight:800}
.icon-button{width:2rem;height:2rem;padding:0;clip-path:none}
.chip{padding:.24rem .6rem;border:1px solid var(--yellow);color:var(--yellow);background:#f0c94a14;clip-path:var(--cut)}
.tab{clip-path:polygon(0 0,calc(100% - 9px) 0,100% 9px,100% 100%,0 100%);background:transparent;color:var(--muted);border-bottom:0}
.tab.active{color:#0b1114;background:var(--yellow);border-color:var(--yellow)}
.badge{background:#0b111433;color:inherit;clip-path:none;border-radius:2px}
.tab.active .badge{background:#0b111433;color:#0b1114}
.nav-item{padding:.44rem .5rem;background:transparent;border-color:transparent;clip-path:none;letter-spacing:0;font-weight:500}
.nav-item.active{background:#f0c94a14;box-shadow:inset 3px 0 0 var(--yellow)}
"""

# ---------------------------------------------------------------- 3. instrument: squared, ruled
INSTRUMENT = """
button{border:1px solid var(--line);background:linear-gradient(180deg,var(--panel2),#101a1e);padding:.5rem .85rem;border-radius:0;font-weight:700;font-size:.82rem;box-shadow:inset 0 1px 0 #ffffff0d}
button:hover{border-color:var(--cyan)}
.primary{border-color:var(--yellow);color:var(--yellow);box-shadow:inset 0 -2px 0 var(--yellow),inset 0 1px 0 #ffffff0d}
.secondary{color:var(--text);box-shadow:inset 0 -2px 0 var(--line),inset 0 1px 0 #ffffff0d}
.ghost{background:transparent;color:var(--muted);box-shadow:none;border-color:transparent}
.ghost:hover{border-color:var(--line)}
.danger{background:transparent;border-color:#8a3a44;color:var(--red);box-shadow:none}
.danger-strong{border-color:var(--red);color:var(--red);box-shadow:inset 0 -2px 0 var(--red),inset 0 1px 0 #ffffff0d}
.icon-button{width:2rem;height:2rem;padding:0}
.chip{padding:.24rem .55rem;border:1px solid var(--yellow);color:var(--yellow);background:#f0c94a12}
.tab{background:transparent;color:var(--muted);border:0;border-bottom:2px solid transparent;padding:.55rem .8rem;box-shadow:none}
.tab.active{color:var(--yellow);border-bottom-color:var(--yellow)}
.badge{background:#31d5d61a;color:var(--cyan);border-radius:0}
.nav-item{padding:.44rem .5rem;background:transparent;border-color:transparent;box-shadow:none;font-weight:500}
.nav-item.active{background:#f0c94a10;box-shadow:inset 3px 0 0 var(--yellow)}
"""

SECTIONS = [
    ("Current", "flat rectangle, 1px border, 4px radius — the default", CURRENT),
    ("1 · Quiet", "borders only where they mean something, solid primary", QUIET),
    ("2 · Cut", "a committed shape language, solid primary", CUT),
    ("3 · Instrument", "squared, ruled underlines, panel gradients", INSTRUMENT),
]

parts = ['<!doctype html><meta charset="utf-8"><title>Button study</title><style>' + BASE]
for i, (name, _, css) in enumerate(SECTIONS):
    parts.append("".join(".s%d %s" % (i, line) if line.strip() and not line.startswith(("--", ":root"))
                         else line for line in css.strip().splitlines(True)))
parts.append(":root{--cut:polygon(0 0,calc(100% - 9px) 0,100% 9px,100% 100%,9px 100%,0 calc(100% - 9px))}")
parts.append("</style><h1>AOO Creator — control study</h1>")
for i, (name, note, _) in enumerate(SECTIONS):
    parts.append('<h2>%s<em>%s</em></h2><div class="s%d">%s</div>' % (name, note, i, ROW))
HERE.joinpath("buttons.html").write_text("".join(parts), encoding="utf-8")
print("wrote buttons.html")
