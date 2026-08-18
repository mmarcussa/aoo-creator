// Assertions ported from creator.test.mjs so they run in a real browser
// (no Node required). Executed by ../../run-tests.py via headless Edge.
// `core.js` is inlined ahead of this file, so its exports are in scope.

function runTests() {
  const results = [];
  const ok = (name, pass, detail) => results.push({ name, pass: !!pass, detail: detail || "" });

  for (const kind of ["oneshot", "complete", "active", "collection"]) {
    let project, files;
    try {
      project = getExample(kind);
    } catch (e) {
      ok(`${kind}: example loads`, false, e.message);
      continue;
    }
    ok(`${kind}: example loads`, true);

    const errors = validateProject(project).filter(i => i.kind === "error");
    ok(`${kind}: satisfies schema v1`, errors.length === 0,
       errors.map(e => `${e.path}: ${e.message}`).join(" / "));

    files = generatePackFiles(project);
    const paths = Object.keys(files);
    ok(`${kind}: emits Content.reds`, paths.some(p => p.endsWith(".Content.reds")));
    ok(`${kind}: emits Localization.reds`, paths.some(p => p.endsWith(".Localization.reds")));

    const manifestPath = paths.find(p => p.endsWith("manifest.json"));
    ok(`${kind}: manifest is schema v1`,
       manifestPath && /"schemaVersion": 1/.test(files[manifestPath]));

    // Regression guard: nothing may land at the game root, or two installed
    // fic packs overwrite each other's metadata (and the core mod's VERSION).
    const stray = paths.filter(p => !p.startsWith("r6/scripts/"));
    ok(`${kind}: no files at game root`, stray.length === 0, stray.join(", "));

    // Every path must sit under this pack's own namespaced folder.
    const ns = JSON.parse(files[manifestPath]).namespace;
    const outside = paths.filter(p => !p.startsWith(`r6/scripts/${ns}/`));
    ok(`${kind}: all paths namespaced`, outside.length === 0, outside.join(", "));

    results.push({ deferred: kind, files });
  }

  // Invalid project must be rejected on every limit creator.test.mjs checks.
  const bad = getExample("oneshot");
  bad.works[0].title = "X".repeat(LIMITS.title + 1);
  bad.works[0].tags = Array.from({ length: LIMITS.tags + 1 }, (_, i) => `Tag ${i}`);
  bad.works[0].active = true;
  bad.works[0].releaseIntervalDays = 1;
  const badIssues = validateProject(bad).filter(i => i.kind === "error");
  const said = badIssues.map(i => i.message).join(" | ");
  ok("invalid: title length rejected", /Title exceeds/.test(said), said);
  ok("invalid: tag count rejected", /open tags/.test(said), said);
  ok("invalid: release interval rejected", /at least/.test(said), said);

  return results;
}

async function report() {
  const results = runTests();
  const zipChecks = [];
  for (const r of results.filter(x => x.deferred)) {
    const zip = createZip(r.files);
    const bytes = new Uint8Array(await zip.arrayBuffer());
    const sig = bytes[0] === 0x50 && bytes[1] === 0x4b && bytes[2] === 0x03 && bytes[3] === 0x04;
    zipChecks.push({ name: `${r.deferred}: ZIP local-file signature`, pass: sig, detail: "" });
    zipChecks.push({ name: `${r.deferred}: ZIP is non-empty`, pass: bytes.length > 100, detail: `${bytes.length} bytes` });
  }
  const all = results.filter(r => !r.deferred).concat(zipChecks);
  const failed = all.filter(r => !r.pass);
  const lines = all.map(r => `${r.pass ? "PASS" : "FAIL"}  ${r.name}${r.detail ? "  -- " + r.detail : ""}`);
  lines.push(`SUMMARY ${all.length - failed.length}/${all.length} passed`);
  document.getElementById("out").textContent = "[[" + lines.join("\n") + "]]";
}

report();
