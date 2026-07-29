# Edit mode UX polish (Option C)

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release (polish)  
**Cycle:** Edit mode UX polish  
**Status:** Approved for planning  
**Visual ref:** `.superpowers/qa/edit-mode-chrome-reference.html` (Option C — dimmed body + icon-only toolbar)  
**Companion mockups:** `.superpowers/brainstorm/268718-1785353487/content/edit-mode-chrome.html`

## Goal

Make commands edit mode quieter and desktop-correct Soft GNOME: no long “tap” banner, clear Done affordance, dimmed cards, icon-only edit/delete with tooltips — match Option C mockup for QA.

## Decisions

| Topic | Choice |
|-------|--------|
| Scope | **B** (includes polish A) — reduce chrome, not full interaction redesign |
| Visual chrome | **C** — no wide banner; “Launch paused” status; dimmed cards; icon-only ✎/🗑 |
| Header button | **Done** while active (yellow); **Edit** when idle |
| Favorites ★ edit | Out of scope this cycle (leave as-is) |

## In scope

- Remove `cc-edit-banner` from commands edit flow (hide/delete usage)
- Add quiet “Launch paused” status label when `edit_commands`
- Header Edit ↔ Done label sync
- Card edit styling: dimmed content; action chip with icon-only buttons + tooltips
- Improve pencil/delete contrast (no muddy beige)
- Desktop copy only (no “tap”)
- QA screenshots vs Option C reference; iterate until match

## Out of scope

- Favorites edit-mode redesign
- Esc to exit edit mode
- Select-then-toolbar / single-action-per-card redesign (was approach C)
- Authoring form changes

## Behavior

1. Click **Edit** → `edit_commands=True`; button label **Done**; show “Launch paused”; cards render with commands-edit chrome; launch clicks remain paused.
2. Click **Done** → exit edit mode; label **Edit**; hide status; normal cards.
3. ✎ opens authoring; 🗑 keeps existing delete confirm flow.
4. Tooltips: “Edit command”, “Delete command”.

## Visual contract (Option C)

- No full-width instruction banner
- Status: small, muted “Launch paused” (near top of content / under chips — not competing with cards)
- Cards: reduced opacity / muted surface on icon+title+desc; action cluster stays crisp on white chip
- Actions: icon-only, ~28–30px hit targets, clear border; delete subtly destructive (light red tint)
- Header Done keeps existing `.cc-edit-commands.active` gold treatment

## Success criteria

- Screenshot of edit mode matches Option C structure (status placement, no banner, dimmed cards, icon toolbar)
- Idle mode unchanged aside from any shared CSS cleanup
- No “tap” in UI strings

## Risks

- Overlay + dim may need CSS on `.command-card.commands-edit` child labels, not the whole button (actions must stay readable)
- “Launch paused” placement must not collide with category chips
