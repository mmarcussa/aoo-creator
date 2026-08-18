"""Generate three static mockups of the AOO Creator Write screen.

Same markup skeleton and the same class names the real tool uses, so whichever
direction wins, its CSS lifts straight into source/styles.css. Fonts are system
only - the standalone build cannot fetch anything.

    python build-mockups.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

BODY = """
<header class="app-header">
  <div class="brand">
    <img class="brand-logo" src="../source/assets/aoo-logo.png" alt="" width="44" height="44">
    <div><strong>AOO Creator</strong><span>Framework pack builder &middot; v0.2.0</span></div>
  </div>
  <div class="header-actions">
    <label class="compact">Theme <select><option>AOO</option></select></label>
    <button class="ghost">Tutorial</button>
    <button class="ghost">Import project</button>
    <button class="ghost">Save project</button>
    <button class="primary">Validate &amp; build ZIP</button>
  </div>
</header>

<div class="status-bar">Autosaved locally.</div>

<main class="workspace">
  <aside class="rail">
    <section class="rail-section">
      <div class="section-title"><h2>Collection</h2><button class="icon-button">&#9881;</button></div>
      <select class="collection-select"><option>Afterlife One-Shots</option></select>
      <div class="project-summary"><span>3 authors &middot; 7 works &middot; v1.2.0</span></div>
      <div class="collection-actions"><button class="ghost">New</button><button class="danger">Delete</button></div>
    </section>
    <section class="rail-section">
      <div class="section-title"><h2>Authors</h2><button class="icon-button">&#9776;</button></div>
      <div class="author-summary"><strong>3 authors</strong><span>1 active &middot; 2 inactive &middot; manage</span></div>
    </section>
    <section class="rail-section grow">
      <div class="section-title"><h2>Works</h2><button class="icon-button">+</button></div>
      <input class="rail-search" type="search" placeholder="Find a title or author">
      <div class="nav-list">
        <button class="nav-item active"><span>An Omelet of Passion II</span><small>3 ch</small></button>
        <button class="nav-item"><span>Delamain Takes the Long Way</span><small>1 ch</small></button>
        <button class="nav-item"><span>ICE Queen</span><small>5 ch</small></button>
        <button class="nav-item"><span>Notes From a Braindance Editor</span><small>2 ch</small></button>
      </div>
    </section>
  </aside>

  <section class="editor-shell">
    <nav class="editor-tabs">
      <button class="active">Write <span class="badge">3</span></button>
      <button>Details</button>
      <button>Comments <span class="badge">4</span></button>
      <button>AOO preview</button>
      <button>Validation <span class="badge">0</span></button>
    </nav>

    <div class="pane active">
      <div class="pane-heading">
        <div><span class="eyebrow">Manuscript</span><h1>An Omelet of Passion II: Reheated</h1></div>
        <div class="pane-actions"><button class="primary">Add chapter</button></div>
      </div>
      <div class="write-layout">
        <aside class="chapter-strip">
          <div class="strip-head">Chapters</div>
          <div class="strip-list">
            <button class="strip-item"><span class="strip-num">1</span><span class="strip-name">Reheated</span><small>1420w</small></button>
            <button class="strip-item active"><span class="strip-num">2</span><span class="strip-name">Second Serving</span><small>980w</small></button>
            <button class="strip-item"><span class="strip-num">3</span><span class="strip-name">Cold Open</span><small>0w</small></button>
          </div>
        </aside>
        <div class="chapter-editor">
          <div class="editor-bar">
            <label class="grow">Chapter title<input value="Second Serving"></label>
            <label class="tight">Price (&euro;$)<input value="450"></label>
            <div class="card-actions"><button>&uarr;</button><button>&darr;</button><button class="danger">Delete</button></div>
          </div>
          <div class="manuscript">She found the shard in a noodle bar booth, still warm. Three chapters of somebody else&rsquo;s handwriting, and every one of them addressed to her.<br><br>Choom, she typed back, you have the wrong merc.<br><br>The reply came before she finished her bowl.</div>
          <div class="editor-foot"><span>980 words</span><span>Chapter 2 of 3</span></div>
          <details class="notes"><summary>Author&rsquo;s notes (optional)</summary></details>
        </div>
      </div>
    </div>
  </section>
</main>
"""

BASE = """
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--text);overflow:hidden}
button,input,select{font:inherit;color:inherit}
button{cursor:pointer}
.workspace{height:calc(100vh - 100px);display:grid;grid-template-columns:280px minmax(0,1fr)}
.rail{display:flex;flex-direction:column;min-height:0;padding:.8rem}
.rail-section.grow{display:flex;min-height:0;flex:1;flex-direction:column}
.section-title{display:flex;align-items:center;justify-content:space-between;margin-bottom:.5rem}
.section-title h2{margin:0}
.nav-list{display:grid;gap:.28rem;overflow:auto}
.nav-item{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.4rem;text-align:left}
.nav-item span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.brand{display:flex;align-items:center;gap:.7rem}
.brand div{display:grid}
.header-actions{display:flex;align-items:center;gap:.55rem}
.compact{display:flex;align-items:center;gap:.45rem}
.app-header{display:flex;align-items:center;justify-content:space-between;padding:0 1rem;height:72px}
.status-bar{height:28px;padding:.3rem 1rem}
.editor-shell{min-width:0;min-height:0;overflow:hidden}
.editor-tabs{height:54px;display:flex;gap:.25rem;padding:.55rem 1.2rem 0}
.pane{height:calc(100% - 54px);overflow:hidden;padding:1.4rem 2rem 2rem;display:flex;flex-direction:column}
.pane-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:1.25rem}
.pane-heading h1{margin:.15rem 0 0}
.write-layout{flex:1;min-height:0;display:grid;grid-template-columns:210px minmax(0,1fr);gap:1rem}
.chapter-strip{display:flex;flex-direction:column;min-height:0}
.strip-list{overflow:auto;padding:.4rem;display:grid;gap:.25rem;align-content:start}
.strip-item{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:.45rem;text-align:left}
.strip-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chapter-editor{display:flex;flex-direction:column;min-height:0;gap:.6rem}
.editor-bar{display:flex;align-items:flex-end;gap:.6rem}
.editor-bar label{display:grid;gap:.28rem}
.editor-bar label.grow{flex:1}
.editor-bar label.tight{width:8.5rem}
.editor-bar input{width:100%}
.card-actions{display:flex;gap:.35rem}
.manuscript{flex:1;min-height:0;overflow:auto}
.editor-foot{display:flex;justify-content:space-between}
.rail-search{width:100%}
.collection-select{width:100%}
.collection-actions{display:grid;grid-template-columns:1fr 1fr;gap:.35rem;margin-top:.5rem}
.project-summary,.author-summary{display:grid;gap:.2rem}
.badge{display:inline-flex;min-width:1.4rem;height:1.4rem;align-items:center;justify-content:center;padding:0 .35rem}
"""

# ---------------------------------------------------------------- A. terminal
A = """
:root{--bg:#07090b;--panel:#0d1216;--panel2:#131b20;--line:#1f3a40;--text:#d8e6e4;--muted:#7d9694;
--cyan:#2ee6e6;--yellow:#ffd23f;--red:#ff4d61;--green:#3ddb92;
--display:"Bahnschrift","DIN Alternate","Segoe UI",sans-serif;--mono:Consolas,"Cascadia Mono",monospace;
--cut:polygon(0 0,calc(100% - 10px) 0,100% 10px,100% 100%,10px 100%,0 calc(100% - 10px))}
body{font:15px/1.45 "Segoe UI",sans-serif;
background:repeating-linear-gradient(0deg,#0000 0 3px,#ffffff05 3px 4px),var(--bg)}
h1,h2,.brand strong,.editor-tabs button,button,.eyebrow,.strip-head,.section-title h2{font-family:var(--display);letter-spacing:.08em;text-transform:uppercase}
button{border:1px solid var(--line);background:var(--panel2);padding:.55rem .85rem;font-weight:600;font-size:.8rem;clip-path:var(--cut)}
button:hover{border-color:var(--cyan);color:var(--cyan)}
.primary{border-color:var(--yellow);background:linear-gradient(180deg,#ffd23f22,#ffd23f0a);color:var(--yellow)}
.danger{border-color:var(--red);background:transparent;color:var(--red)}
.ghost{background:transparent}
.icon-button{width:2rem;height:2rem;padding:0;clip-path:none;border-radius:2px}
input,select{border:1px solid var(--line);background:#0a0f12;padding:.5rem .6rem;clip-path:var(--cut)}
.app-header{border-bottom:1px solid var(--line);background:linear-gradient(180deg,var(--panel),#0a0e11)}
.brand-logo{width:44px;height:44px;object-fit:contain}
.brand strong{font-size:1.05rem;color:var(--yellow)}
.brand span{font-size:.68rem;color:var(--muted);text-transform:none;letter-spacing:.04em;font-family:var(--mono)}
.status-bar{background:#0a1417;border-bottom:1px solid var(--line);font:.72rem/1.5 var(--mono);color:var(--cyan)}
.rail{background:var(--panel);border-right:1px solid var(--line)}
.rail-section{padding:.7rem 0;border-bottom:1px solid var(--line)}
.section-title h2{font-size:.68rem;color:var(--red);letter-spacing:.18em}
.project-summary span,.author-summary span{font:.7rem var(--mono);color:var(--muted)}
.author-summary strong{font-family:var(--display);letter-spacing:.06em}
.collection-select{color:var(--yellow);font-weight:700}
.nav-item{padding:.45rem .5rem;background:transparent;border-color:transparent;text-transform:none;letter-spacing:0;font-family:"Segoe UI",sans-serif}
.nav-item:hover{border-color:var(--line);background:var(--panel2)}
.nav-item.active{border-color:var(--yellow);background:#ffd23f14;color:var(--text)}
.nav-item small{font-family:var(--mono);color:var(--muted);font-size:.68rem}
.editor-tabs{border-bottom:1px solid var(--line);background:var(--panel)}
.editor-tabs button{background:transparent;border-bottom:0;color:var(--muted);clip-path:polygon(0 0,calc(100% - 9px) 0,100% 9px,100% 100%,0 100%)}
.editor-tabs button.active{color:var(--yellow);background:var(--panel2);border-color:var(--line);box-shadow:inset 0 2px 0 var(--yellow)}
.badge{background:#2ee6e61f;color:var(--cyan);font:700 .66rem var(--mono);clip-path:none;border-radius:2px}
.eyebrow{font-size:.66rem;color:var(--red);letter-spacing:.2em;font-weight:700}
.pane-heading h1{font-size:1.5rem;color:var(--text);letter-spacing:.04em}
.chapter-strip{background:var(--panel);border:1px solid var(--line);clip-path:var(--cut)}
.strip-head{padding:.5rem .7rem;border-bottom:1px solid var(--line);font-size:.64rem;color:var(--red);letter-spacing:.2em}
.strip-item{padding:.42rem .5rem;background:transparent;border-color:transparent;clip-path:none;text-transform:none;letter-spacing:0;font-family:"Segoe UI",sans-serif}
.strip-item.active{border-color:var(--yellow);background:#ffd23f14}
.strip-num{width:1.3rem;height:1.3rem;display:grid;place-items:center;background:#2ee6e61f;color:var(--cyan);font:700 .66rem var(--mono)}
.strip-item small{font:.64rem var(--mono);color:var(--muted)}
.editor-bar label{font-size:.64rem;color:var(--muted);font-family:var(--display);letter-spacing:.14em;text-transform:uppercase}
.manuscript{padding:1.3rem 1.5rem;background:#0b1013;border:1px solid var(--line);clip-path:var(--cut);font:1rem/1.8 Georgia,serif;color:#cfdedc}
.editor-foot{font:.7rem var(--mono);color:var(--muted)}
.notes{border:1px solid var(--line);background:var(--panel);clip-path:var(--cut)}
.notes summary{padding:.5rem .8rem;font:.66rem var(--display);letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);cursor:pointer}
.compact{font-size:.72rem;color:var(--muted)}
"""

# ---------------------------------------------------------------- B. archive
B = """
:root{--bg:#12100f;--panel:#1a1715;--panel2:#221e1b;--line:#3a322d;--text:#eee7df;--muted:#a2968a;
--cyan:#5fb8c4;--yellow:#e8b64c;--red:#c25a52;--serif:Georgia,"Iowan Old Style",serif}
body{font:15px/1.5 "Segoe UI",sans-serif;background:var(--bg)}
button{border:1px solid var(--line);background:var(--panel2);padding:.5rem .8rem;border-radius:2px;font-size:.83rem}
button:hover{border-color:var(--muted)}
.primary{background:var(--yellow);border-color:var(--yellow);color:#231d10;font-weight:700}
.danger{background:transparent;border-color:#5a3630;color:var(--red)}
.ghost{background:transparent}
.icon-button{width:1.9rem;height:1.9rem;padding:0}
input,select{border:1px solid var(--line);background:#171412;padding:.5rem .6rem;border-radius:2px}
.app-header{border-bottom:2px solid var(--line);background:var(--panel)}
.brand-logo{width:44px;height:44px;object-fit:contain}
.brand strong{font:700 1.2rem var(--serif);color:var(--text)}
.brand span{font-size:.72rem;color:var(--muted)}
.status-bar{background:#171412;border-bottom:1px solid var(--line);font-size:.74rem;color:var(--muted)}
.rail{background:var(--panel);border-right:1px solid var(--line)}
.rail-section{padding:.75rem 0;border-bottom:1px solid var(--line)}
.section-title h2{font:700 .7rem "Segoe UI";text-transform:uppercase;letter-spacing:.16em;color:var(--muted)}
.collection-select{font:700 .95rem var(--serif);color:var(--text)}
.project-summary span,.author-summary span{font-size:.74rem;color:var(--muted)}
.author-summary strong{font:600 .95rem var(--serif)}
.nav-item{padding:.42rem .5rem;background:transparent;border-color:transparent;border-left:2px solid transparent;border-radius:0}
.nav-item:hover{background:var(--panel2)}
.nav-item.active{border-left-color:var(--yellow);background:var(--panel2);color:var(--text)}
.nav-item span{font-family:var(--serif);font-size:.92rem}
.nav-item small{font-size:.7rem;color:var(--muted)}
.editor-tabs{border-bottom:1px solid var(--line);background:var(--panel);align-items:flex-end;gap:1.4rem;padding:0 2rem}
.editor-tabs button{background:transparent;border:0;border-bottom:2px solid transparent;border-radius:0;padding:.5rem .1rem 0.7rem;color:var(--muted);font-size:.86rem}
.editor-tabs button.active{color:var(--text);border-bottom-color:var(--yellow);font-weight:700}
.badge{background:transparent;border:1px solid var(--line);color:var(--muted);font-size:.68rem;border-radius:99px}
.eyebrow{font-size:.68rem;text-transform:uppercase;letter-spacing:.18em;color:var(--muted);font-weight:700}
.pane-heading h1{font:400 1.85rem/1.2 var(--serif);color:var(--text)}
.pane-heading{border-bottom:1px solid var(--line);padding-bottom:1rem}
.chapter-strip{background:transparent;border-right:1px solid var(--line);padding-right:.5rem}
.strip-head{padding:.4rem .2rem .5rem;font:700 .68rem "Segoe UI";text-transform:uppercase;letter-spacing:.16em;color:var(--muted);border-bottom:1px solid var(--line)}
.strip-item{padding:.45rem .3rem;background:transparent;border:0;border-left:2px solid transparent;border-radius:0}
.strip-item.active{border-left-color:var(--yellow);background:var(--panel2)}
.strip-name{font-family:var(--serif);font-size:.9rem}
.strip-num{width:1.25rem;height:1.25rem;display:grid;place-items:center;border:1px solid var(--line);color:var(--muted);font-size:.66rem;border-radius:50%}
.strip-item small{font-size:.66rem;color:var(--muted)}
.editor-bar label{font:700 .68rem "Segoe UI";text-transform:uppercase;letter-spacing:.14em;color:var(--muted)}
.manuscript{padding:1.8rem 2.2rem;background:#191614;border:1px solid var(--line);border-radius:2px;font:1.05rem/1.85 var(--serif);color:#e4dcd2;max-width:64ch}
.editor-foot{font-size:.74rem;color:var(--muted);max-width:64ch}
.notes{border:1px solid var(--line);background:var(--panel);border-radius:2px;max-width:64ch}
.notes summary{padding:.5rem .8rem;font-size:.8rem;color:var(--cyan);cursor:pointer}
.compact{font-size:.74rem;color:var(--muted)}
"""

# ---------------------------------------------------------------- C. sharpened
C = """
:root{--bg:#090d10;--panel:#111a1f;--panel2:#182228;--line:#26454b;--text:#dce9e7;--muted:#8ba3a1;
--cyan:#31d5d6;--yellow:#f0c94a;--red:#ef5867;--green:#38d28d}
body{font:15px/1.45 "Segoe UI",sans-serif;background:radial-gradient(1200px 500px at 70% -10%,#12343044,transparent),var(--bg)}
button{border:1px solid var(--line);background:var(--panel2);padding:.55rem .85rem;border-radius:4px;font-weight:600;font-size:.84rem}
button:hover{border-color:var(--cyan);color:var(--cyan)}
.primary{border-color:var(--yellow);background:linear-gradient(180deg,#f0c94a26,#f0c94a0d);color:var(--yellow);font-weight:800}
.danger{border-color:#5c2730;background:transparent;color:var(--red)}
.ghost{background:transparent}
.icon-button{width:2rem;height:2rem;padding:0}
input,select{border:1px solid var(--line);background:#0d1519;padding:.5rem .6rem;border-radius:4px}
.app-header{border-bottom:1px solid var(--line);background:linear-gradient(180deg,#16222899,#0c1417);box-shadow:0 10px 30px #0006}
.brand-logo{width:44px;height:44px;object-fit:contain}
.brand strong{font-size:1.12rem;color:var(--yellow);letter-spacing:.01em}
.brand span{font-size:.72rem;color:var(--muted)}
.status-bar{background:#0e1b1f;border-bottom:1px solid var(--line);font-size:.75rem;color:var(--muted)}
.rail{background:var(--panel);border-right:1px solid var(--line)}
.rail-section{padding:.7rem 0;border-bottom:1px solid var(--line)}
.section-title h2{font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.16em;color:var(--red);margin:0}
.collection-select{color:var(--yellow);font-weight:700}
.project-summary span,.author-summary span{font-size:.74rem;color:var(--muted)}
.author-summary strong{font-weight:700}
.nav-item{padding:.46rem .55rem;background:transparent;border-color:transparent}
.nav-item:hover{background:var(--panel2);border-color:var(--line)}
.nav-item.active{background:linear-gradient(90deg,#f0c94a1f,#f0c94a08);border-color:var(--yellow);color:var(--text);font-weight:600}
.nav-item small{font-size:.7rem;color:var(--muted);font-weight:400}
.editor-tabs{border-bottom:1px solid var(--line);background:var(--panel)}
.editor-tabs button{background:transparent;border-bottom:0;border-radius:5px 5px 0 0;color:var(--muted)}
.editor-tabs button.active{color:var(--yellow);background:var(--panel2);border-color:var(--line);box-shadow:inset 0 2px 0 var(--yellow)}
.badge{background:#31d5d61f;color:var(--cyan);font-size:.68rem;font-weight:700;border-radius:99px}
.eyebrow{font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.16em;color:var(--red)}
.pane-heading h1{font-size:1.6rem;font-weight:700}
.chapter-strip{background:var(--panel);border:1px solid var(--line);border-radius:6px;box-shadow:0 12px 30px #0005}
.strip-head{padding:.5rem .7rem;border-bottom:1px solid var(--line);font-size:.66rem;font-weight:800;text-transform:uppercase;letter-spacing:.16em;color:var(--red)}
.strip-item{padding:.45rem .5rem;background:transparent;border-color:transparent}
.strip-item.active{background:linear-gradient(90deg,#f0c94a1f,#f0c94a08);border-color:var(--yellow)}
.strip-num{width:1.3rem;height:1.3rem;display:grid;place-items:center;background:#31d5d61f;color:var(--cyan);font-size:.68rem;font-weight:800;border-radius:4px}
.strip-item small{font-size:.68rem;color:var(--muted)}
.editor-bar label{font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:var(--muted)}
.manuscript{padding:1.5rem 1.8rem;background:var(--panel);border:1px solid var(--line);border-radius:6px;font:1.02rem/1.8 Georgia,serif;color:#d5e3e1;box-shadow:inset 0 1px 0 #ffffff08}
.editor-foot{font-size:.74rem;color:var(--muted)}
.notes{border:1px solid var(--line);background:var(--panel);border-radius:6px}
.notes summary{padding:.55rem .8rem;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--cyan);cursor:pointer}
.compact{font-size:.74rem;color:var(--muted)}
"""

for name, css, title in [("a-terminal", A, "A - In-world terminal"),
                         ("b-archive", B, "B - AO3 in 2077"),
                         ("c-sharpened", C, "C - Sharpened bones")]:
    HERE.joinpath("%s.html" % name).write_text(
        '<!doctype html><meta charset="utf-8"><title>%s</title><style>%s%s</style>%s'
        % (title, BASE, css, BODY), encoding="utf-8")
print("wrote 3 mockups")
