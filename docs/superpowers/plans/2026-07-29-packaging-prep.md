# Packaging prep Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Relocatable `~/.local` install with XDG scripts dir, path module, installer + two safe samples — foundation for a future `.deb`.

**Architecture:** `paths.py` centralizes XDG data/config and framework/CSS location from `__file__`. `packaging/install.sh` copies framework, writes bin wrapper + desktop entry, seeds samples if missing. Runtime no longer uses `~/CommandCenter`.

**Tech Stack:** Python 3, PyGObject, bash installer, XDG Base Directory

**Spec:** [docs/superpowers/specs/2026-07-29-packaging-prep-design.md](../specs/2026-07-29-packaging-prep-design.md)

## Global Constraints

- Scripts dir always `$XDG_DATA_HOME/command-center/scripts` (default `~/.local/share/...`)
- Never auto-migrate personal repo scripts
- Samples: Hello Terminal + Confirm Demo; create only if missing
- No `.deb` / Flatpak this cycle
- Commit after each task

## File map

| File | Role |
|------|------|
| `framework/paths.py` | XDG + framework/CSS helpers |
| `framework/test_paths.py` | Unit tests for paths |
| `framework/menu.py` | Use paths; folder opens scripts_dir |
| `packaging/samples/*.sh` | Sample command templates |
| `packaging/install.sh` | User installer |
| `packaging/command-center.desktop` | Exec → command-center |
| `packaging/install-desktop-entry.sh` | Thin wrapper or deprecate in favor of install.sh |
| `packaging/README.md` | Install / copy scripts / PATH notes |

---

### Task 1: `paths.py` + tests

**Files:**
- Create: `framework/paths.py`
- Create: `framework/test_paths.py`

**Interfaces:**
- Produces: `data_dir() -> str`, `scripts_dir() -> str`, `framework_dir() -> str`, `css_path() -> str`, `ensure_scripts_dir() -> str`

- [ ] **Step 1:** Write failing tests (XDG_DATA_HOME override, scripts under command-center/scripts, css under framework_dir).
- [ ] **Step 2:** Implement `paths.py`.
- [ ] **Step 3:** `python3 -m unittest framework.test_paths` (or run from framework/) — PASS.
- [ ] **Step 4:** Commit `feat: add XDG paths helper for relocatable install.`

---

### Task 2: Wire menu.py to paths

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `paths.scripts_dir`, `paths.css_path`, `paths.ensure_scripts_dir`

- [ ] **Step 1:** Replace `SCRIPTS_DIR` / `CSS_FILE` hardcoded home paths with paths module; call `ensure_scripts_dir` on startup discover.
- [ ] **Step 2:** `open_folder` uses `scripts_dir()`.
- [ ] **Step 3:** `_launch_command` prefers `command-center` if on PATH else `python3` + abspath menu.py.
- [ ] **Step 4:** Smoke-run from repo (may show empty/samples only).
- [ ] **Step 5:** Commit `refactor: use XDG paths for scripts and CSS.`

---

### Task 3: Sample scripts

**Files:**
- Create: `packaging/samples/hello-terminal.sh`
- Create: `packaging/samples/confirm-demo.sh`

- [ ] **Step 1:** Write Hello Terminal (TERMINAL=true, emoji icon, echo).
- [ ] **Step 2:** Write Confirm Demo (CONFIRM=true, safe notify-send/echo).
- [ ] **Step 3:** `chmod +x` both.
- [ ] **Step 4:** Commit `feat: add packaging sample commands Hello Terminal and Confirm Demo.`

---

### Task 4: `install.sh` + desktop + README

**Files:**
- Create: `packaging/install.sh`
- Modify: `packaging/command-center.desktop`
- Create: `packaging/README.md`
- Modify: `packaging/install-desktop-entry.sh` — call install.sh or document superseded

- [ ] **Step 1:** Implement install.sh (copy framework, wrapper, desktop, samples if missing, PATH check).
- [ ] **Step 2:** Desktop Exec uses absolute `~/.local/bin/command-center` or `command-center`.
- [ ] **Step 3:** README: install, copy personal scripts, shortcut reminder, future .deb note.
- [ ] **Step 4:** Run install.sh; verify bin + samples + launch.
- [ ] **Step 5:** Optional QA screenshot of launcher with samples.
- [ ] **Step 6:** Commit `feat: add ~/.local installer for Command Center.`

---

### Task 5: STATUS done

**Files:**
- Modify: `STATUS.md`

- [ ] **Step 1:** Mark cycle done; next = real .deb or Phase 3 leftovers.
- [ ] **Step 2:** Commit `docs: mark packaging-prep cycle done.`
