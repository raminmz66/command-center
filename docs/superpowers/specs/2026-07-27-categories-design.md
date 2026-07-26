# Step 22 — Categories

**Date:** 2026-07-27  
**Phase:** 1 — UI Professionalization  
**Cycle:** Step 22 — Categories  
**Status:** Approved for planning

## Goal

Add Soft GNOME **category filter chips** under the HeaderBar. Chips are built from script `# CATEGORY=` metadata (plus **All**), ordered with a preferred list then extras A–Z. Filtering is **AND** with the existing search query.

## Decisions

| Topic | Choice |
|-------|--------|
| UI pattern | **A** — horizontal filter chips |
| Chip source | **C** — dynamic from scripts; preferred order for common names, then extras alphabetically |
| Search interaction | **A** — category + search both apply (AND) |
| Implementation | **1** — chips in `menu.py` + filter helpers in `textutil.py` |

## In scope

- Chip row under HeaderBar (above the card grid): **All** + discovered categories
- Preferred order: Desktop, System, Network, Maintenance, Security, General — then any other categories A–Z
- Default selection: **All**
- `matches_filters(meta, query, category)` combining `matches_query` with category equality (All → no category constraint)
- Soft GNOME CSS for idle/active chips (`.cc-category-chip`)
- Rebuild chips on script discover/refresh; if selected category disappears, fall back to **All**
- Tag sample scripts with `# CATEGORY=` so chips are visible in the demo
- Preserve search focus fix, Soft GNOME cards, hover tint, `# COLOR=`

## Out of scope

- Favorites (Step 23)
- Sidebar or stacked-section layouts
- In-app category renaming / editing
- Fixed empty chips for categories with no scripts
- Fuzzy category matching

## Architecture

```
textutil.ordered_categories(...)
textutil.matches_filters(meta, query, category)
        ↑
menu.py  — chip row + selected category + render_commands
        ↓
CommandCard (unchanged)
```

`# CATEGORY=` already parsed in `metadata.py` (default `General`).

## Components

### `textutil.py`

Add:

```python
PREFERRED_CATEGORIES = (
    "Desktop", "System", "Network", "Maintenance", "Security", "General",
)

def ordered_categories(categories) -> list[str]:
    """Unique categories: preferred order first, then remaining A–Z (casefold)."""

def matches_filters(meta, query, category) -> bool:
    """True if matches_query(meta, query) and (category is All/empty or equals meta category)."""
```

Category compare: case-insensitive trim; missing/`""` meta category treated as `General`.

### `menu.py`

- Add a horizontal chip container between HeaderBar content and the grid (e.g. `Gtk.Box` with wrap via `Gtk.FlowBox` if needed)
- On `discover_commands`, collect categories → `ordered_categories` → rebuild chip buttons
- Each chip is a toggle/button; selecting one deselects others (radio behavior); **All** is default
- Store `self.selected_category` (string; `"All"` for no filter)
- `render_commands` filters with `matches_filters(meta, query, self.selected_category)`
- Keep existing search focus restoration when rebuilding the grid
- Refresh rediscovers and rebuilds chips; invalid selection → **All**

### `style.css`

- `.cc-category-chip` — quiet border, rounded pill/chip
- `.cc-category-chip:checked` / `.cc-category-chip.active` — Adwaita blue fill (`#3584e4`), white label

### Sample scripts

Set distinct categories on existing demos, e.g.:

- Conky → `Desktop`
- Test Terminal → `System` (or Maintenance)
- Lockdown → `Security`

### Unchanged

- `widgets.py`, `launcher.py`, `metadata.py` (parser already supports `CATEGORY`)

## Data flow

1. Discover scripts → `(path, meta)` + category set  
2. Build ordered chips; selection defaults to All  
3. User picks chip and/or types search → `matches_filters` → rebuild grid  

## Error handling

- No scripts → only **All** chip (or empty chip row + empty grid)
- Unknown / empty category on a script → treat as `General`
- Selected category removed after refresh → select **All**
- Empty search + All → show everything

## Verification

**Automated**

- `ordered_categories`: preferred order, extras sorted, uniqueness
- `matches_filters`: All+query, category only, AND miss, case-insensitive category

**Manual**

1. Chips show All + script categories in preferred order  
2. Select a category → only matching cards  
3. Search within a category (AND)  
4. Refresh with category gone → falls back to All  
5. Search multi-char typing, Soft GNOME, `# COLOR=` still work  

**Done when:** chips filter with search correctly; tests pass; no Soft GNOME/search regressions.

## Risks

- Chip overflow on narrow windows — use wrapping `FlowBox` or horizontal scroll if needed
- Toggle styling varies by GTK theme — prefer explicit CSS classes over relying on theme toggles alone
