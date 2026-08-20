# Publishing a fic collection for Archive of Our Overwrites

This is the guide for people writing and releasing fic collections. You need no coding
knowledge. The AOO Creator builds the mod for you.

A **collection** is one mod. It can hold as many authors, works and chapters as you like, and
it publishes as a single ZIP on Nexus. Players install it alongside Archive of Our Overwrites,
and your fics appear in the in-world Archive and Shard Market.

---

## Before you write anything

Two decisions are permanent. Everything else can be changed later.

### 1. The namespace

Collection settings (the gear beside **Collection**) holds a **namespace**: letters, numbers
and underscores, no spaces. It is the internal name of your mod.

**Never change it after your first public release.** It determines where your files install
and how the game identifies your pack. Changing it turns an update into a separate, competing
mod, and players end up with both.

Pick something specific to your collection, not generic: `AfterlifeOneShots`, not `FicPack`.

### 2. Your project file

**Save project** writes a `.aoopack.json` file. Keep it forever, backed up.

Every author, work, chapter and comment carries a hidden permanent ID. Player saves key on
those IDs: which chapters they recovered, what they propped, stashed and followed. To
publish version 1.1, you **import your saved project file**, edit it, and rebuild.

If you rebuild a collection from scratch instead, every ID is regenerated. To the game it is
an entirely new collection, and every reader loses everything they had recovered from the old
one. There is no way to recover from this after release.

The tool autosaves to your browser, but that is convenience, not backup. Clearing site data,
switching browsers, or using another computer loses it. The `.aoopack.json` file is the real
copy.

### Working on more than one collection

The tool keeps a library. The switcher at the top of the left rail moves between collections,
**New** starts another, **Delete** removes one from your browser. Each keeps its own works,
authors and settings, and the library survives closing the browser.

This is convenience, not backup. The rule above still holds. Save a `.aoopack.json` for every
collection you care about.

---

## The workflow

1. **Collection settings**: name, namespace, version, your creator name, licence.
2. **Authors**: add everyone who "wrote" the fics. Pseuds are in-world handles, up to 24
   characters. Mark each Active or Inactive (see below).
3. **Write**: add chapters and write. Word count is counted for you.
4. **Details**: rating, archive warning, category, tags, summary for each work.
5. **AOO preview**: check how the work card looks in-game, especially long titles and many tags.
6. **Validation**: fix every error. Warnings are advice you can ignore.
7. **Save project**: write your `.aoopack.json`.
8. **Validate & build ZIP**: produces the mod.

---

## Active and inactive authors

This decides whether a work's chapters unlock over time.

| | Inactive author | Active author |
|---|---|---|
| Complete work | All chapters available immediately | Same; timing is ignored |
| Work in progress | **Not allowed** | Chapter 1 available immediately, each later chapter unlocks after the release interval |

The release interval is a minimum of **3 in-game days**. AOO owns the timer and the
follower alerts. You do not write any of that.

An incomplete work must use an Active author. If you mark a work as a WIP, the release fields
appear in Details automatically.

---

## Archived comments

You can ship reader comments as part of a work, so it feels like an archive with history.

They are only valid on a **complete work by an inactive author**: the fiction being that the
author finished, moved on, and the comments are what's left behind. An ongoing work by an
active author cannot have them.

Each comment needs a user handle, body text, and which chapter it attaches to. Your Comments
stat cannot be lower than the number of comments you actually included.

---

## Fields and limits

| Field | Limit |
|---|---|
| Author pseud | 24 characters |
| Work title | 120 characters |
| Chapter title | 120 characters |
| Summary | 140 characters |
| Single tag | 80 characters |
| Tags per work | 100 total, across all four tag fields |
| Chapter price | 1 eddie or more; leaving it at zero is a warning and exports as 300 |
| Release interval | at least 3 in-game days |

**Rating**: General · Teen And Up · Mature · Explicit · Not Rated
**Category**: Gen · F/F · F/M · M/M · Multi · Other
**Archive warning**: No Archive Warnings Apply · Creator Chose Not To Use Archive Warnings ·
Graphic Depictions Of Violence · Major Character Death · Underage · Rape/Non-Con

Label your rating honestly. The game itself is Mature/Explicit, so all ratings are welcome.

Every chapter has an eddie price. That is how players recover it from the Shard Market. You
set the price; you do not create vendors, items or icons.

---

## What the ZIP contains

Everything installs under one folder named for your namespace:

    r6/scripts/<Namespace>/<Namespace>.Content.reds        your works, as game data
    r6/scripts/<Namespace>/<Namespace>.Localization.reds   your text
    r6/scripts/<Namespace>/pack.aoopack.json               your project source
    r6/scripts/<Namespace>/manifest.json                   pack metadata
    r6/scripts/<Namespace>/README.txt                      readme for players
    r6/scripts/<Namespace>/VERSION                         your version number

Because it is all namespaced, any number of fic packs coexist safely.

---

## Publishing to Nexus

Upload the ZIP as a normal Cyberpunk 2077 mod. Players install it with Vortex
like any other mod and deploy.

### The Creator writes your mod page for you

Press **Validate & build ZIP** and open **Your Nexus page**. The tool has every
fact a mod page needs, so it writes one: the description, every work with its
rating and tags, the word and chapter counts, the AOO version readers need, and
install and update notes. Press **Copy the page** and paste it into the Nexus
description box.

It is a starting point, not a template you must keep. Edit it however you like.

Read the notes above the text before you post. The important one:

- **If any work is rated Explicit, the tool tells you to tick "Contains adult
  content" when uploading.** Nexus can remove a mod that does not. The tool
  knows your ratings, so it checks for you.
- Square brackets in a title or summary are left exactly as you wrote them, but
  Nexus may read them as formatting. The tool flags it so you can check the
  preview.

Word counts on the page come from the prose you actually wrote, not from a
stored number, so they stay honest even in a collection you just imported.

---

## Publishing an update

### The Creator checks the update for you

Import the `.aoopack.json` from your last release, make your changes, then press
**Validate & build ZIP**. Above the Nexus page you will see what changed since
that file, split into two lists.

The red list is the one to read. Those changes cost your readers something:

| What | What it costs a reader |
|---|---|
| A work removed | It disappears from the archive for anyone who recovered it. |
| A chapter removed | They lose it, and the eddies they spent on it. |
| The namespace changed | The game sees a different mod. Nothing carries over, and they end up with two. |
| The version unchanged | Mod managers cannot tell the new file from the old one. |
| An author removed | Their works lose their byline. |

The quiet list underneath is everything else: new works, new chapters, retitles,
rating changes. Those are safe. Readers keep what they had.

If you did not import a file, the panel says so. That is a first release, and
there is nothing yet that could break.

This is why the guide keeps insisting you save a `.aoopack.json` for every
release. Without it there is no way to know what an update is about to do.

### Doing it by hand

1. **Import project**: load your saved `.aoopack.json`.
2. Make your changes. Add chapters, fix typos, add works.
3. Bump the **version** in Collection settings.
4. Save the project file again, replacing your copy.
5. Build the ZIP and upload it as an update.

Do not change the namespace. Do not start from a blank collection.

---

## Taking something back

Deleting a work, chapter, author or comment is reversible. The two arrows at the
left of the toolbar undo and redo, and they dim when there is nothing to take
back, so you can see at a glance whether there is a way out.

**Ctrl+Z** works too, but only outside a text box. Inside the manuscript or any
other field it belongs to your browser, undoing your typing the way it does
everywhere else. That line matters: taking back a sentence and taking back a
deleted chapter are different actions, and one keystroke should not do both.

**Ctrl+Y** redoes. Both keep about forty steps.

Autosave still applies. Undo is for the last thing you did, not a way back to
last week: a `.aoopack.json` saved to disk is the only real safety net.

---

## When something is wrong

**Validation shows errors.** Each one names the work and what to fix. Errors block the build
on purpose: they are the things that would break in-game.

**The build button does nothing.** You have validation errors. The tool switches you to the
Validation tab and says how many.

**Nothing appears in-game.** Check `r6\logs\redscript_rCURRENT.log` after launching. AOO logs
a specific warning when it rejects a malformed work. Confirm AOO itself is installed and that
its version is at least the one your pack requires.

**You lost your `.aoopack.json`.** If the pack is not yet released, rebuild it and move on. If
it *is* released, do not rebuild and re-upload under the same namespace. Ask before doing
anything, because a mismatched rebuild is what breaks readers' libraries.

---

## What the tool never does

It does not upload your fic anywhere. Everything happens in your browser, on your machine.
Nothing is sent to a server, and there is no account.
