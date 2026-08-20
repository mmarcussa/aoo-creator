"""Turn raw in-game screenshots into landing-page frames.

Run once when the screenshots change; the WebP output is committed and the build
just copies it.

    python prepare-shots.py "C:/path/to/screenshot folder"

Cropping is measured, not eyeballed. The AOO panel is bordered in saturated
cyan, so its bounding box is found by colour and the crop is derived from that.
Two colours matter and are easy to confuse:

    device bezel   (201,150,67)  saturated orange, r-b ~134
    the tan wall   (126,109,101) nearly neutral,   r-b ~25

A naive "is it orange" test matches both, which is why this keys on saturation.

The crop keeps a margin of surrounding screen so each frame still reads as a
game UI rather than a raw web screenshot, and drops the wall and the lamp,
which carry no information and cost a third of the pixels.
"""
import pathlib, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "source" / "assets" / "ingame"
WIDTH = 1280          # enough for a 2x retina render at the page's display size
QUALITY = 82
MARGIN = 22           # screen kept around the panel, in source pixels

# order matters: this is the sequence the landing page steps through
SEQUENCE = [
    ("005950", "net-directory", "Archive of Our Overwrites on the Night City Net"),
    ("010015", "archive-empty", "The archive, before any collection is installed"),
    ("010141", "archive-index", "Your collection, listed with its stats"),
    ("010156", "work-page", "A reader opens your fic"),
    ("010118", "shard-market", "Chapters recovered from the Shard Market"),
    ("010104", "timed-release", "A timed work releasing on a schedule"),
]


def panel_box(im):
    """Locate the AOO panel by the long cyan runs that form its frame.

    Keying on "any cyan pixel" fails: the MESSAGES/NET tabs above the panel and
    accents at the screen edges are cyan too, so the box came back as the whole
    screen. The panel's own border is the giveaway - a horizontal run over a
    thousand pixels wide, which nothing else in the frame produces.
    """
    W, H = im.size
    px = im.load()

    def is_cyan(c):
        r, g, b = c
        return b > 110 and g > 110 and (g - r) > 45 and (b - r) > 45

    rows = []
    for y in range(H):
        n = sum(1 for x in range(0, W, 2) if is_cyan(px[x, y]))
        if n * 2 > 1100:
            rows.append(y)
    if len(rows) < 2:
        return None
    # the topmost long run is the tab strip's rule; the panel frame is below it
    top = min(y for y in rows if y > 330)
    # the empty-archive frame has a fainter bottom rule that the width threshold
    # misses, so require the bottom to be a real distance below the top
    lower = [y for y in rows if y > top + 300]
    bottom = max(lower) if lower else None
    if bottom is None:
        return None
    band = [x for x in range(W) if is_cyan(px[x, top])]
    if not band:
        return None
    return min(band), top, max(band), bottom


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else "C:/Users/UsEr/Pictures/Screenshots")
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    made = []

    # The game UI is fixed on screen, so every frame must share ONE crop or the
    # sequence jitters between steps. Detect per frame, then agree on the median
    # and apply that to all; a frame whose own detection strays far from it is
    # reported rather than silently framed differently.
    sources, boxes = [], []
    for stamp, name, caption in SEQUENCE:
        matches = sorted(src.glob("*%s*.png" % stamp))
        if not matches:
            sys.exit("FAIL: no screenshot matching %s in %s" % (stamp, src))
        im = Image.open(matches[0]).convert("RGB")
        sources.append((im, name, caption, matches[0].name))
        b = panel_box(im)
        if b:
            boxes.append(b)
    if not boxes:
        sys.exit("FAIL: could not locate the panel in any frame")

    def med(i):
        v = sorted(b[i] for b in boxes)
        return v[len(v) // 2]

    x0, y0, x1, y1 = med(0), med(1), med(2), med(3)
    print("  agreed panel box: x %d..%d  y %d..%d  (from %d/%d frames)"
          % (x0, x1, y0, y1, len(boxes), len(SEQUENCE)))
    print("")
    for b in boxes:
        if max(abs(b[i] - [x0, y0, x1, y1][i]) for i in range(4)) > 12:
            print("  NOTE: one frame's own box strayed from the agreed crop: %s" % (b,))

    for im, name, caption, srcname in sources:
        W, H = im.size
        crop = (max(0, x0 - MARGIN), max(0, y0 - MARGIN),
                min(W, x1 + MARGIN), min(H, y1 + MARGIN))
        im = im.crop(crop)
        scale = WIDTH / im.width
        im = im.resize((WIDTH, round(im.height * scale)), Image.LANCZOS)
        dest = OUT / ("%s.webp" % name)
        im.save(dest, "WEBP", quality=QUALITY, method=6)
        size = dest.stat().st_size
        total += size
        made.append((name, im.width, im.height, size, caption))
        print("  %-15s %4dx%-4d %6.1f KB   %s" % (name, im.width, im.height,
                                                  size / 1024, caption))

    print("\n  %d frames, %.1f KB total" % (len(made), total / 1024))
    heights = {h for _, _, h, _, _ in made}
    if len(heights) > 1:
        print("  NOTE: frame heights differ %s - the sequence container should"
              " reserve the tallest to avoid layout shift" % sorted(heights))
    return 0


if __name__ == "__main__":
    sys.exit(main())
