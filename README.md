# AOO Creator v0.2.0 — working copy

Self-contained working copy of the AOO Creator, split out of the Codex project on
2026-08-18. The Codex project (`Documents/Codex/.../ArchiveOfOurOverwrites/creator/`)
was reverted to v0.1.0 and is untouched by this work.

## What's here

| Path | What it is |
|---|---|
| `AOO-Creator-v0.2.0-standalone.html` | The tool. Double-click it — no server, works offline. This is the file to send people. |
| `source/` | The editable source. Everything is built from here. |
| `build-standalone.py` | Regenerates the standalone file from `source/`. |
| `run-tests.py` | Runs the test suite in a real browser. No Node needed. |
| `check-ui-contract.py` | Verifies the markup still exposes every field the exporter reads. |
| `PackAuthorGuide.md` | The guide to hand to anyone publishing a collection. |

## Editing

Edit files in `source/`, then rebuild:

    python build-standalone.py "./source" "./AOO-Creator-v0.2.0-standalone.html"

The build inlines `styles.css`, `core.js`, `app.js` and the logo into one HTML file,
strips the ES module syntax, and asserts that no external reference survives — so a
broken build fails loudly instead of producing a dead page.

`source/` is also directly hostable: serve it over any static web server (or GitHub
Pages) and `index.html` works as-is. It will NOT work by double-clicking `source/index.html`
— browsers block ES modules on `file://`. That is what the standalone build exists to solve.

## Testing

    python run-tests.py

Runs `source/tests/browser-tests.js` against `source/core.js` in headless Edge or Chrome,
and exits non-zero if anything fails. These are the assertions from the project's original
`tests/creator.test.mjs` — which needs Node — plus guards on the pack layout. Run it after
any change to `core.js`.

Current status: **39/39 passing** across all four bundled examples.

Before and after any change to `index.html`, also run:

    python check-ui-contract.py

`core.js` never touches the DOM, so styling cannot affect what gets exported. Markup can:
losing a `data-bind` attribute or an element id while rearranging the page would silently
drop that field from every exported pack, and the browser tests would not notice because
they call `core.js` directly. This compares the markup against a recorded baseline of all
38 binding attributes and 53 element ids. After an intentional change, re-record with
`--update`.

## What changed from v0.1.0

- **Write tab** replaces the old Work/Chapters split. Chapter strip on the left, one large
  manuscript field on the right, notes collapsed. Metadata moved to a **Details** tab.
- **Conditional fields** — release model and interval only appear on a work in progress.
  Marking a work complete clears the timed-release flag.
- **Derived values** — word count is computed from chapter text and read-only; the comments
  stat can no longer fall below the number of archived comments.
- **Fresh projects no longer open on a validation error** — the badge reads `–` until the
  first edit.
- **Restyled** — calmer panels, tighter fields, prose set in a serif. A later visual pass
  added depth to the chrome, gradient selection states, anchored tabs, and fixed accent
  roles: yellow for the primary action and current selection, cyan for system and counts,
  red for section labels and destructive actions, green for ready. The writing column is
  capped at a 74-character measure so prose is comfortable to read while typing. All of it
  is token-based, so the AOO, neutral dark, light and high-contrast themes follow without
  separate rules.
- **Guided tour.** The tutorial is now interactive, following the pattern from Eddyline
  Foundry: a dimmed backdrop, a highlight box around the element being described, and a
  positioned card with Back, Next, Skip and a step counter. Ten steps, switching tabs as it
  goes, ending on the build button. Arrow keys navigate; Escape exits. The first-run card
  now offers the tour or exploring alone, and the Tutorial button restarts it any time.
- **Tutorial text rewritten** for the new flow, including the rule that matters most: keep your
  `.aoopack.json` and re-import it to publish updates, or readers lose everything they
  recovered from the old version.
- **Multiple collections.** The tool now keeps a library of collections instead of a single
  project, with a switcher at the top of the left rail plus New and Delete. Switching
  preserves each collection's works, authors and chapters independently, and the whole
  library survives closing the browser. Creating a new collection is no longer destructive,
  so it needs no confirmation; deleting one does, and the last remaining collection cannot
  be deleted. An existing single-project autosave from v0.1.0 is migrated into the library
  automatically on first open.
- **Authors moved out of the left rail** into their own searchable roster. The rail showed
  every author as a row, which fell apart past a few dozen; it now shows a count that opens
  the roster. Pseud and status are edited inline, renaming an author still updates the pseud
  on all of their works, and an author who still has works cannot be deleted.
- **No browser popups.** Every `prompt()` and `confirm()` is gone — seven in total, two
  prompts and five confirms. Author creation and editing happen inline in the roster.
  Five genuinely destructive actions (delete work, chapter, comment, author, collection)
  use an in-page confirmation styled like the rest of the tool; the rest needed no
  confirmation once they stopped destroying anything.
- **Quiet control treatment.** Buttons were flat outlined rectangles differing only by
  colour — the default result of deciding nothing. Optional actions are now plain text that
  gain a background on hover, the primary action is a solid fill so it is unmistakable, tabs
  are underlined rather than boxed, and several nested outlines were removed so surfaces read
  by tone. Save project deliberately keeps its border: it is the one that prevents permanent
  loss. Text on solid accents uses `var(--bg)`, which inverts correctly in the light theme.
- **Action hierarchy.** Three action tiers rather than two: primary for the build, a new
  secondary tier for Save project (not the goal, but the one that prevents permanent loss),
  ghost for everything optional. Deleting a whole collection is now visually heavier than
  deleting a chapter. Rail entries dropped their button-like borders for an inset accent
  bar, so navigation no longer looks like actions.
- **Autosave no longer lies.** The status bar used to say "local autosave active", which
  reads as "your work is safe" — it isn't. A chip at the right of the status bar now shows *Not saved
  to a file* or *Saved to a file* per collection, and clicking it saves, and the wording says autosave lives only
  in this browser. This is the highest-stakes misunderstanding in the tool: losing the
  `.aoopack.json` means never publishing a compatible update.
- **Import is explicit about replacing.** A project file carries the collection's identity,
  so importing one whose id matches a collection already in the browser replaces it — that
  is the update flow. It now says so and asks first, naming the collection; importing a file
  with a new id still adds a collection silently, because nothing is at risk. Imported
  collections are marked as file-backed, since that is where they came from.
- **Collection settings has a label.** It held the permanent namespace behind an unlabelled
  gear icon. It is now a **Settings** button beside New and Delete, and the namespace itself
  is shown in the rail so the irreversible value is visible without opening anything.
- **The works list carries state.** Each row now shows the author pseud and chapter count,
  plus a dot: green ready, amber warnings, red errors. Previously it was title and chapter
  count only, which is not enough to navigate twenty works.
- **Where the problems are.** The Works heading shows how many works have errors, so a
  writer finishing a large collection can see what is left without clicking through. The
  list re-render is debounced so typing stays smooth.
- **Pack layout fixed.** `pack.aoopack.json`, `manifest.json`, `README.txt` and `VERSION`
  used to land at the Cyberpunk root, where any two installed fic packs overwrote each
  other's copies — and the core mod's own `VERSION`. Everything now sits under
  `r6/scripts/<Namespace>/`, so packs are fully self-contained and cannot collide.

Project data shape is unchanged (`schemaVersion` is still `1`), so v0.1.0 `.aoopack.json`
files import cleanly.

## Verified

Tested on `file://` in headless Edge: the bundle executes fully, the Write/Details flow
works, derived word count updates across tabs, conditional fields toggle, and export
produces a valid ZIP — 6 files, `PK\x03\x04` signature, CRC clean when opened with a real
ZIP reader, correct `r6/scripts/<Namespace>/` REDscript layout, manifest stamped
`creatorVersion 0.2.0 / schemaVersion 1 / frameworkVersion 1.0.0`.

## Waiting on the core mod (not tool defects)

Both of these are correct in the tool and correct in the AOO source. They only need the
dev.17 core to be repacked and shipped:

- `AOO_MIN_VERSION` is `0.3.0-dev.17`. That build doesn't exist in `dist/` yet — the last
  packaged core is dev.16.1.
- The rating dropdown offers **Not Rated**, emitting `AOORating.NotRated`. The enum is
  already in the AOO source (`AOO.Classes.reds`, appended as `= 4` so G/T/M/E keep their
  numbers), but it is absent from the packaged dev.16.1 build. Since REDscript compiles
  globally, a pack using it would fail to compile against dev.16.1.

Nothing to change here — the repack resolves both.
