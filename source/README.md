# AOO Creator v0.2.0

A dependency-free browser tool for building Archive of Our Overwrites fic collection mods. It runs entirely on the user's device and is ready for static hosting on GitHub Pages.

## Use

Open `index.html` through any static web server. For GitHub Pages, publish the contents of this folder at the repository root or from a `docs` directory.

Opening `index.html` by double-clicking it will **not** work — browsers block ES modules on `file://`. Use the single-file standalone build for offline use.

1. Name the collection and set its permanent namespace in Collection settings.
2. Add your authors in the Authors roster.
3. Write chapters in the Write tab; fill in metadata in Details.
4. Review AOO preview and Validation.
5. Save the `.aoopack.json` project file and keep it — it is required to publish updates.
6. Select **Validate & build ZIP** to export a Nexus-ready collection mod.

The exported ZIP requires Archive of Our Overwrites `v0.3.0-dev.17` or newer. It contains REDscript registration, localization, a manifest, project source, version, and readme. Every file lives under `r6/scripts/<Namespace>/`, so any number of fic packs can be installed side by side without colliding. No fic text is uploaded anywhere by the creator.

## Contract

- Framework: `1.0.0`
- Creator schema: `1`
- English output; the generated localization module is structured for later language packages.
- Stable internal author, work, chapter, and comment IDs survive display-name changes and project re-imports.
- Maximum author pseud: 24 characters
- Maximum work or chapter title: 120 characters
- Maximum market summary: 140 characters
- Maximum tag label: 80 characters
- Maximum open tags per work: 100
- Active author release interval: minimum 3 in-game days

## Interface

- **Write** — the manuscript. Chapter list on the left, one large body field on the right, author's notes collapsed. Word counts update as you type.
- **Details** — work metadata: author, rating, archive warning, category, tags, summary. Release timing appears only on a work in progress; word count is derived, not typed.
- **Comments** — optional archived comments, valid only on complete works by inactive authors.
- **AOO preview** — the work card as the game renders it, including long titles and tag walls.
- **Validation** — errors block the build; warnings are advisory.
- **Collection settings** (gear icon) — pack name, namespace, version, creator, licence.

## Included safeguards

A library of collections with a switcher, local autosave, undo/redo, import/export, four visual themes, first-run tutorial, examples, long-title and tag-wall preview, fixed AO3 selections plus custom open tags, validation severity, guarded author deletion, in-page confirmations rather than browser popups, and a browser-side ZIP builder with no third-party service dependency.

## Tests

    python ../run-tests.py

Runs `tests/browser-tests.js` against `core.js` in headless Edge or Chrome. `tests/creator.test.mjs` holds equivalent assertions for `node --test` where Node is available.
