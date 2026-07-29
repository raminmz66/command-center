# Launcher UX Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hide favorited commands from the main grid, split header chrome by job, and add an “All commands” label.

**Architecture:** Adjust `CommandCenter.render_commands` to exclude saved favorites from the main grid; reorder HeaderBar packing; add a labeled section above the main grid with Soft GNOME CSS.

**Tech Stack:** Python 3, GTK 3

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-29-launcher-ux-polish-design.md`
- Favorites **A**: full cards in Favorites; hide those from main
- Header **A**: folder · refresh · sep · ★ | search · Edit · +
- Do not change sample script icons or emoji catalog
- Commit after each task
- Work from `/home/ramin/CommandCenter`

## File structure

| File | Responsibility |
|------|----------------|
| `framework/menu.py` | Header reorder; main-grid exclude favorites; All commands label |
| `framework/style.css` | Separator + All commands micro-label |
| `STATUS.md` | Cycle status |

---

### Task 1: Header chrome split + CSS separator

**Files:**
- Modify: `framework/menu.py` (HeaderBar pack order)
- Modify: `framework/style.css`

- [x] **Step 1:** After packing refresh, pack a thin vertical separator (Gtk.Separator or Box with class `cc-header-sep`), then `edit_fav_button`. Do **not** `pack_start` `edit_cmd_button`.
- [x] **Step 2:** Pack order on the end: `add_cmd_button` first (`pack_end`), then `edit_cmd_button` (`pack_end`), then `search_entry` (`pack_end`) so visual right-to-left from window edge is: + · Edit · search (GTK pack_end stacks toward the center).
- [x] **Step 3:** Add CSS for `.cc-header-sep`.
- [x] **Step 4:** Commit

---

### Task 2: Hide favorites from main grid + All commands label

**Files:**
- Modify: `framework/menu.py` (`render_commands` / content packing)
- Modify: `framework/style.css`

- [x] **Step 1:** Create `self.commands_label` with class `cc-commands-label`; pack between `favorites_box` and `grid`.
- [x] **Step 2:** In main-grid build loop, after filters, skip saved favorites basenames.
- [x] **Step 3:** Show `commands_label` when Favorites visible or main has cards.
- [x] **Step 4:** CSS for `.cc-commands-label`.
- [x] **Step 5:** Commit

---

### Task 3: Screenshot QA + STATUS done

- [x] **Step 1:** Launch app; verify no duplicate cards; header order; label present.
- [x] **Step 2:** Update `STATUS.md` cycle to done; mark plan checkboxes.
- [x] **Step 3:** Commit
