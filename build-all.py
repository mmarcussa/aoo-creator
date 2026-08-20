"""Build both artifacts from source/ and run every guard.

    python build-all.py [--base-url https://your.domain]

One source tree, two outputs:
    AOO-Creator-v<VERSION>-standalone.html   the download (offline, Nexus, direct send)
    docs/                                    the hosted site (GitHub Pages / Cloudflare)

Stops at the first failure, so a broken build never reaches either artifact.
"""
import subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
base = []
if "--base-url" in sys.argv:
    base = ["--base-url", sys.argv[sys.argv.index("--base-url") + 1]]

STEPS = [
    ("build standalone", ["build-standalone.py"]),
    ("build web",        ["build-web.py"] + base),
    ("export tests",     ["run-tests.py"]),
    ("ui contract",      ["check-ui-contract.py"]),
    ("theme audit",      ["check-themes.py"]),
    ("cursor audit",     ["check-cursors.py"]),
]

for label, cmd in STEPS:
    print("\n===== " + label + " " + "=" * (58 - len(label)), flush=True)
    r = subprocess.run([sys.executable, str(ROOT / cmd[0])] + cmd[1:], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"\nSTOPPED: {label} failed (exit {r.returncode}). Neither artifact is trustworthy.")

print("\n===== all green " + "=" * 48, flush=True)
print("  download artifact : AOO-Creator-v*-standalone.html")
print("  hosted artifact   : docs/")
