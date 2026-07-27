# Step 23b — Favorites polish (stars + Apply)

**Date:** 2026-07-27  
**Phase:** 1 — UI Professionalization (follow-up)  
**Cycle:** Step 23b — Favorites polish  
**Status:** Approved for planning

## Goal

Make edit-mode favorite stars larger and stop the Favorites strip from updating live while editing. Pending toggles apply only when the user clicks **Apply**, which also exits edit mode.

## Decisions

| Topic | Choice |
|-------|--------|
| Star size | Larger, clearly visible on the card (CSS; ~22–24px) |
| Commit UX | **A** — Header shows **Apply** in edit mode; Apply persists pending set, refreshes Favorites strip, exits edit mode (replaces **Done**) |
| While editing | Card clicks only flip pending stars; do **not** call `toggle_favorite` / `save_favorites`; do **not** rebuild Favorites strip from pending |
| Discard | Leaving edit only via Apply — no Cancel in v1 (re-enter edit and Apply again to change). Entering edit copies current favorites into a pending list |

## In scope

- Bigger `.cc-favorite-star` styling
- `self.pending_favorites` (list) while `edit_favorites` is True
- Card click in edit mode: toggle basename in `pending_favorites` only; re-render **main + favorites strip cards’ star glyphs from pending**, but Favorites strip **membership** still reflects **saved** `self.favorites` until Apply
- Apply: `save_favorites(pending)` (with prune via known basenames), `self.favorites = load_favorites()`, exit edit mode, full render
- Keep startup Favorites visibility fix (`no_show_all` toggle + post-`show_all` render)
- Preserve search focus fix, Soft GNOME, category chips

## Out of scope

- Cancel / discard button
- Drag-reorder
- Showing pending additions in the Favorites strip before Apply (strip stays stable = last saved set)

## Behavior detail

**Enter edit** (star header button):  
`pending_favorites = list(self.favorites)`; show **Apply**; stars reflect `pending_favorites`.

**Click card in edit:**  
Toggle basename in `pending_favorites`; refresh card stars only (re-render grids) **without** changing which commands appear in the Favorites strip (strip still built from `self.favorites`).

**Apply:**  
Save `pending_favorites` (pruned to known scripts); reload `self.favorites`; `edit_favorites = False`; clear pending; rebuild strip + main; header returns to star icon.

## Risks

- Re-rendering all cards on each pending toggle may still feel “jumpy” for stars — acceptable; strip membership must not jump
- User closes window mid-edit — pending discarded (OK for v1)
