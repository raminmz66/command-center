# Script Authoring UI

**Date:** 2026-07-28  
**Phase:** 4 — Framework Release (reordered; Steps 25–29 parked)  
**Cycle:** Script authoring (create / edit / delete)  
**Status:** Approved for planning

## Goal

Let users create, edit, and delete Command Center scripts entirely in the app — metadata (name, icon, description, category, color, terminal, confirm) plus script body — without hand-editing `# KEY=` files.

## Visual reference (authoritative)

Soft GNOME mockups (expected final look):

**[`docs/superpowers/visuals/2026-07-28-script-authoring.html`](../visuals/2026-07-28-script-authoring.html)**

| Screen | Contents |
|--------|----------|
| 1 | Edit commands mode — header **Edit** (gold) + **+**; card ✎ / 🗑; launch-paused banner |
| 2 | New command — full-window cream form |
| 3 | Edit command — same form, prefilled |
| 4 | Delete confirm — dim overlay, cream modal, red Delete |

Tokens: accent `#f6c32a`, cream `#fff8e7`, danger `#c01c28`. Match layout density and chrome of those screens during implementation and screenshot QA.

Related exploration (access / placement comparisons, not the locked visual):

- [`docs/superpowers/visuals/2026-07-28-authoring-access-options.html`](../visuals/2026-07-28-authoring-access-options.html)
- [`docs/superpowers/visuals/2026-07-28-authoring-editor-placement.html`](../visuals/2026-07-28-authoring-editor-placement.html)

## Decisions

| Topic | Choice |
|-------|--------|
| Scope | Create + edit + delete; full metadata + script body |
| Access | **B** — Header **+** create; **Edit** mode for ✎ / 🗑 on cards |
| Icon | **B** — Curated symbolic grid + optional custom name |
| Form placement | **C** — Full-window swap (hide grid; Back returns) |
| Delete | **A** — Confirm dialog before removing file |
| Architecture | **2** — `scriptio.py` + `authoring.py` + `menu.py` stack |
| Filename | Slug from Name on create; keep path on edit (no rename v1) |
| Favorites vs Edit | Mutually exclusive modes |

## In scope

- Header **+** → New command form
- Header **Edit** toggle → edit-commands mode (gold active); banner; card action buttons; no launch
- ✎ → Edit form (prefilled); 🗑 → delete confirm → remove `.sh` + prune favorites
- Form fields: Name, Description, Category, Icon (grid + custom), Color (none/r/g/b/o/p/y), Terminal, Confirm, Script body
- Save writes `#!/bin/bash`, `# KEY=` metadata, body; `chmod +x`; return to launcher and reload
- Dirty Back/Cancel → discard confirm when form changed
- Soft GNOME CSS aligned with visual reference
- Unit tests for `scriptio` (round-trip, slug, unique path)
- Preserve: search focus fix, Soft GNOME cards, categories, favorites Apply flow, confirm popover

## Out of scope

- File rename on edit
- Import external script wizard
- Syntax highlighting / run-from-form
- Packaging (Step 32), generator/templates (30–31)
- Steps 25–29 (execution engine, status, keyboard, notifications, tray)

## Architecture

```
menu.py
  Gtk.Stack: launcher | authoring
       │
       ├─ Edit mode: ✎ / 🗑 / + ──► authoring form / delete dialog
       │
authoring.py  — form widget, validation, dirty tracking
       │
scriptio.py   — read_script / write_script / slug / unique_path / delete
       │
scripts/*.sh  — still the source of truth (# NAME= … + body)
```

Grid continues to use `metadata.read_metadata` for listing. `scriptio` emits headers compatible with that parser.

## Components

### `scriptio.py`

- `read_script(path) -> dict` with `meta` (same keys as metadata) + `body` (str, no shebang/meta lines)
- `write_script(path, meta, body) -> None` — shebang, metadata lines only for set fields, body; chmod `0o755`
- `slug_filename(name) -> str` — e.g. `My Backup` → `my-backup.sh`
- `unique_path(directory, slug) -> str` — append `-2`, `-3`, … before `.sh` if needed
- `delete_script(path) -> None`

### `authoring.py`

- Builds form UI matching visual reference screens 2–3
- Curated icon list (~12–20 `*-symbolic` names) + custom entry
- Color swatches; Terminal / Confirm switches
- `load_from(path|None)`, `collect() -> (meta, body)`, validation messages
- Signals/callbacks: save, cancel/back

### `menu.py`

- `Gtk.Stack` between launcher content and authoring view
- `edit_commands` mode (exclusive with `edit_favorites`)
- Header: Edit commands button + **+** button
- Wire card actions; delete `Gtk.MessageDialog` or custom cream dialog matching screen 4
- After save/delete: reload commands, show launcher, exit authoring

### `widgets.py` / CSS

- Optional: expose edit/delete buttons on cards when `edit_commands`
- Classes: `.cc-edit-commands`, `.cc-authoring-*`, `.cc-delete-dialog`, card `.cc-card-edit` / `.cc-card-delete`, banner `.cc-edit-banner`

## Behavior details

1. **Create:** slug from Name; collision → `name-2.sh`; empty Name or empty body blocks Save.
2. **Edit:** rewrite same path; Name change does not rename file.
3. **Delete:** confirm copy names command + basename; on success remove from favorites JSON if present; refresh.
4. **Edit mode:** primary card click does nothing (or only hits action buttons); confirm popover must not open for launch.
5. **Modes:** entering Edit commands exits Favorites edit (and vice versa) without applying pending favorites — or Apply first if pending; prefer: exit favorites edit discarding pending unless Apply was pressed (same as leaving without Apply today). Spec: entering Edit commands while Favorites edit is active **discards pending favorites** and exits favorites edit (document in UI via mode exclusivity).

## Testing

- Unit: `framework/test_scriptio.py` — round-trip, slug, unique_path, chmod bit when possible
- Manual / QA: screenshot loop against `authoring-visual-design.html` screens 1–4

## Success criteria

- User can add a command from the UI and see a new card after Save
- User can edit metadata/body and see changes after reload
- User can delete with confirm; file gone; favorites cleaned
- Visual QA matches the reference HTML within Soft GNOME / GTK limits
