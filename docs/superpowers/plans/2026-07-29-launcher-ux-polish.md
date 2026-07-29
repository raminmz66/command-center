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

- [ ] **Step 1:** After packing refresh, pack a thin vertical separator (Gtk.Separator or Box with class `cc-header-sep`), then `edit_fav_button`. Do **not** `pack_start` `edit_cmd_button`.
- [ ] **Step 2:** Pack order on the end: `add_cmd_button` first (`pack_end`), then `edit_cmd_button` (`pack_end`), then `search_entry` (`pack_end`) so visual right-to-left from window edge is: + · Edit · search (GTK pack_end stacks toward the center).
- [ ] **Step 3:** Add CSS:

```css
.cc-header-sep {
  min-width: 1px;
  margin: 4px 6px;
  opacity: 0.35;
}
```

- [ ] **Step 4:** Commit

```bash
git add framework/menu.py framework/style.css
git commit -m "feat: split launcher header chrome by favorites vs commands."
```

---

### Task 2: Hide favorites from main grid + All commands label

**Files:**
- Modify: `framework/menu.py` (`render_commands` / content packing)
- Modify: `framework/style.css`

- [ ] **Step 1:** Create `self.commands_label = Gtk.Label(label="All commands", xalign=0)` with class `cc-commands-label`; `set_no_show_all(True)`; pack between `favorites_box` and `grid`.
- [ ] **Step 2:** In main-grid build loop, after `matches_filters`, skip if `os.path.basename(path)` is in the saved favorites set used for the strip (`self.favorites`).
- [ ] **Step 3:** Show `commands_label` when Favorites section is visible **or** main grid has ≥1 card; hide only when both Favorites and main are empty.
- [ ] **Step 4:** CSS for `.cc-commands-label` — ~11–12px, weight 700, opacity ~0.7, letter-spacing, margin under Favorites (~8–12px).
- [ ] **Step 5:** Commit

```bash
git add framework/menu.py framework/style.css
git commit -m "feat: hide favorited commands from main grid; add All commands label."
```

---

### Task 3: Screenshot QA + STATUS done

- [ ] **Step 1:** Launch app; verify no duplicate Conky/Lockdown cards; header order matches spec; label present.
- [ ] **Step 2:** Update `STATUS.md` cycle to done; mark plan checkboxes.
- [ ] **Step 3:** Commit

```bash
git add STATUS.md docs/superpowers/plans/2026-07-29-launcher-ux-polish.md
git commit -m "docs: mark launcher UX polish done after visual QA."
```
