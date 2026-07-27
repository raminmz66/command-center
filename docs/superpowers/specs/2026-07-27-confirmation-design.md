# Step 24 — Confirmation System

**Date:** 2026-07-27  
**Phase:** 2 — Smart Launcher  
**Cycle:** Step 24 — Confirmation System  
**Status:** Approved for planning

## Goal

When a script has `# CONFIRM=true`, show an inline Soft GNOME confirmation banner before running. Message: `Run {Name}?` with **Cancel** / **Run**. While open, card launches are hard-blocked until Cancel, Run, or Escape.

## Decisions

| Topic | Choice |
|-------|--------|
| UI | **C** — inline banner (not modal) |
| Copy | **A** — `Run {Name}?` only |
| While open | **B** — hard block card launches until Cancel / Run / Escape |
| Implementation | **1** — banner + state in `menu.py`; reuse `run_command` |

## In scope

- Inline banner under category chips (above Favorites / main grid)
- Visual: warm panel, gold border (`#f6c32a`), Cancel + red **Run** — match brainstorm mockup C
- On card click: if `meta["confirm"]` → show banner, stash path/meta; else run immediately
- While pending: ignore launch clicks on cards (edit-favorites toggles still allowed if already in edit mode)
- Cancel / Escape → hide banner, clear pending
- Run → hide banner, call `run_command`, clear pending
- Tag sample script `# CONFIRM=true` (Lockdown Status)
- Soft GNOME CSS: `.cc-confirm-banner`, buttons
- Preserve search focus fix, favorites Apply, chips

## Out of scope

- Custom `# CONFIRM_MSG=`
- Modal / MessageDialog
- Confirm for non-metadata reasons
- “Don’t ask again”

## Architecture

```
card click
  → if edit_favorites: toggle pending favorites (unchanged)
  → elif pending confirm: ignore (hard block)
  → elif meta.confirm: show banner (stash path, meta)
  → else: run_command(...)

banner Run → run_command(stashed)
banner Cancel / Esc → clear
```

`metadata.py` already parses `confirm`. `launcher.py` unchanged.

## Components

### `menu.py`

- `self.pending_confirm = None`  # `(path, meta)` or None
- `self.confirm_banner` box (`no_show_all`), label + Cancel + Run
- `on_command_clicked(card, path, meta)` wiring instead of direct `run_command` in normal mode
- Escape in window key handler dismisses confirm when pending (search Escape still clears search when search focused)

### `style.css`

- Warm background, gold border, padding, radius matching mockup
- Run button destructive red; Cancel quiet border

### Sample

`scripts/update-lockdown-status.sh` → `# CONFIRM=true`

## Verification

- Confirm script shows banner; non-confirm runs immediately
- Run executes; Cancel/Esc dismiss without run
- Second card click while pending does nothing
- CSS loads; Soft GNOME / favorites / search intact

## Risks

- Escape conflict with search — only cancel confirm when search does not have focus (or when pending and not typing)
- Banner layout shift — accept mild reflow; keep `no_show_all` when hidden
