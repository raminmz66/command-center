# Empty-state that teaches

**Date:** 2026-08-08  
**Phase:** Polish backlog  
**Cycle:** Empty-state that teaches  
**Status:** Approved  
**Parent:** PROJECT_ROADMAP active backlog item 3

## Goal

When the scripts library is truly empty, show a centered teaching CTA that opens Create command — not a blank content area.

## Decisions

| Topic | Choice |
|-------|--------|
| When | **True empty only** — zero `.sh` files after discover |
| Filter / search empty | **Out of scope** — no special “no matches” state |
| Layout | **A · Centered hero** — hide category chips |
| Primary action | **Create command** → `show_authoring(None)` (same as header `+`) |
| Restore demos | **Out of scope** |
| Visual | Title + short body + yellow primary button; no icon / dashed panel |

## Behavior

### Show

- After `discover_commands`, if `len(self.commands) == 0`:
  - Hide category chip bar
  - Hide favorites section and “All commands” label (already empty)
  - Hide (or leave empty) the command grid
  - Show centered empty-state: title, body, CTA button

### Hide

- As soon as any command exists (after create/save/refresh/seed), hide empty-state and restore normal chips + cards.

### CTA

- Label: **Create command**
- On click: `self.show_authoring(None)`
- Header `+` remains available

### Copy

| Element | Text |
|---------|------|
| Title | No commands yet |
| Body | Create your first command to fill this launcher. |
| Button | Create command |

## In scope

- Empty-state UI in `menu.py` (+ small helper/module if useful)
- CSS under Soft GNOME (yellow primary aligned with existing accent buttons)
- Hide chips when empty
- Unit test for empty-library predicate / copy constants as needed
- QA screenshot with empty XDG scripts dir (tombstone demos so seed does not refill)
- Update `STATUS.md`

## Out of scope

- Search/filter “no results” empty state
- Restore sample commands
- Reorder favorites
- Changing seed / tombstone behavior beyond using it for QA

## Success

1. Zero scripts → centered CTA visible; chips hidden.  
2. CTA opens authoring (new command).  
3. After saving a command, empty-state gone; chips/cards normal.  
4. Non-empty library never shows empty-state.  
5. Screenshot QA confirms layout matches Option A.
