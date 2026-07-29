# Desktop summon Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Single-instance Gtk.Application launch/focus with search focus, launcher-style Esc, `.desktop` install helper, and an in-app shortcut setup popover (GNOME owns the keybinding).

**Architecture:** `CommandCenterApp(Gtk.Application)` owns lifecycle; existing `CommandCenter` window gains `present_and_focus_search()`. Desktop entry + install script for Custom Shortcuts. Header popover documents `Ctrl+Space` and opens Keyboard Settings.

**Tech Stack:** Python 3, PyGObject GTK 3, Gio/Gtk.Application, GNOME `.desktop`, Soft GNOME CSS

**Spec:** [docs/superpowers/specs/2026-07-29-desktop-summon-design.md](../specs/2026-07-29-desktop-summon-design.md)

## Global Constraints

- No in-app global key grab or gsettings writes for keybindings
- Closing the main window quits the application (cold start)
- Focus search on activate only when main launcher view is visible
- Soft GNOME; no tray/daemon
- Commit after each task

## File map

| File | Role |
|------|------|
| `framework/app.py` | `CommandCenterApp` — create / activate |
| `framework/menu.py` | Window UI; `present_and_focus_search`; Esc; shortcut popover; entrypoint calls app |
| `framework/style.css` | Header gear + popover Soft GNOME |
| `packaging/command-center.desktop` | Desktop entry template |
| `scripts/install-desktop-entry.sh` | Install into `~/.local/share/applications/` |

---

### Task 1: Gtk.Application single-instance shell

**Files:**
- Create: `framework/app.py`
- Modify: `framework/menu.py` (bottom entrypoint + small hooks for app to hold window ref)

**Interfaces:**
- Produces: `CommandCenterApp` with `application_id="org.commandcenter.App"`, `do_activate` creates/shows window
- Produces: `CommandCenter.present_and_focus_search()` — present; focus search if stack is main

- [ ] **Step 1:** Add `framework/app.py` with `Gtk.Application` subclass; on activate create `CommandCenter` once, `add_window`, show_all, call `present_and_focus_search`.
- [ ] **Step 2:** Add `present_and_focus_search` on `CommandCenter`; wire `destroy`/`delete-event` to quit via application if needed.
- [ ] **Step 3:** Replace `Gtk.main()` boot with `CommandCenterApp().run(sys.argv)`.
- [ ] **Step 4:** Verify: run `python3 menu.py` twice quickly — only one window; second focuses.
- [ ] **Step 5:** Commit `feat: add Gtk.Application single-instance activate for summon.`

---

### Task 2: Launcher-style Escape on main grid

**Files:**
- Modify: `framework/menu.py` (`on_search_key_press`, `on_window_key_press`)

**Interfaces:**
- Consumes: main stack name, `search_entry`, existing confirm/authoring Esc

- [ ] **Step 1:** Implement helper `_escape_main_launcher()` — if confirm open, hide; elif search text, clear; else close window.
- [ ] **Step 2:** Call it from search Esc and from window Esc when not authoring.
- [ ] **Step 3:** Manual check: type query → Esc clears; Esc again quits; authoring Esc unchanged.
- [ ] **Step 4:** Commit `fix: launcher-style Escape clears search then closes.`

---

### Task 3: Desktop entry + install helper

**Files:**
- Create: `packaging/command-center.desktop`
- Create: `scripts/install-desktop-entry.sh`

**Interfaces:**
- Produces: Exec path to `framework/menu.py` (python3), `StartupWMClass=command-center` / match app id as feasible
- Install copies/symlinks to `~/.local/share/applications/command-center.desktop` and runs `update-desktop-database` if present

- [ ] **Step 1:** Write desktop file with Name, Comment, Exec, Icon (`utilities-terminal` or project icon if any), Categories, StartupNotify, StartupWMClass.
- [ ] **Step 2:** Write install script resolving repo root, writing absolute Exec, installing desktop file.
- [ ] **Step 3:** Run install script; verify file exists under `~/.local/share/applications/`.
- [ ] **Step 4:** Commit `feat: add desktop entry and install helper for Custom Shortcuts.`

---

### Task 4: Shortcut setup popover + Open Keyboard Settings

**Files:**
- Modify: `framework/menu.py` (header gear, popover UI)
- Modify: `framework/style.css`

**Interfaces:**
- Consumes: launch command string matching desktop Exec
- Produces: popover with Copy + Open Keyboard Settings (`gnome-control-center keyboard` or `xdg-open` fallback)

- [ ] **Step 1:** Add header button (gear) left of search cluster (`pack_end` order: + · Edit · gear · search — or gear left of search: + · Edit · search · gear per Soft GNOME; prefer **search · gear · Edit · +** so gear sits with utility actions — actually spec says gear on main; put gear immediately left of search via pack_end: first pack_end=+ , then Edit, then gear, then search → visual search · gear · Edit · +. Wait pack_end stacks toward center: first packed = far right. Current: + · Edit · search. Add gear: pack_end +; Edit; gear; search → visual **search · gear · Edit · +**.
- [ ] **Step 2:** Build popover: title, Ctrl+Space recommendation, steps, command entry, Copy, Open Keyboard Settings.
- [ ] **Step 3:** CSS for button/popover.
- [ ] **Step 4:** QA screenshot of main window with popover open (`CC_QA_*` or manual import).
- [ ] **Step 5:** Commit `feat: add desktop shortcut setup popover in header.`

---

### Task 5: STATUS + smoke QA

**Files:**
- Modify: `STATUS.md`

- [ ] **Step 1:** Smoke: single-instance, Esc, popover opens, desktop file installed.
- [ ] **Step 2:** Capture edit-free launcher screenshot with shortcut popover if not done in Task 4.
- [ ] **Step 3:** Update STATUS — cycle done; next packaging or remaining Phase 3.
- [ ] **Step 4:** Commit `docs: mark desktop summon cycle done.`
