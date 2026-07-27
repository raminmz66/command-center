# Step 23 — Favorites

**Date:** 2026-07-27  
**Phase:** 1 — UI Professionalization  
**Cycle:** Step 23 — Favorites  
**Status:** Approved for planning

## Goal

Add a Soft GNOME **Favorites** strip above the main card grid for quick access. Favorites are toggled in-app (edit mode), persisted to a JSON config, and remain visible in the main grid as well. The Favorites strip ignores category and search filters.

## Decisions

| Topic | Choice |
|-------|--------|
| Source of truth | **B** — in-app persistence (config file); no `# FAVORITE=` for v1 |
| Layout | **A** — separate Favorites section above the main grid |
| Duplication | **A** — favorited commands appear in Favorites **and** in the main grid |
| Toggle UX | **C** — edit mode; in edit mode, **clicking the card toggles favorite** (star is display-only); no launch until edit ends |
| Filters vs Favorites | **A** — Favorites strip always shows all favorites (ignores category + search) |
| Implementation | **1** — `favorites.py` + JSON under `~/.config/command-center/` |

## In scope

- `framework/favorites.py`: load / save / `is_favorite` / `toggle_favorite`
- Persist ordered list of script **basenames** in `~/.config/command-center/favorites.json`
- HeaderBar control to enter/exit **edit favorites** mode
- Favorites section (label + card row) between category chips and main grid
- Hide Favorites section when the list is empty
- In edit mode: card click toggles favorite; ★/☆ is visual only; do not run commands
- In normal mode: card click launches (unchanged)
- Main grid still applies category AND search; favorites also appear there when they match
- Soft GNOME CSS for section, edit control, star indicator (gold `#f6c32a` aligned with active chips)
- Preserve search focus fix, Soft GNOME cards, hover tint, `# COLOR=`, category chips

## Out of scope

- `# FAVORITE=` script metadata
- Drag-reorder (order = toggle order: newly favorited **append**)
- Cross-machine sync
- A Favorites category chip
- Pausing search / category while editing (filters still apply to main grid only)

## Architecture

```
~/.config/command-center/favorites.json
        ↑↓
favorites.py  — load / save / is_favorite / toggle_favorite
        ↑
menu.py  — edit mode, Favorites strip, dual render, header toggle
        ↓
CommandCard (widgets.py) — optional star display when edit_mode / is_favorite
```

## Components

### `favorites.py`

- Config path: `~/.config/command-center/favorites.json` (create parent dirs on save)
- Schema: JSON array of strings (basenames), e.g. `["conky.sh", "test-terminal.sh"]`
- API:
  - `load_favorites() -> list[str]` — missing/corrupt → `[]`
  - `save_favorites(names: list[str]) -> None`
  - `is_favorite(basename: str) -> bool`
  - `toggle_favorite(basename: str) -> bool` — returns new state; appends when adding; removes when unfavoriting; persists immediately
- Optionally prune basenames that no longer exist on successful save after render/discover (recommended: prune unknown ids on save after toggle or on load+discover merge in menu)

### `menu.py`

- State: `self.favorites` (list), `self.edit_favorites` (bool, default False)
- HeaderBar: toggle button (star icon / “Done”) to flip `edit_favorites` and re-render
- Layout: chips → `favorites_box` (section label + favorites grid/box) → main `grid`
- `render_commands`:
  - Rebuild Favorites strip from `self.favorites` ∩ discovered commands (ignore category/search)
  - Rebuild main grid with `matches_filters` as today (favorites still included when they match)
- Click wiring:
  - **Normal:** card → `run_command` (existing)
  - **Edit:** card → `toggle_favorite(basename)` then refresh; do **not** call launcher
- Empty favorites → hide `favorites_box`
- Refresh / rediscover: reload favorites from disk (or keep in-memory already saved); rebuild both sections
- Preserve search caret restore; use section/`grid.show_all()` only — never window `show_all()` on filter/favorite rebuilds

### `widgets.py`

- Support showing a star indicator (★ favorited / ☆ not, in edit mode) without intercepting clicks as a separate control — whole card remains the click target
- Pass flags from menu (e.g. `edit_mode`, `favorited`) when constructing cards

### `style.css`

- `.cc-favorites-section` / label
- Edit-mode header button styling
- `.cc-favorite-star` — gold `#f6c32a` when favorited; muted when not

### Unchanged

- `launcher.py`, `metadata.py`, category/`textutil` filter helpers (reuse as-is for main grid)

## Data flow

1. Startup / refresh → discover scripts; `load_favorites()`
2. Render Favorites strip (all favorited that still exist) + filtered main grid
3. User enters edit mode → re-render with stars; card clicks toggle + save
4. User exits edit mode → re-render without stars; card clicks launch again

## Error handling

- Missing or invalid JSON → empty favorites, no crash
- Basename in JSON but script gone → skip in UI; drop on next save/prune
- Config dir not writable → toggle fails gracefully (keep prior in-memory state; optional stderr/log — do not crash UI)

## Verification

**Automated**

- `favorites.py`: load empty/missing; round-trip save; toggle add/remove; corrupt JSON → `[]`

**Manual**

1. Edit → click cards → stars update; Done → Favorites section shows them  
2. Favorited cards still appear in main grid when filters match  
3. Category/search do **not** shrink the Favorites strip  
4. Empty favorites → section hidden  
5. Multi-char search, Soft GNOME, chips, `# COLOR=` still work  
6. In edit mode, clicking a card does **not** run the script  

**Done when:** edit/persist/section behavior matches decisions; unit tests pass; no Soft GNOME/search/category regressions.

## Risks

- Edit vs launch mode confusion — make HeaderBar edit state obvious (“Done” when editing)
- Duplicate cards (Favorites + main) may feel redundant with few scripts — accepted per decision A
- Config path hardcoding vs XDG — use `GLib.get_user_config_dir()` or `pathlib` + `~/.config` consistently with desktop norms
