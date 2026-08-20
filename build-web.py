"""Build the hosted version of AOO Creator into docs/.

Two artifacts come out of one source tree:

  build-standalone.py  ->  AOO-Creator-v<VERSION>-standalone.html  (download / offline / Nexus)
  build-web.py         ->  docs/                                   (GitHub Pages, later Cloudflare)

The tool itself is deliberately identical in both. A writer who downloads the
offline file after using the site should get exactly what they just used, so the
hosted copy is not a different product with web fonts and analytics bolted on.
What the hosted build adds is what a URL needs and a file:// page cannot use: a
landing page, link-preview metadata, a favicon, cache headers, and a link to
fetch the offline copy.

The landing page is the one place the two versions diverge, and it can, because
it is not the tool: no bindings, no themes, no export path, no contract. Nothing
a guard tracks can drift there.

    python build-web.py                                  # relative og:image, fine for testing
    python build-web.py --base-url https://your.domain   # absolute, needed for real previews

Layout produced:
    docs/index.html   the landing page
    docs/app.html     the tool
    docs/AOO-Creator-v<VERSION>-standalone.html   the download the landing page offers

Exits non-zero if any reference in either built page does not resolve.
"""
import argparse, html, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"
# docs/ and not web/: GitHub Pages "deploy from a branch" only offers the repo root
# or /docs, so this name works with no Action and no extra machinery. Cloudflare
# Pages lets you point at any directory, so it does not care either way.
OUT = ROOT / "docs"
VERSION = (SRC / "VERSION").read_text(encoding="utf-8").strip()
STANDALONE = f"AOO-Creator-v{VERSION}-standalone.html"

# source name -> name in docs/. The tool moves to app.html so the landing page
# can own the root URL. schema.json is NOT published: nothing links to it and
# it reads as developer scaffolding on a writer's site. It stays in source/.
COPY_AS = {
    "landing.html": "index.html",
    "index.html": "app.html",
    "styles.css": "styles.css",
    "app.js": "app.js",
    "core.js": "core.js",
}
ASSETS = ["aoo-logo.png", "share-card.png", "screenshot-app.png"]

TITLE = "AOO Creator"
DESC = ("Write fic collections for Cyberpunk 2077's Archive of Our Overwrites and export a "
        "Nexus-ready mod. Runs entirely in your browser — no account, nothing uploaded.")


def meta(base):
    img = f"{base}/assets/share-card.png" if base else "assets/share-card.png"
    canonical = f'\n<link rel="canonical" href="{base}/">' if base else ""
    return f"""<meta name="description" content="{html.escape(DESC, quote=True)}">
<link rel="icon" href="assets/aoo-logo.png" type="image/png">
<link rel="apple-touch-icon" href="assets/aoo-logo.png">
<meta name="theme-color" content="#070b0d">
<meta name="color-scheme" content="dark">{canonical}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{TITLE}">
<meta property="og:title" content="{TITLE} — build fic collection mods">
<meta property="og:description" content="{html.escape(DESC, quote=True)}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Archive of Our Overwrites Creator">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE} — build fic collection mods">
<meta name="twitter:description" content="{html.escape(DESC, quote=True)}">
<meta name="twitter:image" content="{img}">
"""


OFFLINE = f"""
      <p class="welcome-offline">Working without a connection, or want to keep a copy?
      <a href="{STANDALONE}" download>Download the single-file version</a> — one HTML file,
      identical to this page, opens straight from your desktop.</p>
"""

OFFLINE_CSS = """
/* hosted build only: pointer to the downloadable single-file copy */
.welcome-offline{margin:.35rem 0 0;font-size:.86rem;line-height:1.55;color:var(--muted)}
.welcome-offline a{color:var(--cyan);text-decoration:underline;text-underline-offset:3px}
.welcome-offline a:hover{color:var(--text)}
"""

# a quiet way back for someone who lands straight on the tool and wants to know
# what it is
HOMELINK_CSS = """
/* hosted build only. It lives in the header, not floating: fixed to the bottom
   left it covered the rail's "Load example" dropdown, which is a control, and a
   decorative back-link must never sit on top of one. */
.site-home{display:inline-flex;align-items:center;padding:.34rem .6rem;
  border:1px solid var(--line);border-radius:2px;background:transparent;
  font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;white-space:nowrap;
  color:var(--muted);text-decoration:none;opacity:.75;transition:opacity 140ms ease}
.site-home:hover{opacity:1;color:var(--cyan);border-color:var(--cyan)}
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  X-Frame-Options: DENY

/assets/*
  Cache-Control: public, max-age=604800

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/*.css
  Cache-Control: public, max-age=86400

/*.js
  Cache-Control: public, max-age=86400

/index.html
  Cache-Control: public, max-age=0, must-revalidate

/app.html
  Cache-Control: public, max-age=0, must-revalidate
"""


def once(text, old, new, what):
    if text.count(old) != 1:
        sys.exit(f"FAIL: {what}: {text.count(old)} matches for {old[:70]!r}")
    return text.replace(old, new)


def refs_of(page):
    return set(re.findall(r'(?:href|src)="([^"#:]+?)"', page))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="", help="site origin, e.g. https://aoo.example")
    base = ap.parse_args().base_url.rstrip("/")

    src_standalone = ROOT / STANDALONE
    if not src_standalone.exists():
        sys.exit(f"FAIL: {STANDALONE} not found; run build-standalone.py first")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    for src_name, out_name in COPY_AS.items():
        shutil.copy2(SRC / src_name, OUT / out_name)
    for name in ASSETS:
        shutil.copy2(SRC / "assets" / name, OUT / "assets" / name)
    # fonts stay real files here: the browser caches them and fetches them in
    # parallel, where the standalone has to carry them base64 inside one file
    (OUT / "assets" / "fonts").mkdir()
    for woff in sorted((SRC / "assets" / "fonts").glob("*.woff2")):
        shutil.copy2(woff, OUT / "assets" / "fonts" / woff.name)
    # the in-game and tool frames for the landing-page sequence
    (OUT / "assets" / "ingame").mkdir()
    frames = sorted((SRC / "assets" / "ingame").glob("*.webp"))
    if len(frames) < 6:
        sys.exit("FAIL: expected at least 6 sequence frames, found %d" % len(frames))
    for f in frames:
        shutil.copy2(f, OUT / "assets" / "ingame" / f.name)
    # the OFL obliges us to distribute the licence with the fonts
    licences = sorted((SRC / "assets" / "fonts").glob("OFL-*.txt"))
    if len(licences) != 2:
        sys.exit("FAIL: expected 2 OFL licence texts, found %d" % len(licences))
    for lic in licences:
        shutil.copy2(lic, OUT / "assets" / "fonts" / lic.name)
    shutil.copy2(src_standalone, OUT / STANDALONE)

    # ---- landing page ---------------------------------------------------
    land = (OUT / "index.html").read_text(encoding="utf-8")
    land = once(land, "<title>AOO Creator</title>",
                "<title>AOO Creator</title>\n" + meta(base), "landing metadata")
    land = land.replace("AOO-Creator-STANDALONE.html", STANDALONE)
    land = land.replace("vVERSION_TOKEN", f"v{VERSION}")
    if "VERSION_TOKEN" in land or "AOO-Creator-STANDALONE" in land:
        sys.exit("FAIL: a landing-page placeholder was not substituted")
    (OUT / "index.html").write_text(land, encoding="utf-8")

    # ---- the tool -------------------------------------------------------
    app = (OUT / "app.html").read_text(encoding="utf-8")
    app = once(app, '  <link rel="stylesheet" href="styles.css">',
               '  <link rel="icon" href="assets/aoo-logo.png" type="image/png">\n'
               '  <link rel="stylesheet" href="styles.css">', "app favicon")
    app = once(app, '      <div class="welcome-foot">',
               OFFLINE + '\n      <div class="welcome-foot">', "offline link")
    app = once(app, '<div class="header-actions">',
               '<div class="header-actions">'
               '<a class="site-home" href="index.html">&larr; What is this?</a>',
               "home link")
    (OUT / "app.html").write_text(app, encoding="utf-8")

    css = (OUT / "styles.css").read_text(encoding="utf-8")
    (OUT / "styles.css").write_text(css + OFFLINE_CSS + HOMELINK_CSS, encoding="utf-8")

    # a stray URL should reach the page that explains the tool, not a relative guess
    (OUT / "404.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>AOO Creator</title>'
        '<meta http-equiv="refresh" content="0;url=./">'
        '<p>Not found. <a href="./">Go to AOO Creator</a>.</p>\n', encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n" + (f"\nSitemap: {base}/sitemap.xml\n" if base else ""),
        encoding="utf-8")
    (OUT / "_headers").write_text(HEADERS, encoding="utf-8")
    # Pages runs Jekyll otherwise, which silently drops files beginning with _
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # ---- guard ----------------------------------------------------------
    # the mirror of the standalone's "no external reference survived inlining":
    # here every reference must resolve to a file we actually shipped
    checked = 0
    for page_name in ("index.html", "app.html"):
        page = (OUT / page_name).read_text(encoding="utf-8")
        refs = refs_of(page)
        missing = sorted(r for r in refs if not (OUT / r).exists())
        if missing:
            sys.exit(f"FAIL: unresolved reference(s) in docs/{page_name}: " + ", ".join(missing))
        checked += len(refs)
    if "<script" not in (OUT / "app.html").read_text(encoding="utf-8"):
        sys.exit("FAIL: app.html lost its script tag")

    # Nothing unreferenced ships. The sequence uses six of the eight in-game
    # frames; the spares were quietly adding 61 KB to every visitor's download.
    # This is the mirror of the check below: there, every reference must resolve;
    # here, everything shipped must be referenced.
    pages = "".join((OUT / n).read_text(encoding="utf-8") for n in ("index.html", "app.html"))
    orphans = [f for f in sorted((OUT / "assets" / "ingame").glob("*"))
               if f.name not in pages]
    for f in orphans:
        f.unlink()
    if orphans:
        print("  pruned %d unreferenced frame(s): %s"
              % (len(orphans), ", ".join(f.name for f in orphans)))

    # every url() inside the stylesheet must resolve too. A missing font file
    # does not throw; it silently renders in the fallback face, so nothing but
    # a check like this would catch it.
    sheet = (OUT / "styles.css").read_text(encoding="utf-8")
    css_refs = set(re.findall(r"url\(['\"]?(assets/[^)'\"]+)['\"]?\)", sheet))
    css_missing = sorted(r for r in css_refs if not (OUT / r).exists())
    if css_missing:
        sys.exit("FAIL: unresolved url() in docs/styles.css: " + ", ".join(css_missing))
    checked += len(css_refs)

    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"  docs/ built: {len(list(OUT.rglob('*')))} entries, {total // 1024} KB total")
    print(f"  index.html = landing, app.html = the tool, {checked} references all resolve")
    if base:
        print(f"  canonical + share image absolute at {base}")
    else:
        print("  NOTE: no --base-url, so og:image is relative. Link previews on Discord/"
              "Nexus/X\n        need the absolute form - rebuild with --base-url once the "
              "domain is live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
