# Step 24b — Confirm placement (popover)

**Date:** 2026-07-27  
**Phase:** 2 — Smart Launcher  
**Cycle:** Step 24b — Confirm placement UX  
**Status:** Approved for planning

## Goal

Fix eye-jump UX: confirmation must appear **next to the clicked card**, not as a top banner. Keep the **accepted Soft GNOME confirm chrome** (cream fill, gold border, `Run {Name}?`, Cancel / red Run).

## Decisions

| Topic | Choice |
|-------|--------|
| Placement | **B** — popover anchored to the clicked card |
| Widget | **1** — `Gtk.Popover` |
| Visual | **Preserve accepted banner design** — cream `#fff8e7`, border `#f6c32a`, Cancel quiet, Run `#c01c28` |
| Copy | Unchanged — `Run {Name}?` |
| While open | Unchanged — hard-block other launches; Escape / Cancel dismiss |

## In scope

- Remove top `confirm_banner` from the content stack
- On confirmable card click: create/show `Gtk.Popover` relative to that card
- Popover body: label + Cancel + Run with accepted Soft GNOME styles (`.cc-confirm-popover` / reuse button classes)
- Prefer popover position above the card; allow GTK to flip if needed
- `pending_confirm` hard-block + Escape dismiss unchanged
- Run → hide popover → `run_command`
- Cancel / Escape / popover `closed` → clear pending

## Out of scope

- Modal overlay (option A)
- In-card morph (option C)
- Changing confirm copy, `# CONFIRM=` parsing, or sample script tags
- Redesigning button colors away from the accepted look

## Architecture

```
card click (confirm)
  → pending_confirm = (path, meta)
  → Gtk.Popover(relative_to=card) with Soft GNOME content
  → hard-block other launches

Run    → hide → run_command
Cancel / Esc / closed → hide → clear pending
```

## Components

### `menu.py`

- Delete packing/show/hide of top `confirm_banner` box
- `show_confirm(path, meta, relative_to=card)` builds or reuses popover pointed at `relative_to`
- Wire `on_command_clicked` to pass the card widget into `show_confirm`
- Connect popover `closed` to clear pending if still set
- Keep Escape handling when pending and search not focused

### `style.css`

- Remove or stop using `.cc-confirm-banner` as a page banner
- Style popover content box to match accepted look:
  - background `#fff8e7`
  - border `2px solid #f6c32a`
  - padding ~14–16px
  - label 15px / 700
  - Cancel / Run buttons same as accepted (`.cc-confirm-cancel`, `.cc-confirm-run`)

## Visual contract (accepted)

Must match the previously approved banner appearance inside the popover:

| Element | Spec |
|---------|------|
| Panel | Cream `#fff8e7`, gold `#f6c32a` border, ~10px radius |
| Title | Bold `Run {Name}?` |
| Cancel | White/light, bordered, min-width ~72px |
| Run | `#c01c28` fill, white text |

## Verification

- Click Lockdown (bottom card) → popover appears on/near that card, not at top
- Visual match to accepted cream/gold confirm
- Run / Cancel / Escape behavior unchanged
- Non-confirm cards still launch immediately
- Favorites / chips / search unchanged

## Risks

- Popover styling varies by GTK theme — prefer styling an inner box with our classes, not relying on theme popover chrome alone
- Card rebuild during pending could orphan popover — dismiss pending on `render_commands` if relative card is destroyed, or avoid rebuilding while pending
