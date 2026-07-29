# Launcher UX polish (Favorites + header)

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release (reordered)  
**Cycle:** Launcher UX polish  
**Status:** Approved for planning  
**Parent:** [2026-07-27-favorites-design.md](2026-07-27-favorites-design.md), [2026-07-27-favorites-separation-design.md](2026-07-27-favorites-separation-design.md)

## Goal

Fix first-viewport Soft GNOME launcher issues: stop favorited commands from appearing twice, clarify header edit controls, and label the main command region.

## Decisions

| Topic | Choice |
|-------|--------|
| Favorites duplication | **A** — full cards in Favorites; hide those commands from the main grid |
| Header chrome | **A** — left: folder · refresh · separator · ★; right: search · **Edit** · **+** |
| Main region label | Yes — quiet Soft GNOME **“All commands”** label above the main grid |
| Sample / catalog icons | **No change** — emoji choice remains free; sample script icons are user data |

## In scope

- Exclude favorited basenames from the main grid render (after category/search filters)
- Reorder HeaderBar: move command **Edit** to the right cluster next to **+**
- Visual separator between refresh and ★ on the left
- Add “All commands” label above main grid with Soft GNOME micro-label CSS
- Keep Favorites strip membership, Apply/pending favorites behavior, and empty Favorites hide behavior

## Out of scope

- Changing emoji catalog or sample `# ICON=` values
- Merging favorites-edit and commands-edit into one mode
- Overflow / ⋮ menu for folder+refresh
- Authoring form, packaging, confirm popover

## Layout (top → bottom)

1. HeaderBar as decided above  
2. Category chips  
3. Favorites panel (when non-empty) — full cards  
4. “All commands” label (when Favorites visible and/or main has cards; hide only if both empty)  
5. Main grid — filtered commands **minus** current saved favorites set  

## Behavior details

1. Favorites strip still ignores category and search.  
2. Main grid applies filters, then drops any command whose basename is in `self.favorites` (saved set). While favorites-edit is active, strip membership still follows saved favorites until Apply (unchanged).  
3. Commands edit/delete overlays remain available on cards in Favorites and in main.  
4. Unfavoriting via Apply returns the command to the main grid on the next render.

## Success criteria

- No duplicate cards for the same command on the launcher page  
- ★ and Edit are spatially separated by job (favorites left, commands right)  
- “All commands” label clarifies the lower region  
- Soft GNOME chrome preserved; no sample icon migration  

## Risks

- With all matching commands favorited, main grid can be empty under filters — label still explains the region  
- Reordering HeaderBar `pack_start` / `pack_end` must preserve Apply / Done button state sync  
