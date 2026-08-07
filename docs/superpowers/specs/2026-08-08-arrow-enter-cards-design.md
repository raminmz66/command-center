# Arrow + Enter on cards

**Date:** 2026-08-08  
**Phase:** Polish backlog  
**Cycle:** 1 — Arrow + Enter on cards  
**Status:** Approved  
**Parent:** PROJECT_ROADMAP active backlog item 1

## Goal

Keyboard-navigate visible command cards with arrow keys while search keeps the caret; Enter runs the highlighted card like a click.

## Decisions

| Topic | Choice |
|-------|--------|
| Focus model | **Search keeps caret**; arrows move a highlight ring only |
| First highlight | **Only after** ↓/↑/←/→ — nothing highlighted until then |
| Card order | **One sequence:** favorites (if visible) then main grid |
| Enter | **Run** highlighted card (same path as click, including confirm popover) |
| Esc | **Clear highlight first**, then existing ladder (dismiss confirm → clear search → close) |
| Implementation | Index + CSS class `keyboard-focus` on `CommandCard` |

## Behavior

### Navigation

- Visible launchable cards form a flat list: favorites strip cards, then main grid cards (same filter/category as UI).
- Arrow keys (handled while search focused, and when window handles keys): move `highlight_index`.
- First arrow with no highlight: ↓/→ → index `0`; ↑/← → index `n-1` (if `n>0`).
- ←/→: ±1; ↑/↓: ±`columns` (default 3); clamp to `[0, n-1]`.
- Wrap: **none** (stop at ends).
- Rebuild/filter/category change / `render_commands`: clear highlight.
- `edit_commands` or `edit_favorites` or authoring visible: no highlight nav / Enter launch.

### Enter

- If highlight active and launch allowed: invoke same handler as card click (`on_command_clicked` / confirm).
- If no highlight: leave default (do not steal Enter from search for other purposes).

### Esc

1. If highlight active → clear highlight, keep search text/focus.  
2. Else existing `_escape_main_launcher`.

### Visual

- CSS class `keyboard-focus` on highlighted `button.command-card` — border/background similar to hover (blue accent), distinct enough at a glance.
- Cards remain `can_focus=False`.

## In scope

- `menu.py` highlight state + key handling
- Pure helper for index math (unit-tested)
- CSS for `.command-card.keyboard-focus`
- QA screenshot path (`CC_QA_NAV=1` or similar)
- Update `STATUS.md`

## Out of scope

- Moving real GTK focus onto cards
- Tray / notifications
- Drag-reorder favorites (backlog item 2)
- Changing summon / search-first focus

## Success

1. ↓ then Enter launches the first visible card (favorites-first if present) without leaving search focus for typing.  
2. Esc clears highlight before clearing search.  
3. Search/category change drops highlight.  
4. Edit modes do not keyboard-launch.  
5. Unit tests for index movement; screenshot QA of highlighted card.
