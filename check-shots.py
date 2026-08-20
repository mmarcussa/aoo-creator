"""Fail the build when the landing page is showing an older version of the tool.

This exists because it happened. Three features landed - the Nexus page, the
update diff, undo in the toolbar - and the landing page kept showing screenshots
taken before any of them existed. The page ended up claiming "the Creator writes
the mod page too" beside an image with no such panel in it, which is the kind of
quiet dishonesty nobody notices until a reader does.

Nothing in the build knew the images were derived from the UI, so nothing could
say they had gone stale. prepare-tool-shots.py now stamps a hash of the files
that decide what the tool looks like, and this compares it.

    python prepare-tool-shots.py     # re-shoot and re-stamp

The stamp deliberately covers index.html, styles.css and app.js only. VERSION
and core.js do not change what a screenshot looks like, and including them would
make this cry wolf on every exporter edit.
"""
import hashlib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"
STAMP = SRC / "assets" / "shots.stamp"
WATCHED = ("index.html", "styles.css", "app.js")
SHOTS = ("assets/ingame/tool-write.webp", "assets/ingame/tool-build.webp",
         "assets/screenshot-app.png")


def fingerprint():
    h = hashlib.sha256()
    for name in WATCHED:
        h.update((SRC / name).read_bytes())
    return h.hexdigest()


def main():
    missing = [s for s in SHOTS if not (SRC / s).exists()]
    if missing:
        sys.exit("FAIL: missing landing image(s): " + ", ".join(missing) +
                 "\n  run: python prepare-tool-shots.py")

    if not STAMP.exists():
        sys.exit("FAIL: no shots.stamp; the landing images cannot be shown to match "
                 "the tool.\n  run: python prepare-tool-shots.py")

    want = fingerprint()
    have = STAMP.read_text(encoding="utf-8").strip()
    if want != have:
        sys.exit("FAIL: the tool's UI changed since the landing images were taken.\n"
                 "  stamped %s\n  current %s\n"
                 "  The landing page would show an older version of the tool.\n"
                 "  run: python prepare-tool-shots.py" % (have[:16], want[:16]))

    print("  landing images match the current UI (%s)" % want[:16])
    print("SUMMARY landing images are current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
