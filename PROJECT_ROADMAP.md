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
# ICON=
# DESC=
# TERMINAL=
```

Future metadata:

```bash
# CATEGORY=
# CONFIRM=
# FAVORITE=
# TYPE=
# SHORTCUT=
```

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

Foundation v1.0-alpha

The project has evolved from a simple Python launcher into a modular GTK application framework.

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

# Remaining Roadmap

---

# Phase 1 — UI Professionalization

Goal:

Make Command Center look like a polished GNOME application.

---

# Step 20 — Final CSS Design

Improve visual quality.

Add:

- rounded cards
- modern spacing
- better typography
- hover animations
- improved header
- dark mode support
- theme integration

Target:

```
╭──────────────────────────────╮
│ Command Center          📁 ⟳ │
├──────────────────────────────┤
│                              │
│   🖥 Conky     🔒 Security    │
│                              │
│   💾 Backup    🌐 VPN         │
│                              │
╰──────────────────────────────╯
```

---

# Step 21 — Search System

Add:

```
🔍 Search commands...
```

Features:

- instant filtering
- keyboard focus
- fast discovery

Example:

Typing:

```
con
```

shows:

```
Conky
```

---

# Step 22 — Categories

Metadata:

```bash
# CATEGORY=System
```

Interface:

```
All

Desktop

System

Network

Maintenance

Security
```

---

# Step 23 — Favorites

Metadata:

```bash
# FAVORITE=true
```

Features:

- favorite commands section
- quick access
- priority sorting

---

# Phase 2 — Smart Launcher

---

# Step 24 — Confirmation System

For dangerous commands:

Metadata:

```bash
# CONFIRM=true
```

Example:

```
Run lockdown command?

[Cancel] [Run]
```

Useful for:

- sudo commands
- cleanup
- shutdown
- system changes

---

# Step 25 — Advanced Execution Engine

Improve launcher.py.

Add:

- command output capture
- error reporting
- execution history
- logs
- success messages

Example:

```
✓ Backup completed
```

---

# Step 26 — Status Commands

Support commands that report state.

Example:

```
Update Lockdown

ACTIVE ✓
```

Metadata:

```bash
# TYPE=status
```

---

# Phase 3 — Desktop Integration

---

# Step 27 — Keyboard Control

Add:

- global shortcut
- arrow navigation
- Enter execution
- Escape close

Example:

```
Ctrl + Space
```

opens Command Center.

---

# Step 28 — Desktop Notifications

Examples:

```
Backup completed successfully
```

or:

```
Firewall enabled
```

---

# Step 29 — System Tray Mode

Optional background mode:

```
Command Center icon

     |
     |
Quick commands
```

---

# Phase 4 — Framework Release

---

# Step 30 — Project Generator

Create:

```
command-center-init MyLauncher
```

Automatically creates:

```
MyLauncher/

framework/

scripts/

icons/

style.css

README.md
```

---

# Step 31 — Templates

Possible templates:

## Desktop Utility

Examples:

- Conky
- screenshots
- wallpapers


## Server Administration

Examples:

- service restart
- logs
- monitoring


## Developer Toolbox

Examples:

- build
- test
- deploy


## Home Automation

Examples:

- lights
- sensors
- scripts

---

# Step 32 — Packaging

Possible releases:

- Debian package
- AppImage
- Flatpak

---

# Long-Term Vision

Command Center becomes a reusable GTK framework.

A user installs:

```
Command Center
```

Adds scripts:

```
backup.sh

monitor.sh

cleanup.sh

vpn.sh
```

and immediately gets:

```
╭──────────────────────────╮
│ Command Center           │
├──────────────────────────┤
│ 🖥 Conky                 │
│ 🔒 Security              │
│ 💾 Backup                │
│ 🌐 VPN                   │
╰──────────────────────────╯
```

No Python editing.

No configuration files.

Just scripts + metadata.

---

# Current Achievement Summary

Completed:

✅ Working GTK launcher  
✅ Script-driven architecture  
✅ Metadata API  
✅ Native GNOME icons  
✅ Card-based UI  
✅ Modular framework  
✅ CSS separation  
✅ Dynamic refresh  
✅ GNOME HeaderBar  
✅ Clean project structure  

---

# Next Development Point

The next step is:

## Step 20 — Professional CSS redesign

After that:

Command Center will not only function professionally — it will look like a polished GNOME desktop application.
