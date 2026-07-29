# Edit mode UX polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Match Option C edit-mode mockup — Done button, Launch paused status, dimmed cards, icon-only actions; no wide banner.

**Architecture:** Menu owns mode chrome (banner removal, status label, Done label). CommandCard + CSS own dimmed body and action chip. QA via `CC_QA_AUTHORING=edit` + screenshot iterate.

**Tech Stack:** GTK 3, Soft GNOME CSS, existing edit_commands path

**Spec:** [docs/superpowers/specs/2026-07-29-edit-mode-ux-design.md](../specs/2026-07-29-edit-mode-ux-design.md)  
**Visual ref:** `.superpowers/qa/edit-mode-chrome-reference.html` (choice C)

## Global Constraints

- Favorites edit out of scope
- No “tap” copy
- Commit after each task
- Iterate screenshots until visually match Option C

## File map

| File | Role |
|------|------|
| `framework/menu.py` | Done label; status label; remove banner show |
| `framework/widgets.py` | Action chip structure/classes for CSS |
| `framework/style.css` | Dimmed card + chip + status styles |

---

### Task 1: Header Done + Launch paused status (remove banner)

**Files:**
- Modify: `framework/menu.py`
- Modify: `framework/style.css`

- [ ] **Step 1:** Replace edit_banner usage with `edit_status` label “Launch paused” (or hide banner permanently and add status).
- [ ] **Step 2:** `_sync_edit_cmd_button` sets label Edit/Done and active class.
- [ ] **Step 3:** Show/hide status with edit_commands.
- [ ] **Step 4:** Commit `feat: replace edit banner with Done and Launch paused status.`

---

### Task 2: Dimmed cards + icon action chip CSS

**Files:**
- Modify: `framework/widgets.py`
- Modify: `framework/style.css`

- [ ] **Step 1:** Structure actions in a chip container; tooltips; no emoji-only affordance without icons if already symbolic.
- [ ] **Step 2:** CSS: `.command-card.commands-edit` dim children; chip opaque; better edit/delete colors.
- [ ] **Step 3:** Commit `style: dim edit-mode cards and polish action chip.`

---

### Task 3: QA screenshots + iterate to match C

**Files:**
- Possibly CSS/menu tweaks

- [ ] **Step 1:** `CC_QA_AUTHORING=edit CC_QA_SHOT=...` capture edit mode.
- [ ] **Step 2:** Compare to Option C; adjust spacing/opacity/status placement.
- [ ] **Step 3:** Re-shot until acceptable match.
- [ ] **Step 4:** Commit `fix: align edit mode visuals with Option C mockup.` (or fold into prior if no extra diff)
- [ ] **Step 5:** STATUS done + commit `docs: mark edit mode UX polish done.`
