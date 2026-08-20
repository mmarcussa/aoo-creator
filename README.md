# AOO Creator v0.2.0 — working copy

Self-contained working copy of the AOO Creator, split out of the Codex project on
2026-08-18. The Codex project (`Documents/Codex/.../ArchiveOfOurOverwrites/creator/`)
was reverted to v0.1.0 and is untouched by this work.

## What's here

| Path | What it is |
|---|---|
| `source/` | The editable source. Both artifacts are built from here. |
| `AOO-Creator-v0.2.0-standalone.html` | **Download artifact.** Double-click it — no server, works offline. This is the file to send people. |
| `docs/` | **Hosted artifact.** Built output for GitHub Pages / Cloudflare. Never edit by hand; it is regenerated. |
| `build-all.py` | Builds both artifacts and runs every guard. The one command to run. |
| `build-standalone.py` | Builds the standalone file from `source/`. |
| `build-web.py` | Builds `docs/` from `source/`. |
| `run-tests.py` | Runs the test suite in a real browser. No Node needed. |
| `check-ui-contract.py` | Verifies the markup still exposes every field the exporter reads. |
| `check-themes.py` | Measures WCAG contrast across every theme. No theme ships unread. |
| `PackAuthorGuide.md` | The guide to hand to anyone publishing a collection. |

## Editing

Edit files in `source/`, then rebuild:

    python build-all.py

That builds both artifacts and runs all three guards, stopping at the first failure so
a broken build never reaches either output. To build just one:

    python build-standalone.py
    python build-web.py --base-url https://your.domain

## Two versions, one source

There are two shipping artifacts and they are deliberately the same tool. A writer who
downloads the offline copy after using the site should get exactly what they just used,
so the hosted version is not a separate product with web fonts and analytics bolted on.
The only things `docs/` adds are what a URL needs and a `file://` page cannot use.

| | `AOO-Creator-v0.2.0-standalone.html` | `docs/` |
|---|---|---|
| For | Nexus, direct sending, offline, archival | the public site, later a Cloudflare domain |
| Opens by | double-clicking | visiting a URL |
| Files | one, ~412 KB | six + assets, cached separately |
| Logo | base64 inlined (33% larger than the PNG) | a real PNG the browser caches |
| Adds | nothing external, by assertion | favicon, link-preview metadata, cache headers, a download link back to the standalone |
| Guard | no external reference survives inlining | every reference resolves to a shipped file |

Note the two guards are mirror images, and both fail the build loudly.

**Fonts stay system fonts in both.** Self-containment is what forces that constraint, and
matching the two versions is worth more than a web font would buy. If the standalone is
ever dropped, that constraint lifts — but not before.

**No analytics, ever.** The boot screen tells the reader `network — not required` and the
welcome screen says nothing is uploaded. A tracker would make both of those a lie.

### What `docs/` contains

| File | What it is |
|---|---|
| `index.html` | The landing page. Built from `source/landing.html`. |
| `app.html` | The tool. Built from `source/index.html`. |
| `AOO-Creator-v0.2.0-standalone.html` | The download the landing page offers. |

The landing page is the one place the two versions diverge, and it can, because
it is not the tool: no bindings, no themes, no export path, no contract. Nothing
a guard tracks can drift there. The tool itself stays identical in both.

### Deploying `docs/`

The name is not arbitrary: GitHub Pages' *deploy from a branch* option only offers the
repo root or `/docs`, so `docs/` deploys with no Action and no extra machinery. Cloudflare
Pages lets you point at any directory, so it works there too.

Settings → Pages → Source: *Deploy from a branch* → your branch, folder `/docs`.

It already contains `.nojekyll` (Pages otherwise drops files beginning with `_`),
`_headers` (Cloudflare Pages cache policy), `robots.txt`, and `404.html`.

Rebuild with `--base-url https://your.domain` once the domain exists: without it the
`og:image` is a relative path, and Discord, Nexus and X will not render a link preview.
The share image itself is `source/assets/share-card.png`, 1200×630.

### About `source/`

`source/index.html` will NOT work by double-clicking — browsers block ES modules on
`file://`. That is the bug the standalone build exists to solve. Serve it over HTTP
(`python -m http.server`) to develop against it directly.

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
38 binding attributes and 73 element ids. After an intentional change, re-record with
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
- **Twenty-four themes**, grouped in the picker (Core / Archive / Old hardware / Aesthetic /
  Uneasy / Design). Three of them are structural rather than palettes: Frutiger Aero is
  gloss and depth, Bauhaus flat is the deliberate absence of both, and Acid neo-brutalism
  is thick rules with unblurred offsets. Ten more carry a shape language rather than only a
  palette: The Matrix and Liminal space are square because a terminal and an empty institution
  both are, Emo is angular, DreamCore and TraumaCore are soft, Vaporwave and McBling are
  glossy and rounded, 80s workout is chunky, MTV is broadcast-rounded, and WeirdCore's corners
  deliberately disagree with each other. AOO, Paper and High contrast stay neutral so the
  others have something to be characterful against.
- **Shape is guarded, not eyeballed.** `check-themes.py` also measures geometry: it flags any
  element whose rendered corner curve reaches further in than its text does while text sits in
  the corner. That is the exact failure that shipped twice in Gyaru. Every one is audited rather than eyeballed: `check-themes.py` walks all of them
  and computes WCAG contrast for thirteen pairs that have actually broken before.
- **Base themes reworked.** Light became **Paper** — warm ground and dark ink, better for
  reading prose for hours than clinical grey. Neutral dark became **Midnight** — dim and
  desaturated for late writing. High contrast is deliberately untouched: it exists to be
  legible, not to have character. AOO got a polish, not a personality: stronger lines and a
  more legible muted tone. Stored theme values are unchanged, so existing preferences resolve.
- **Eight themes.** The original four (AOO, neutral dark, light, high contrast) plus Windows
  95, The Matrix, BIOS setup and Gyaru. Each keeps the four accent roles distinguishable, so
  the primary action never looks like the destructive one. Windows 95 and BIOS also carry
  structural rules — bevelled outset/inset borders and square corners respectively — because
  those looks are not palettes. Text on solid accents moved to an `--on-accent` token, since
  the old `var(--bg)` assumption breaks where a theme's background does not contrast with its
  accent.
- **A four-role type system.** The base stack used to be `"Segoe UI", Inter, system-ui` — one
  face for everything, naming the font most associated with generic interfaces. It is now four
  tokens: a condensed display face for headings, labels and tabs; a humanist face for body; a
  serif for prose; and a monospace for numerals, counts and identifiers, so data reads as data.
  Themes override the tokens rather than only `body`, so a terminal theme gets a terminal voice
  in its headings too. System faces only — the file still fetches nothing.
- **One orchestrated arrival.** The welcome screen reveals in a stagger — mark, heading, a rule
  sweeping out under it, then the four cards in sequence. One well-made moment at first open
  rather than motion scattered through a tool people write in for hours.
- **Atmosphere in the chrome.** Twelve themes layer gradients behind the interface. Deliberately
  never behind the manuscript, and never on a surface that carries text, so the contrast audit
  keeps its measurements.
- **Motion, restrained.** Panes rise slightly on switch, dialogs and the tour card scale in,
  status messages flash on change, and hover states settle over 120ms. Only colour, shadow,
  transform and opacity animate, so nothing triggers layout. The manuscript, works list and
  chapter strip never shift position. All of it is disabled under
  `prefers-reduced-motion: reduce`, verified with the browser flag rather than assumed.
- **Publishing is a moment, not a download.** Build used to validate and quietly drop a file.
  It now opens a sheet stating what is about to exist: namespace and that it is permanent,
  version, authors, works, chapters, words, the AOO version required, and the exact six paths
  the ZIP will contain. It also checks whether the `.aoopack.json` is current and says so
  plainly if it is not, because that is the last moment anyone will care.
- **The preview tab became the proof sheet.** Once the card rendered beside the manuscript, a
  whole tab showing the same card was redundant. It is now both widths the game renders at,
  side by side, where long titles and tag walls fail first.
- **Details became a work record.** It was three columns of form fields — the surface that
  most read as a mod utility, on the screen where a writer describes their work for an
  archive. It is now numbered rubrics: byline, rating and warnings, summary, tags, and *how
  the archive received it*. Rating is a row of marks you pick — G T M E N — rather than a
  dropdown. Tags are chips you collect by typing and pressing Enter, with an × to drop one,
  instead of one comma-separated string per category. The invented engagement numbers are
  named for what they are and set in monospace.

  The data path is deliberately untouched: every `data-bind` and `data-bind-list` input is
  still there, and the chips write through them. The exporter reads exactly what it did
  before — all 38 bindings intact through the restructure.
- **Write beside the preview.** A toggle in the Write heading opens the AOO work card next to
  the manuscript, updating as you type the body, the title, the tags. Seeing a fic render as an
  in-game card was previously tab four of five; it is now the thing you write against. The
  panel folds away below 1300px rather than squeezing the manuscript, and the choice persists.
- **A standing answer to "can I ship this".** A chip beside the build button reads *Ready to
  build* or *N to fix* and jumps to Validation when clicked. Publishability was previously
  something you had to go and look up.
- **The shell reads as a console.** The masthead leads with the collection you are building
  rather than the tool's own name, which is now a monospace footnote under it. A HUD frame
  brackets the working area. Tabs are numbered `01`–`05` so they read as a sequence rather
  than five peers, and the rail sections are numbered to match — both via CSS counters, so no
  markup carries the numbers. Registration ticks mark the corner of the working panels. All
  of it is structure and type rather than colour, so it holds across every theme; the themes
  with their own strong language (Windows 95, BIOS, Nokia, Bauhaus, brutalism) opt out of the
  frame rather than fight it.
- **Boot sequence.** The tool powers on rather than appearing: a CRT line opens into the
  field, the mark resolves out of a channel-split glitch inside a spinning reticle, four POST
  lines report the framework contract, schema, library and *network — not required*, and a
  fill bar wipes the screen away. Purely cosmetic, follows the theme tokens so a Windows 95
  boot looks like one, skippable with any key or click, and skipped entirely under reduced
  motion. It then **waits**: once the bar completes, a pulsing prompt with a blinking caret
  appears and the sequence holds until a key or click, rather than moving on by itself, so the
  POST lines are actually readable.
- **Welcome screen.** Clicking the logo reopens it at any time; Escape closes it. First run opens a full screen offering four real paths rather than a
  list of steps: start blank, take the tour, open one of the four worked examples, or import
  a saved `.aoopack.json`. It also states the thing a writer most needs to know up front —
  that the browser is not a backup. The mark is inline SVG using `currentColor`, so it
  follows all eight themes and costs no file size; the whole screen added about 3 KB.
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
