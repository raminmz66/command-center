# Authoring Icon Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 36-emoji picker (no custom name); cards show the same emoji as `# ICON=`; migrate sample scripts; no symbolic icon path on cards.

**Architecture:** `ICON_CATALOG` of 36 emoji in `authoring.py`; `CommandCard` renders a `Gtk.Label` glyph; scripts store emoji in `# ICON=`.

**Tech Stack:** Python 3, GTK 3, `unittest`

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-29-authoring-icon-catalog-design.md`
- Picker ≡ card glyph character-for-character
- No GNOME symbolic / `Gtk.IconTheme` for command icons
- No custom icon-name field
- Catalog length 36; grid 6×6; flat glyph tiles
- Migrate `conky.sh` → 🖥, `test-terminal.sh` → 💻, `update-lockdown-status.sh` → 🔒
- Preserve Soft GNOME authoring chrome, favorites, confirm, search focus
- Commit after each task; screenshot QA; work from `/home/ramin/CommandCenter`

## File structure

| File | Responsibility |
|------|----------------|
| `framework/authoring.py` | 36-emoji catalog, picker, remove custom entry |
| `framework/widgets.py` | Emoji label on cards |
| `framework/style.css` | Emoji glyph size on cards |
| `scripts/*.sh` | Emoji `# ICON=` |
| `framework/test_scriptio.py` | Optional emoji round-trip assert |
| `STATUS.md` | Cycle done |

---

### Task 1: Expand catalog + remove custom name in `authoring.py`

**Files:**
- Modify: `framework/authoring.py`

- [x] **Step 1:** Replace `CURATED_ICONS` with `ICON_CATALOG` (36 emoji from spec). Remove symbolic pairs / `_CURATED_BY_NAME` mapping to names.
- [x] **Step 2:** Remove `custom_icon_entry` UI and handlers; load/select by emoji only; default `🔧`.
- [x] **Step 3:** Smoke import; commit

```bash
git add framework/authoring.py
git commit -m "feat: 36-emoji authoring catalog; drop custom icon name."
```

---

### Task 2: Cards render emoji; CSS

**Files:**
- Modify: `framework/widgets.py`
- Modify: `framework/style.css`

- [x] **Step 1:** Replace `Gtk.Image` theme lookup with `Gtk.Label(meta["icon"] or "🔧")` + `command-icon` (+ color class).
- [x] **Step 2:** CSS `.command-icon` font-size ~28–32px for card glyphs.
- [x] **Step 3:** Commit

```bash
git add framework/widgets.py framework/style.css
git commit -m "feat: show emoji glyphs on command cards."
```

---

### Task 3: Migrate sample scripts + scriptio test

**Files:**
- Modify: `scripts/conky.sh`, `scripts/test-terminal.sh`, `scripts/update-lockdown-status.sh`
- Modify: `framework/test_scriptio.py` (emoji round-trip)

- [ ] **Step 1:** Set `# ICON=` per spec table.
- [ ] **Step 2:** Add/adjust unit test that `write_script`/`read_script` preserves emoji ICON.
- [ ] **Step 3:** Run tests; commit

```bash
cd framework && python3 -m unittest test_scriptio -v
git add scripts/*.sh framework/test_scriptio.py
git commit -m "chore: migrate sample scripts to emoji icons."
```

---

### Task 4: Screenshot QA + STATUS

**Files:**
- Modify: `STATUS.md`, this plan checkboxes

- [ ] **Step 1:** Screenshot launcher (emoji cards) and authoring form (36 grid).
- [ ] **Step 2:** Fix any visual gaps (size/spacing).
- [ ] **Step 3:** Mark cycle done; commit

```bash
git commit -m "docs: mark emoji icon catalog done after visual QA."
```

---

## Execution handoff

Implement now; commit per task; screenshot QA without waiting.
