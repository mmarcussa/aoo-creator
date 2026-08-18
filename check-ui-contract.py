"""Guard the contract between the markup and the exported data.

Styling changes are safe by construction: core.js never touches the DOM. The risk in a
restyle is markup — losing a data-binding attribute or an element id while rearranging
index.html silently drops a field from every exported pack, and the browser tests will
not notice because they call core.js directly.

This compares index.html and app.js against a recorded baseline of every binding
attribute and every id app.js depends on.

    python check-ui-contract.py            # verify against the baseline
    python check-ui-contract.py --update   # re-record after an intentional change

Exits 0 when the contract holds, 1 when anything the exporter depends on went missing.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "source"
BASELINE = SRC / "tests" / "ui-contract.json"

BINDINGS = ["data-bind", "data-bind-list", "data-bind-stat", "data-pack",
            "data-chapter-field", "data-comment-field", "data-author-field"]


def scan():
    html = (SRC / "index.html").read_text(encoding="utf-8")
    app = (SRC / "app.js").read_text(encoding="utf-8")

    found = {}
    for attr in BINDINGS:
        # attributes live in index.html and in app.js template literals alike
        names = set(re.findall(attr + r'="([A-Za-z0-9_]+)"', html))
        names |= set(re.findall(attr + r'="([A-Za-z0-9_]+)"', app))
        found[attr] = sorted(names)

    ids_used = sorted(set(re.findall(r'\$\("#([A-Za-z0-9_]+)"\)', app)))
    # ids are declared in the static markup and in app.js render templates alike
    ids_declared = set(re.findall(r'id="([A-Za-z0-9_]+)"', html))
    ids_declared |= set(re.findall(r'id="([A-Za-z0-9_]+)"', app))
    return {"bindings": found, "idsUsed": ids_used,
            "idsMissing": sorted(i for i in ids_used if i not in ids_declared)}


def main():
    now = scan()
    failures = []

    # An id app.js queries but the markup no longer declares is always a break.
    for missing in now["idsMissing"]:
        failures.append("app.js queries #%s but index.html no longer declares it" % missing)

    if "--update" in sys.argv:
        BASELINE.write_text(json.dumps(now, indent=2) + "\n", encoding="utf-8")
        print("baseline recorded: %d ids, %d binding groups"
              % (len(now["idsUsed"]), len(now["bindings"])))
        return 1 if failures else 0

    if not BASELINE.exists():
        sys.exit("No baseline. Run: python check-ui-contract.py --update")

    was = json.loads(BASELINE.read_text(encoding="utf-8"))

    for attr in BINDINGS:
        before, after = set(was["bindings"].get(attr, [])), set(now["bindings"][attr])
        for gone in sorted(before - after):
            failures.append('%s="%s" disappeared - that field would stop being exported' % (attr, gone))
        for added in sorted(after - before):
            print('NOTE  new binding %s="%s"' % (attr, added))

    for gone in sorted(set(was["idsUsed"]) - set(now["idsUsed"])):
        print("NOTE  app.js no longer queries #%s" % gone)

    if failures:
        for f in failures:
            print("FAIL  " + f)
        print("SUMMARY %d contract break(s)" % len(failures))
        return 1

    total = sum(len(v) for v in now["bindings"].values())
    print("PASS  %d bindings and %d element ids intact" % (total, len(now["idsUsed"])))
    print("SUMMARY ui contract holds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
