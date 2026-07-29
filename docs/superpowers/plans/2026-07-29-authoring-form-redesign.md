# Authoring Form Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sectioned Soft GNOME authoring form with header-only Save and popover icon picker matching the locked visual HTML.

**Architecture:** Rebuild `AuthoringForm` sections; `Gtk.Popover` for icon grid; CSS for sections/chip; screenshot QA vs `docs/superpowers/visuals/2026-07-29-authoring-form-redesign.html`.

**Tech Stack:** Python 3, GTK 3

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-29-authoring-form-redesign-design.md`
- Visual: `docs/superpowers/visuals/2026-07-29-authoring-form-redesign.html`
- Header Save only; no footer Cancel/Save
- Icon: chip + Change… → Popover 6×6; no form height jump
- Sections: Identity, Appearance, Behavior, Script
- Keep 36 emoji catalog, color, toggles, dirty Back, validation
- Commit after each task; iterate screenshots until UX match
- Work from `/home/ramin/CommandCenter`

## File structure

| File | Responsibility |
|------|----------------|
| `framework/authoring.py` | Sectioned layout, chip, popover |
| `framework/style.css` | Section / chip / popover styles |
| `framework/menu.py` | Window height if needed; Escape popover priority optional |
| `STATUS.md` | Cycle status |

---

### Task 1: CSS for sections + chip

**Files:** Modify `framework/style.css`

- [x] Add `.cc-authoring-section`, `.cc-authoring-section-title`, `.cc-authoring-chip`, `.cc-authoring-change`, popover glyph styles; remove reliance on footer button layout.
- [x] Commit: `style: Soft GNOME section chrome for authoring form.`

---

### Task 2: Rebuild `AuthoringForm` layout + popover

**Files:** Modify `framework/authoring.py`

- [x] Four sections; remove footer actions; icon chip + Change… + `Gtk.Popover` with 36-grid; Escape closes popover via form handler if needed.
- [x] Bump default window height in `menu.py` if Script still cramped (~780–820).
- [x] Commit: `feat: sectioned authoring form with icon popover.`

---

### Task 3: Screenshot QA loop

- [x] Capture form (popover closed + open); compare to visual HTML; fix spacing until senior-UX accept.
- [x] Update STATUS; commit: `fix: polish authoring form to match redesign visual.`

---
