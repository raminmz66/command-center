# Command Center — Project Overview & Roadmap

## Vision

**Command Center** is a modern GTK desktop application that turns shell scripts into a professional graphical command center.

The idea:

> A user drops executable scripts into a folder.  
> Each script describes itself through metadata.  
> Command Center automatically creates a polished launcher interface.

The user should not need to modify Python code when adding commands.

The workflow:

```
Create script
      |
      |
Add metadata
      |
      |
Drop into scripts/
      |
      |
Command Center automatically creates GUI action
```

Example:

```bash
#!/bin/bash

# NAME=Conky
# ICON=system-monitor-app-symbolic
# DESC=Start desktop widgets
# CATEGORY=Desktop
# TERMINAL=false

conky
```

---

# Project Philosophy

## 1. Everything is a plugin

Commands are independent scripts.

Example:

```
scripts/

backup.sh
conky.sh
vpn.sh
cleanup.sh
```

The application does not know what they do.

It only knows:

- name
- icon
- description
- category
- execution method

---

## 2. Metadata is the API

Scripts describe themselves.

Current metadata:

```bash
# NAME=
# ICON=          # emoji or legacy symbolic name
# DESC=
# CATEGORY=
# TERMINAL=
# CONFIRM=
```

Favorites live in user config (`~/.config/command-center/`), not script metadata.

---

## 3. UI is data-driven

The application should never contain:

```python
if command == "Conky":
```

Everything comes from metadata.

---

## 4. Appearance is separated

The UI should be controlled by:

```
style.css
```

not Python.

Python handles:

- logic
- loading
- execution

CSS handles:

- colors
- spacing
- fonts
- shapes

---

# Current Status

## Version

Soft GNOME personal launcher — installable via `.deb` / `~/.local` (`packaging/`).

Live cursor for day-to-day work: **`STATUS.md`**. This file is long-term vision + backlog only.

---

# Completed Milestones

---

# Milestone 1 — Functional Launcher

Completed:

- GTK application window
- Script discovery
- Grid layout
- Buttons
- Tooltips
- Terminal execution
- Non-terminal execution

Status:

✅ Complete

---

# Milestone 2 — Metadata System

Scripts now describe themselves.

Example:

```bash
# NAME=Backup
# ICON=document-save-symbolic
# DESC=Backup home directory
# TERMINAL=true
```

The application reads this information automatically.

Status:

✅ Complete

---

# Milestone 3 — Native GNOME Integration

Moved away from emoji icons.

Implemented:

- GTK icon theme support
- symbolic icons
- Yaru compatibility
- Adwaita compatibility

Example:

Before:

```
🖥️ Conky
```

After:

```
[system-monitor icon]

Conky
```

Status:

✅ Complete

---

# Milestone 4 — Card Interface

Commands are displayed as application cards.

Features:

- icon
- title
- description
- grid layout
- fixed window size

Status:

✅ Complete

---

# Milestone 5 — Modular Architecture

The application was separated into components:

```
framework/

menu.py
widgets.py
metadata.py
launcher.py
style.css
```

Responsibilities:

## menu.py

Main application window.

Handles:

- window
- layout
- loading commands

---

## widgets.py

Visual components.

Handles:

- command cards
- icons
- labels

---

## metadata.py

Script parser.

Handles:

- reading metadata
- creating command information

---

## launcher.py

Execution engine.

Handles:

- terminal commands
- normal commands

---

## style.css

Appearance.

Handles:

- colors
- spacing
- design

---

Status:

✅ Complete

---

# Milestone 6 — Framework Refactor

New structure:

```
CommandCenter/

framework/

├── menu.py
├── widgets.py
├── metadata.py
├── launcher.py
└── style.css


scripts/

└── commands
```

The old launcher remains safe.

The new version is developed separately.

Status:

✅ Complete

---

# Milestone 7 — GNOME HeaderBar

Implemented:

- native application header
- folder button
- refresh button
- close button

The application now behaves like a proper GNOME utility.

Status:

✅ Complete

---

# Current Architecture

```
                 Script
                   |
                   |
              metadata.py
                   |
                   |
              menu.py
             /       \
            /         \
     widgets.py    launcher.py
            |
            |
        style.css
```

---

# Roadmap (refined 2026-07-30)

Park = keep for a later pass; re-decide then (implement or trash).
Trash = removed from the plan.

## Done

| Area | Notes |
|------|--------|
| Soft GNOME UI / CSS | Cards, header, theme-friendly styling |
| Search | Instant filter, focus, shortcuts |
| Categories | `# CATEGORY=` + chips |
| Favorites | Edit/Apply, separated strip |
| Confirmation | `# CONFIRM=` + popover |
| Script authoring | In-app create/edit/delete, emoji icons |
| Desktop summon (lite) | GNOME global shortcut + show/focus + Esc |
| Packaging | XDG paths, `install.sh` / `uninstall.sh`, `.deb`, app icon |

## Parked (later)

| Item | Goal (when we reopen) |
|------|------------------------|
| **29** — System tray | Background tray icon + quick commands (vs summon-and-close) |
| **31** — Templates | Curated script packs beyond Hello Terminal / Confirm Demo |
| **32 leftovers** — Flatpak / AppImage | Extra formats; `.deb` already ships |

Card keyboard nav (old 27 leftovers) moved to **Active backlog** below.

## Active backlog (do in order)

Each item: brainstorm → spec → plan → execute.

1. **Arrow + Enter on cards** — keyboard navigate the grid; Enter runs highlighted command  
2. **Reorder favorites by drag** — drag to reorder the favorites strip  
3. **Empty-state that teaches** — clear CTA when scripts dir is empty  
4. **Remember window size/position** — restore geometry on summon  

## Removed (trashed 2026-07-30)

| Item | Why dropped |
|------|-------------|
| **25** Advanced execution engine | Fire-and-forget is enough; history/logs out of scope |
| **26** Status commands | Live card status / polling not needed for personal use |
| **28** Desktop notifications | Prefer `notify-send` inside scripts when wanted |
| **30** Project generator | Not distributing as a multi-project framework right now |

## Next

Active backlog (in order) — each: brainstorm → spec → plan → execute:

1. Arrow + Enter on cards  
2. Reorder favorites by drag  
3. Empty-state that teaches  
4. Remember window size/position  

Live cursor: `STATUS.md`.

---

# Long-Term Vision

Command Center stays a **personal Soft GNOME launcher**: drop scripts with metadata, get a polished GUI — no Python edits to add commands.

Optional later paths (only if parked items earn their keep): tray mode, keyboard-palette nav, template packs, wider packaging.

---

# Current Achievement Summary

✅ GTK Soft GNOME launcher
✅ Script-driven architecture + metadata API
✅ Search, categories, favorites, confirm
✅ In-app script authoring
✅ Desktop summon (GNOME shortcut)
✅ Relocatable install + `.deb` + uninstall + app icon
