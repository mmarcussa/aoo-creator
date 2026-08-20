"""Fetch the embedded OFL font files and emit their @font-face CSS.

Run once; the .woff2 files are committed and the build reads them from disk.

Why these exact faces, from measuring what the tool actually renders:

  Literata 400 + 700   --font-prose is used on exactly three things: the
                       manuscript textarea, the notes textarea, and the write
                       pane's h1. A textarea renders one style throughout, so
                       italic runs are structurally impossible there and a
                       Literata Italic would be ~38 KB of unreachable payload.
                       The h1 is weight 700, so bold earns its place.
  IBM Plex Sans 400+700  the stylesheet asks for weight 700 twenty-seven times
                       and 800 thirteen times; 600 appears twice. 700 is the
                       weight the UI is actually built on.

Subsets: latin and latin-ext. latin-ext costs ~123 KB and covers U+0100-024F,
which is where Polish, Czech and Hungarian letters live. This is an archive for
fiction with international pseuds and Eastern European character names, and a
name rendered half in Literata and half in a fallback reads as a bug, so it
stays. Cyrillic, Greek and Vietnamese are not fetched.

Asking the CSS API with a browser UA returns pre-subset WOFF2; the upstream
repos ship variable TTFs an order of magnitude larger.
"""
import pathlib, re, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "source" / "assets" / "fonts"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

WANT = {
    "Literata": ("https://fonts.googleapis.com/css2?"
                 "family=Literata:wght@400;700&display=swap"),
    "IBMPlexSans": ("https://fonts.googleapis.com/css2?"
                    "family=IBM+Plex+Sans:wght@400;700&display=swap"),
}
KEEP = ("latin", "latin-ext")
FAMILY_CSS_NAME = {"Literata": "Literata", "IBMPlexSans": "IBM Plex Sans"}


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode("utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.glob("*.woff2"):
        stale.unlink()

    faces, total = [], 0
    for name, css_url in WANT.items():
        try:
            css = fetch(css_url)
        except Exception as exc:
            sys.exit("FAIL: could not reach the font CSS API for %s: %s" % (name, exc))
        blocks = re.findall(r"/\*\s*([a-z-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S)
        if not blocks:
            sys.exit("FAIL: no @font-face blocks returned for %s" % name)

        for subset, body in blocks:
            if subset not in KEEP:
                continue
            url = re.search(r"url\((https://[^)]+\.woff2)\)", body)
            weight = re.search(r"font-weight:\s*(\d+)", body)
            urange = re.search(r"unicode-range:\s*([^;]+);", body)
            if not (url and weight and urange):
                sys.exit("FAIL: incomplete @font-face for %s/%s" % (name, subset))
            fname = "%s-%s-%s.woff2" % (name, weight.group(1), subset)
            data = fetch(url.group(1), binary=True)
            if data[:4] != b"wOF2":
                sys.exit("FAIL: %s is not a WOFF2 file" % fname)
            (OUT / fname).write_bytes(data)
            total += len(data)
            faces.append((FAMILY_CSS_NAME[name], weight.group(1), fname,
                          urange.group(1).strip()))
            print("  %-38s %6.1f KB  weight %s" % (fname, len(data) / 1024, weight.group(1)))

    # font-display:swap so prose is readable immediately in the fallback and
    # reflows once, rather than blanking while the face loads
    lines = ["/* ================= embedded faces =================",
             "   Literata (c) 2017 The Literata Project Authors.",
             "   IBM Plex Sans (c) 2017 IBM Corp, Reserved Font Name \"Plex\".",
             "   Both under the SIL Open Font License 1.1; texts in assets/fonts/OFL-*.txt.",
             "   Fetched by get-fonts.py. Both families are OFL, so redistributing them",
             "   inside a mod tool is permitted. swap, not block: a writer should never",
             "   watch an empty page while a font loads. */"]
    for fam, weight, fname, urange in faces:
        lines.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;"
                     "font-display:swap;src:url('assets/fonts/%s') format('woff2');"
                     "unicode-range:%s}" % (fam, weight, fname, urange))
    (OUT / "faces.css").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n  %d files, %.1f KB total" % (len(faces), total / 1024))
    print("  faces.css written with %d @font-face blocks" % len(faces))
    return 0


if __name__ == "__main__":
    sys.exit(main())
