// Assertions ported from creator.test.mjs so they run in a real browser
// (no Node required). Executed by ../../run-tests.py via headless Chrome.
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

  /* ---- Nexus page generator ----------------------------------------------
     A pure transform, so testable the same way the exporter is. These check
     the claims a writer would be embarrassed by: that every work appears,
     that the counts come from the prose rather than a stale field, and that
     an Explicit collection is flagged for Nexus's adult-content rule. */
  for (const kind of ["oneshot", "complete", "active", "collection"]) {
    const proj = getExample(kind);
    const page = generateNexusPage(proj);
    const body = page.text;

    ok(`${kind}: nexus page is non-empty`, body.length > 200, `${body.length} chars`);
    ok(`${kind}: nexus page names the collection`, body.indexOf(proj.pack.name) >= 0);
    ok(`${kind}: nexus page states the core version`,
       body.indexOf(AOO_MIN_VERSION) >= 0, AOO_MIN_VERSION);

    const missing = proj.works.filter(w => body.indexOf(w.title) < 0);
    ok(`${kind}: nexus page lists every work`, missing.length === 0,
       missing.map(w => w.title).join(", "));

    let written = 0;
    for (const w of proj.works) {
      for (const c of (w.chapters || [])) {
        const t = (c.body || "").trim();
        if (t) written += t.split(/\s+/).length;
      }
    }
    if (written > 0) {
      ok(`${kind}: nexus word count is real`, body.indexOf(" 0 words") < 0,
         `${written} words of prose`);
    }
    ok(`${kind}: nexus page returns notes array`, Array.isArray(page.notes));
  }

  const expl = getExample("oneshot");
  expl.works[0].rating = "Explicit";
  const explNotes = generateNexusPage(expl).notes.join(" ").toLowerCase();
  ok("explicit: adult-content note raised", explNotes.indexOf("adult") >= 0, explNotes);

  const br = getExample("oneshot");
  br.works[0].title = "[WIP] Static in the Walls";
  const brPage = generateNexusPage(br);
  ok("brackets: title left intact",
     brPage.text.indexOf("[WIP] Static in the Walls") >= 0);
  ok("brackets: writer is warned",
     brPage.notes.join(" ").toLowerCase().indexOf("square bracket") >= 0,
     brPage.notes.join(" | "));

  /* ---- update diff --------------------------------------------------------
     The dangerous edits are the invisible ones. A renamed title is cosmetic; a
     removed work or a changed namespace silently empties a reader's shelf. So
     these check that the reader-breaking cases land in `breaking`, and that the
     cosmetic ones do not. */
  {
    const clone = (o) => JSON.parse(JSON.stringify(o));
    const base = getExample("collection");
    const kinds = (d, list) => d[list].map(x => x.kind);

    // republishing untouched still warns: the version has not moved
    const same = diffProjects(base, clone(base));
    ok("diff: unchanged pack flags the version",
       kinds(same, "breaking").indexOf("version") >= 0, kinds(same, "breaking").join(","));

    // a bumped version alone is a clean update
    const bumped = clone(base);
    bumped.pack.version = "1.1.0";
    const okDiff = diffProjects(base, bumped);
    ok("diff: bumped version is clean", okDiff.ok === true, kinds(okDiff, "breaking").join(","));
    ok("diff: bump is reported as a change",
       kinds(okDiff, "changes").indexOf("version") >= 0);

    // dropping a work costs readers what they recovered
    const dropped = clone(bumped);
    const goneTitle = dropped.works[0].title;
    dropped.works.splice(0, 1);
    const dropDiff = diffProjects(base, dropped);
    ok("diff: removed work is breaking",
       kinds(dropDiff, "breaking").indexOf("work-removed") >= 0, kinds(dropDiff, "breaking").join(","));
    ok("diff: removed work is named",
       dropDiff.breaking.some(b => b.what.indexOf(goneTitle) >= 0));
    ok("diff: removed work makes it not ok", dropDiff.ok === false);

    // the namespace is the pack's identity
    const renamed = clone(bumped);
    renamed.pack.namespace = "SomethingElse";
    ok("diff: namespace change is breaking",
       kinds(diffProjects(base, renamed), "breaking").indexOf("namespace") >= 0);

    // losing a chapter costs eddies as well as prose
    const lostCh = clone(bumped);
    lostCh.works[0].chapters.splice(0, 1);
    ok("diff: removed chapter is breaking",
       kinds(diffProjects(base, lostCh), "breaking").indexOf("chapter-removed") >= 0);

    // adding is safe
    const added = clone(bumped);
    added.works[0].chapters.push(makeChapter("A new chapter"));
    const addDiff = diffProjects(base, added);
    ok("diff: added chapter is a change, not breaking",
       addDiff.ok === true && kinds(addDiff, "changes").indexOf("chapter-added") >= 0,
       kinds(addDiff, "breaking").join(","));

    // a retitled work is cosmetic: readers keep it
    const retitled = clone(bumped);
    retitled.works[0].title = "A Completely Different Name";
    const retDiff = diffProjects(base, retitled);
    ok("diff: retitle is cosmetic", retDiff.ok === true,
       kinds(retDiff, "breaking").join(","));
    ok("diff: retitle is still reported",
       kinds(retDiff, "changes").indexOf("work-retitled") >= 0);

    // going backwards is as wrong as standing still
    const back = clone(base);
    back.pack.version = "0.9.0";
    ok("diff: version going backwards is breaking",
       kinds(diffProjects(base, back), "breaking").indexOf("version") >= 0);
  }



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
