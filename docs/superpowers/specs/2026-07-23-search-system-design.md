# Step 21 — Search System

**Date:** 2026-07-23  
**Phase:** 1 — UI Professionalization  
**Cycle:** Step 21 — Search system  
**Status:** Approved for planning

## Goal

Add a Soft GNOME HeaderBar search that instantly filters command cards by **name + description**, with keyboard focus on open and via **`Ctrl+F` / `/`**.

## Decisions

| Topic | Choice |
|-------|--------|
| Placement | **B** — search in the HeaderBar |
| Match fields | **B** — name + description |
| Keyboard focus | **B** — focus on open; also `Ctrl+F` and `/` |
| Implementation | **1** — filter in `menu.py` + pure `matches_query` helper |

## In scope

- `Gtk.SearchEntry` in the HeaderBar with Soft GNOME styling (`.cc-search-entry`)
- Case-insensitive substring match on `meta["name"]` and `meta["desc"]`
- Empty query → show all commands
- No matches → empty grid (optional short “No commands” label allowed)
- Escape clears the search query (focus stays in the entry)
- Pure helper `matches_query(meta, query) -> bool` with unit tests
- Preserve Soft GNOME cards, hover icon tint, and `# COLOR=` behavior
- Folder / refresh / run behavior unchanged

## Out of scope

- Categories / favorites (Steps 22–23)
- Fuzzy ranking, search history, recent queries
- Global desktop hotkey to open Command Center
- Filtering by category or filename

## Architecture

```
textutil.matches_query(meta, query)
        ↑
menu.py  — SearchEntry + filter + rebuild grid
        ↓
CommandCard (unchanged)
```

Appearance for the entry stays in `style.css`. Matching logic is pure Python (no GTK) so it is unit-testable.

## Components

### `textutil.py`

Add:

```python
def matches_query(meta, query) -> bool
```

Rules:

- If `query` is empty or whitespace-only → `True`
- Compare with casefold (or lower) substring
- Match if query appears in `name` **or** `desc` (missing desc treated as `""`)
- Do not raise on normal dict-like meta

### `menu.py`

- Add `Gtk.SearchEntry` to the HeaderBar (expand as needed; folder + refresh remain `pack_start`)
- Keep a list of loaded `(path, meta)` entries when discovering scripts
- On `search-changed` (or equivalent): filter with `matches_query`, clear grid, attach matching cards (same 3-column layout)
- On window show / after construction: grab focus on the search entry
- Accelerators: `Ctrl+F` and `/` focus the search entry
- Escape: clear the search text
- Refresh reloads scripts and re-applies the current query

### `style.css`

- Style `.cc-search-entry` to fit Soft GNOME (rounded, quiet border, readable placeholder)

### Unchanged

- `widgets.py`, `launcher.py`, `metadata.py` (search uses existing `name` / `desc` only)

## Data flow

1. Discover `.sh` scripts → `(path, meta)` list  
2. User types query → `matches_query` for each meta  
3. Rebuild grid with matching `CommandCard`s → click still calls `run_command`

## Error handling

- Empty scripts folder → empty grid (existing behavior)
- Invalid / empty query → show all
- No matches → empty grid (optional label)
- Missing `desc` key → treat as empty string

## Verification

**Automated**

- Unit tests for `matches_query`: empty query, name hit, description hit, miss, case-insensitive

**Manual**

1. Open app → search focused; type `con` → Conky only  
2. Query that only matches description still shows the card  
3. Escape / clear → all cards return  
4. `Ctrl+F` and `/` refocus search  
5. Soft GNOME + `# COLOR=` + folder/refresh/run still work  

**Done when:** HeaderBar search filters instantly by name+desc; focus and shortcuts work; tests pass; no Soft GNOME regressions.

## Risks

- HeaderBar title vs search layout may need a custom title widget so search has room without clipping on small widths
- `/` accelerator must not fire when another text field is focused later (only search exists in Step 21)
