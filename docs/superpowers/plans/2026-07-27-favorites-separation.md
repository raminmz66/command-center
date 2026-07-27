# Favorites Section Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Stronger Soft GNOME Favorites panel + larger label so the strip is clearly separated from chips and the main grid (CSS only).

**Architecture:** Update `.cc-favorites-section` and `.cc-favorites-label` in `framework/style.css` to match approved preview v2 (stronger tint/border, 16px label).

**Tech Stack:** GTK 3 CSS

## Global Constraints

- CSS-only; do not change `menu.py` structure or favorites behavior
- Tokens: fill `alpha(@theme_fg_color, 0.07)`; border `1px solid alpha(@borders, 0.9)`; radius 12px; padding 14px; margin 14px 8px 16px; label 16px / 700
- Preserve empty-section hide
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/style.css` | Favorites panel + label |
| `STATUS.md` | Mark 23c done → Step 24 |

---

### Task 1: Favorites panel CSS

**Files:**
- Modify: `framework/style.css`

- [x] **Step 1: Replace Favorites section rules**

Replace existing `.cc-favorites-section` and `.cc-favorites-label` blocks with:

```css
.cc-favorites-section {
  margin: 14px 8px 16px;
  padding: 14px;
  border-radius: 12px;
  background-color: alpha(@theme_fg_color, 0.07);
  border: 1px solid alpha(@borders, 0.9);
}

.cc-favorites-label {
  font-weight: 700;
  font-size: 16px;
  opacity: 0.92;
  margin: 0 4px 12px;
  color: @theme_fg_color;
}
```

- [x] **Step 2: CSS load check**

```bash
python3 - <<'PY'
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
p = Gtk.CssProvider()
p.load_from_path("/home/ramin/CommandCenter/framework/style.css")
print("css-ok")
PY
```

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/style.css
git commit -m "$(cat <<'EOF'
fix: strengthen Favorites panel separation and label size.

EOF
)"
```

---

### Task 2: STATUS + plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-27-favorites-separation.md` (this file)

- [x] **Step 1: STATUS** — Step 23c done; next Step 24 Confirmation `ready to brainstorm`

- [x] **Step 2: Mark all `- [x]` as `- [x]`**

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add STATUS.md docs/superpowers/plans/2026-07-27-favorites-separation.md
git commit -m "$(cat <<'EOF'
docs: mark Favorites separation polish complete in STATUS.

EOF
)"
```

---

## Manual verification

```bash
cd ~/CommandCenter/framework && python3 menu.py
```

Confirm Favorites panel vs chips/main grid; empty hide; Apply/edit still work.
