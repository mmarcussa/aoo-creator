"""Build the hosted version of AOO Creator into docs/.

Two artifacts come out of one source tree:

  build-standalone.py  ->  AOO-Creator-v0.2.0-standalone.html   (download / offline / Nexus)
  build-web.py         ->  docs/                                 (GitHub Pages, later Cloudflare)

They are deliberately the same tool. The hosted copy is not a different product with
web fonts and analytics bolted on; a writer who downloads the offline file after using
the site should get exactly what they just used. So this script only adds what a URL
needs and a file:// page cannot use: link-preview metadata, a favicon, cache headers,
and a link to fetch the offline copy.

    python build-web.py                          # relative og:image, fine for testing
    python build-web.py --base-url https://your.domain   # absolute, needed for real previews

Exits non-zero if any reference in the built page does not resolve to a shipped file.
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

# Copied verbatim. schema.json rides along because it is the published contract a
# pack author may want to read; everything else here is the running application.
COPY = ["index.html", "styles.css", "app.js", "core.js", "404.html", "schema.json"]
ASSETS = ["aoo-logo.png", "share-card.png"]

TITLE = "AOO Creator"
DESC = ("Write fic collections for Cyberpunk 2077's Archive of Our Overwrites and export a "
        "Nexus-ready mod. Runs entirely in your browser \u2014 no account, nothing uploaded.")


def meta(base):
    img = f"{base}/assets/share-card.png" if base else "assets/share-card.png"
    canonical = f'\n  <link rel="canonical" href="{base}/">' if base else ""
    return f"""  <link rel="icon" href="assets/aoo-logo.png" type="image/png">
  <link rel="apple-touch-icon" href="assets/aoo-logo.png">
  <meta name="theme-color" content="#0b1114">
  <meta name="color-scheme" content="dark light">{canonical}
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{TITLE}">
  <meta property="og:title" content="{TITLE} \u2014 build fic collection mods">
  <meta property="og:description" content="{html.escape(DESC, quote=True)}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Archive of Our Overwrites Creator">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{TITLE} \u2014 build fic collection mods">
  <meta name="twitter:description" content="{html.escape(DESC, quote=True)}">
  <meta name="twitter:image" content="{img}">
"""


OFFLINE = f"""
      <p class="welcome-offline">Working without a connection, or want to keep a copy?
      <a href="{STANDALONE}" download>Download the single-file version</a> \u2014 one HTML file,
      identical to this page, opens straight from your desktop.</p>
"""

OFFLINE_CSS = """
/* hosted build only: pointer to the downloadable single-file copy */
.welcome-offline{margin:.35rem 0 0;font-size:.86rem;line-height:1.55;color:var(--muted)}
.welcome-offline a{color:var(--accent);text-decoration:underline;text-underline-offset:3px}
.welcome-offline a:hover{color:var(--fg)}
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  X-Frame-Options: DENY

/assets/*
  Cache-Control: public, max-age=604800

/*.css
  Cache-Control: public, max-age=86400

/*.js
  Cache-Control: public, max-age=86400

/index.html
  Cache-Control: public, max-age=0, must-revalidate
"""


def once(text, old, new, what):
    if text.count(old) != 1:
        sys.exit(f"FAIL: {what}: {text.count(old)} matches for {old[:70]!r}")
    return text.replace(old, new)


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

    for name in COPY:
        shutil.copy2(SRC / name, OUT / name)
    for name in ASSETS:
        shutil.copy2(SRC / "assets" / name, OUT / "assets" / name)
    shutil.copy2(src_standalone, OUT / STANDALONE)

    page = (OUT / "index.html").read_text(encoding="utf-8")
    page = once(page, '  <link rel="stylesheet" href="styles.css">',
                meta(base) + '  <link rel="stylesheet" href="styles.css">', "head metadata")
    page = once(page, "      <div class=\"welcome-foot\">", OFFLINE + "\n      <div class=\"welcome-foot\">",
                "offline link")
    (OUT / "index.html").write_text(page, encoding="utf-8")

    css = (OUT / "styles.css").read_text(encoding="utf-8")
    (OUT / "styles.css").write_text(css + OFFLINE_CSS, encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n" + (f"\nSitemap: {base}/sitemap.xml\n" if base else ""),
        encoding="utf-8")
    (OUT / "_headers").write_text(HEADERS, encoding="utf-8")
    # Pages runs Jekyll otherwise, which silently drops files beginning with _
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # Guard, mirroring the standalone's "no external reference survived": here every
    # reference must resolve to a file we actually shipped.
    refs = set(re.findall(r'(?:href|src)="([^"#:]+?)"', page))
    missing = sorted(r for r in refs if not (OUT / r).exists())
    if missing:
        sys.exit("FAIL: unresolved reference(s) in docs/index.html: " + ", ".join(missing))
    if 'href="app.js"' in page or "<script" not in page:
        sys.exit("FAIL: index.html lost its script tag")

    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"  docs/ built: {len(list(OUT.rglob('*')))} entries, {total // 1024} KB total")
    print(f"  references checked: {len(refs)} all resolve")
    if base:
        print(f"  canonical + share image absolute at {base}")
    else:
        print("  NOTE: no --base-url, so og:image is relative. Link previews on Discord/"
              "Nexus/X\n        need the absolute form - rebuild with --base-url once the "
              "domain is live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
