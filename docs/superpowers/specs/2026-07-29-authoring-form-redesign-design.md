# Authoring form redesign (Soft GNOME)

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release (reordered)  
**Cycle:** Authoring form UI/UX redesign  
**Status:** Approved for planning  
**Parent:** [2026-07-28-script-authoring-design.md](2026-07-28-script-authoring-design.md), [2026-07-29-authoring-icon-catalog-design.md](2026-07-29-authoring-icon-catalog-design.md)

## Goal

Redesign the create/edit command form for Soft GNOME clarity: clear section hierarchy, roomier spacing, header-only Save, and a non-jumping icon picker (popover). Match the approved visual reference.

## Visual reference (authoritative)

**[`docs/superpowers/visuals/2026-07-29-authoring-form-redesign.html`](../visuals/2026-07-29-authoring-form-redesign.html)**

Icon-picker comparison (locked **C**):  
[`docs/superpowers/visuals/2026-07-29-authoring-form-icon-picker.html`](../visuals/2026-07-29-authoring-form-icon-picker.html)

## Decisions

| Topic | Choice |
|-------|--------|
| Scope | **C** — sectioned layout + roomier Soft GNOME polish |
| Actions | **A** — Header ← Back · title · **Save** only (no footer Cancel/Save) |
| Icon picker | **C** — Selected chip + Change… → `Gtk.Popover` 6×6 grid (no layout jump) |
| Sections | Identity · Appearance · Behavior · Script |
| Catalog | Keep 36 emoji; picker ≡ card (unchanged) |

## In scope

- Rebuild `authoring.py` into four cream sections with section titles
- Remove footer Cancel/Save
- Icon: chip + Change… → popover; Escape closes popover first
- CSS for sections, chip, popover grid; roomier spacing
- Window height tuned so Script has meaningful space when popover closed
- Replace/update visual reference HTML for QA
- Preserve: dirty Back discard, validation, emoji catalog, color, toggles, stack Back fix

## Out of scope

- Two-column / tabbed form
- Changing emoji catalog contents
- Packaging / Steps 25–31

## Layout (top → bottom)

1. **Header:** ← Back | Edit/New command | Save  
2. **Identity:** Name | Category; Description  
3. **Appearance:** Icon chip + Change…; Color swatches  
4. **Behavior:** Terminal · Confirm switches  
5. **Script:** monospace TextView (largest share)

## Architecture

```
authoring.py
  header (Back / title / Save)
  section Identity
  section Appearance  → chip + Gtk.Popover(icon grid)
  section Behavior
  section Script
style.css  — .cc-authoring-section, chip, popover glyphs
```

## Behavior details

1. Change… pops popover relative to chip/button; pick sets emoji, updates chip, closes popover.  
2. Escape: if popover open → close it; else → cancel/Back (dirty confirm as today).  
3. No footer action buttons.  
4. Screenshot QA must match visual reference (sections, chip, no footer, Script room).

## Success criteria

- Form reads as four clear sections with Soft GNOME cream chrome  
- Header Save only; no footer Cancel/Save  
- Changing icon does not jump form height  
- Visual QA accepted vs redesign HTML  
