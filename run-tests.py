"""Run the AOO Creator test suite in a real browser (headless Edge/Chrome).

The project's original tests/creator.test.mjs needs Node. This runner executes the
same assertions (see source/tests/browser-tests.js) against the same core.js, in the
same engine the tool actually ships to, and needs nothing installed but a browser.

    python run-tests.py

Exits 0 if every assertion passes, 1 otherwise.
"""
import os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    sys.exit("FAIL: no Edge or Chrome found; edit BROWSERS in run-tests.py")


def build_page():
    core = (SRC / "core.js").read_text(encoding="utf-8")
    core = re.sub(r"(?m)^export\s+(?=(const|let|var|function|class|async)\b)", "", core)
    if re.search(r"(?m)^\s*export\b", core):
        sys.exit("FAIL: unhandled export form in core.js")
    tests = (SRC / "tests" / "browser-tests.js").read_text(encoding="utf-8")
    return (
        '<!doctype html><meta charset="utf-8"><title>tests</title>'
        '<body><pre id="out">RUNNING</pre><script>\n'
        + core + "\n" + tests + "\n</script>"
    )


def main():
    browser = find_browser()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="aoo-tests-"))
    try:
        page = tmp / "tests.html"
        page.write_text(build_page(), encoding="utf-8")
        out = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--no-first-run",
             "--virtual-time-budget=10000", f"--user-data-dir={tmp / 'profile'}",
             "--dump-dom", page.as_uri()],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
        ).stdout
        m = re.search(r"\[\[(.*?)\]\]", out, re.S)
        if not m:
            sys.exit("FAIL: tests did not report; the page likely threw before finishing")
        body = m.group(1).strip()
        print(body)
        return 0 if "FAIL" not in body else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
