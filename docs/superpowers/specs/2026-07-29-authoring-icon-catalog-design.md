# Authoring icon catalog (emoji on cards)

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release (reordered)  
**Cycle:** Authoring icon catalog  
**Status:** Approved for planning  
**Parent:** [2026-07-28-script-authoring-design.md](2026-07-28-script-authoring-design.md)

## Goal

Expand the authoring icon picker to **36 emoji**, drop the custom icon-name field, and make command cards show **exactly the same glyph** as the picker after Save. Migrate existing sample scripts to emoji icons. No GNOME symbolic icon path.

## Decisions

| Topic | Choice |
|-------|--------|
| Card vs picker | **Identical emoji** on both |
| Metadata | `# ICON=<emoji>` (single character / emoji sequence as text) |
| Catalog size | **~36** in a **6×6** flat glyph grid |
| Custom icon name | **Removed** |
| Legacy symbolic | **None** — cards always render emoji from `# ICON=` |
| Sample scripts | Update `conky.sh`, `test-terminal.sh`, `update-lockdown-status.sh` |

## In scope

- Replace curated `(symbolic, emoji)` pairs with a list of **36 emoji** in `authoring.py`
- Remove “Custom icon name…” entry and related wiring
- Form preview = selected emoji only
- Save writes `# ICON=<emoji>` via existing `scriptio.write_script`
- `CommandCard`: render emoji with `Gtk.Label` (same glyphs as picker); remove theme `Gtk.Image` icon lookup for command icons
- Update the three scripts under `scripts/` to emoji `# ICON=`
- Soft GNOME: keep flat glyph tiles (no chunky buttons); gold selection chrome unchanged in spirit
- Preserve authoring create/edit/delete, favorites, confirm, categories, search focus fix

## Out of scope

- Icon search / categories inside the picker
- Custom uploaded images
- Reintroducing GNOME symbolic icons on cards
- Packaging / Steps 25–31

## Catalog (36)

Picker order (6 columns × 6 rows). Exact codepoints may be adjusted in implementation if a glyph is missing on the target font; visual set must stay Soft GNOME–friendly and distinct:

```
🖥 💾 🔒 🌐 ⚙ 🗂
🛡 📡 🧹 ⏱ 📦 🔧
🗒 🚀 🔑 ☁ 🔊 🔋
🏠 ⭐ 🔥 💡 🗑 📁
🔄 🛠 📊 🖧 🧩 🎮
📝 🛰 🔐 💻 🧭 ⚡
```

Suggested script mapping after migration:

| Script | Emoji |
|--------|-------|
| `conky.sh` | 🖥 |
| `test-terminal.sh` | 💻 |
| `update-lockdown-status.sh` | 🔒 |

## Architecture

```
authoring.py  — ICON_CATALOG[36], picker grid, preview, no custom entry
       │
       ▼
scriptio.write_script  — # ICON=<emoji>
       │
       ▼
scripts/*.sh
       │
metadata.read_metadata / scriptio.read_script  — meta["icon"] = emoji string
       │
       ▼
widgets.CommandCard  — Gtk.Label(emoji) as command glyph
```

## Components

### `authoring.py`

- `ICON_CATALOG`: list of 36 emoji strings  
- Grid: 6×6 `EventBox` + label glyphs (existing flat style)  
- Remove `custom_icon_entry` and `_on_custom_icon`  
- `get_values()` / `load()` use emoji only  

### `widgets.py`

- Build command glyph from `meta["icon"]` as a centered `Gtk.Label` with class `command-icon` (and existing color classes on the label when `# COLOR=` is set)  
- Do not call `Gtk.IconTheme` / `set_from_icon_name` for command cards  

### `scripts/*.sh`

- Set `# ICON=` to the table above (or catalog equivalents)

## Behavior details

1. Selecting a glyph updates preview and saved `ICON` to that exact string.  
2. After Save → reload, the card glyph must match the picker glyph character-for-character.  
3. Empty/missing `ICON` falls back to a default catalog emoji (e.g. 🔧), not a theme icon.  
4. Color tint (`# COLOR=`) applies to the emoji label via existing `command-icon-*` CSS where feasible (GTK emoji tinting may be limited; do not block ship if OS ignores color on emoji).

## Testing

- Unit (light): catalog length == 36; optional round-trip `write_script` / `read_script` preserves emoji in `ICON`  
- Manual: pick each of several glyphs → Save → card shows the same glyph; edit existing migrated scripts  

## Success criteria

- Picker has 36 flat emoji; no custom-name field  
- Card icon === picker selection after Save  
- Three sample scripts use emoji `# ICON=`  
- No symbolic icon rendering path remains on command cards  
