# Soft GNOME CSS Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Deliver Soft GNOME visuals (rounded cards, light elevation, Adwaita-blue hover outline, balanced cards) via CSS-first styling plus light Python hooks.

**Architecture:** Appearance lives in `framework/style.css`. `widgets.py` adds style classes and truncates descriptions. `menu.py` adds window/grid CSS classes and Soft GNOME spacing. Behavior and metadata/launcher stay unchanged.

**Tech Stack:** Python 3, GTK 3 (`gi.repository.Gtk` / `Gdk`), GTK CSS, `unittest`

## Global Constraints

- Soft custom skin, theme-aware: light/dark follow the desktop
- Visual direction: Soft GNOME (rounded cards ~14px radius, light elevation, Adwaita blue hover `#3584e4`)
- Balanced cards: icon + title + short description
- CSS owns colors/spacing/shapes; Python only light hooks (classes, truncation, spacing)
- Keep 3-column grid
- Do not change `metadata.py` or `launcher.py`
- No search/categories/favorites/confirm/status/keyboard features
- No full CommandCard rewrite
- No automated UI test suite (unit tests for pure helpers only)
- Primary themes: Adwaita and Yaru
- Work from repo root: `/home/ramin/CommandCenter`
- Commit after each task with a clear message; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/textutil.py` | Pure `truncate_description(text, max_len=48) -> str` |
| `framework/test_textutil.py` | Unit tests for truncation |
| `framework/widgets.py` | CommandCard: classes + truncation |
| `framework/menu.py` | Window/grid classes + Soft GNOME spacing |
| `framework/style.css` | Soft GNOME appearance |

---

### Task 1: Description truncation helper

**Files:**
- Create: `framework/textutil.py`
- Create: `framework/test_textutil.py`

**Interfaces:**
- Consumes: nothing
- Produces: `truncate_description(text: str, max_len: int = 48) -> str`
  - Empty/`None`-like empty string → `""`
  - If `len(text) <= max_len` → return `text` unchanged
  - Else → return `text[: max_len - 1].rstrip() + "…"` (Unicode ellipsis)
  - Never raise on normal string input

- [x] **Step 1: Write the failing tests**

Create `framework/test_textutil.py`:

```python
#!/usr/bin/env python3

import unittest

from textutil import truncate_description


class TruncateDescriptionTests(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(truncate_description(""), "")

    def test_short_unchanged(self):
        self.assertEqual(
            truncate_description("Start desktop widgets"),
            "Start desktop widgets",
        )

    def test_exact_max_unchanged(self):
        text = "a" * 48
        self.assertEqual(truncate_description(text, 48), text)

    def test_long_truncated_with_ellipsis(self):
        text = "Show automatic update lockdown status for the whole system"
        result = truncate_description(text, 48)
        self.assertTrue(result.endswith("…"))
        self.assertEqual(len(result), 48)
        self.assertFalse(result[:-1].endswith(" "))

    def test_custom_max_len(self):
        self.assertEqual(
            truncate_description("abcdefghij", 5),
            "abcd…",
        )


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run tests to verify they fail**

Run from `framework/`:

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -v
```

Expected: FAIL / ERROR importing `textutil` (module not found) or missing function.

- [x] **Step 3: Write minimal implementation**

Create `framework/textutil.py`:

```python
#!/usr/bin/env python3


def truncate_description(text, max_len=48):
    if not text:
        return ""

    if len(text) <= max_len:
        return text

    if max_len <= 1:
        return "…"[:max_len]

    return text[: max_len - 1].rstrip() + "…"
```

- [x] **Step 4: Run tests to verify they pass**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -v
```

Expected: all 5 tests OK.

- [x] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/textutil.py framework/test_textutil.py
git commit -m "$(cat <<'EOF'
feat: add description truncation helper for balanced cards.

EOF
)"
```

---

### Task 2: CommandCard style classes and truncation

**Files:**
- Modify: `framework/widgets.py`

**Interfaces:**
- Consumes: `truncate_description` from `textutil`
- Produces: `CommandCard` still constructed as `CommandCard(meta)` where `meta` has `name`, `icon`, `desc`
- Style classes on widgets: button `command-card`; title label `command-title`; description label `command-desc`
- Description text shown is `truncate_description(meta["desc"])`
- Empty desc: do not pack description label (same as today)
- Icon fallback unchanged: `application-x-executable`
- Size request: `180` × `130` (Soft GNOME balanced cards)
- Keep vertical box: icon → title → description; title may keep bold markup

- [x] **Step 1: Update `framework/widgets.py` to match this full file**

```python
#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from textutil import truncate_description


class CommandCard(Gtk.Button):

    def __init__(self, meta):

        super().__init__()

        self.set_size_request(
            180,
            130
        )

        self.get_style_context().add_class(
            "command-card"
        )

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )

        box.set_halign(
            Gtk.Align.CENTER
        )

        box.set_valign(
            Gtk.Align.CENTER
        )

        icon = Gtk.Image()

        theme = Gtk.IconTheme.get_default()

        if theme.has_icon(meta["icon"]):

            icon.set_from_icon_name(
                meta["icon"],
                Gtk.IconSize.DIALOG
            )

        else:

            icon.set_from_icon_name(
                "application-x-executable",
                Gtk.IconSize.DIALOG
            )

        title = Gtk.Label(
            label=meta["name"]
        )

        title.set_markup(
            f"<b>{meta['name']}</b>"
        )

        title.get_style_context().add_class(
            "command-title"
        )

        desc_text = truncate_description(
            meta.get("desc", "")
        )

        description = Gtk.Label(
            label=desc_text
        )

        description.set_line_wrap(
            True
        )

        description.set_justify(
            Gtk.Justification.CENTER
        )

        description.set_max_width_chars(
            22
        )

        description.get_style_context().add_class(
            "command-desc"
        )

        box.pack_start(
            icon,
            False,
            False,
            0
        )

        box.pack_start(
            title,
            False,
            False,
            0
        )

        if desc_text:

            box.pack_start(
                description,
                False,
                False,
                0
            )

        self.add(
            box
        )
```

- [x] **Step 2: Sanity-check import**

```bash
cd /home/ramin/CommandCenter/framework && python3 -c "from widgets import CommandCard; print('ok')"
```

Expected: `ok` (may warn about Gtk if no display; import should succeed).

- [x] **Step 3: Re-run unit tests**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -v
```

Expected: all OK.

- [x] **Step 4: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/widgets.py
git commit -m "$(cat <<'EOF'
feat: style-class CommandCard and truncate descriptions.

EOF
)"
```

---

### Task 3: Window and grid Soft GNOME hooks

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: unchanged `CommandCard`, `read_metadata`, `run_command`
- Produces: window style class `command-center-window`; grid style class `command-grid`
- Header action buttons get style class `cc-header-button`
- Border width `18`; grid row/column spacing `12`
- Default size `640` × `540`
- Behavior unchanged (load/refresh/open_folder/run)

- [x] **Step 1: Apply these targeted edits in `framework/menu.py`**

After `super().__init__()` in `CommandCenter.__init__`, add:

```python
        self.get_style_context().add_class(
            "command-center-window"
        )
```

Change size and border:

```python
        self.set_default_size(
            640,
            540
        )
```

```python
        self.set_border_width(
            18
        )
```

After creating `folder_button` (before connect), add:

```python
        folder_button.get_style_context().add_class(
            "cc-header-button"
        )
```

After creating `refresh_button` (before connect), add:

```python
        refresh_button.get_style_context().add_class(
            "cc-header-button"
        )
```

After creating `self.grid`, add class and set spacing to 12:

```python
        self.grid.get_style_context().add_class(
            "command-grid"
        )

        self.grid.set_row_spacing(
            12
        )

        self.grid.set_column_spacing(
            12
        )
```

(Remove the previous 15/15 spacing assignments or replace them with 12.)

- [x] **Step 2: Syntax check**

```bash
python3 -m py_compile /home/ramin/CommandCenter/framework/menu.py
```

Expected: exit 0, no output.

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/menu.py
git commit -m "$(cat <<'EOF'
feat: add Soft GNOME layout hooks on window and header.

EOF
)"
```

---

### Task 4: Soft GNOME `style.css`

**Files:**
- Modify: `framework/style.css` (currently empty)

**Interfaces:**
- Consumes: classes `command-center-window`, `command-grid`, `command-card`, `command-title`, `command-desc`, `cc-header-button`
- Produces: Soft GNOME look — ~14px card radius, light border/elevation, `#3584e4` hover outline, quieter description, rounded header buttons
- Prefer theme colors for surfaces/text; accent mainly on hover
- No heavy animation

- [x] **Step 1: Replace `framework/style.css` with**

```css
/* Soft GNOME — Command Center
   Theme-aware surfaces; accent used for hover outline.
   Targets Adwaita / Yaru (GTK 3).
*/

.command-center-window {
  background-color: @theme_bg_color;
}

.command-grid {
  margin: 4px;
}

.cc-header-button {
  border-radius: 8px;
  padding: 4px;
  min-width: 28px;
  min-height: 28px;
}

.cc-header-button:hover {
  background-color: alpha(@theme_fg_color, 0.08);
}

.command-card {
  border-radius: 14px;
  border: 1px solid alpha(@borders, 0.9);
  padding: 14px 10px;
  background-color: @theme_base_color;
  box-shadow: 0 1px 2px alpha(black, 0.06);
  transition: border-color 100ms ease-in-out;
}

.command-card:hover {
  border-color: #3584e4;
  border-width: 2px;
  background-color: alpha(@theme_selected_bg_color, 0.12);
  box-shadow: 0 4px 12px alpha(#3584e4, 0.18);
}

.command-card:active {
  background-color: alpha(@theme_selected_bg_color, 0.20);
}

.command-title {
  font-weight: bold;
  color: @theme_fg_color;
}

.command-desc {
  font-size: 0.85em;
  color: alpha(@theme_fg_color, 0.65);
  opacity: 0.9;
}
```

- [x] **Step 2: Confirm CSS file is non-empty and loadable**

```bash
test -s /home/ramin/CommandCenter/framework/style.css && wc -l /home/ramin/CommandCenter/framework/style.css
python3 - <<'PY'
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
p = Gtk.CssProvider()
p.load_from_path("/home/ramin/CommandCenter/framework/style.css")
print("css-ok")
PY
```

Expected: line count > 0 and `css-ok`.

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/style.css
git commit -m "$(cat <<'EOF'
feat: apply Soft GNOME CSS for cards and header.

EOF
)"
```

---

### Task 5: Status and plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-23-soft-gnome-css-redesign.md` (mark all tasks `[x]`)

**Interfaces:**
- STATUS stage → `done` for Step 20; next action → Phase 1 Step 21 ready to brainstorm
- Active plan link set; note verification is manual (light/dark launch)

- [x] **Step 1: Update STATUS.md Now / Next action**

Set:

| Field | Value |
|-------|--------|
| Phase | 1 — UI Professionalization |
| Cycle | Step 20 — Professional CSS redesign |
| Stage | `done` |
| Active spec | link to design spec |
| Active plan | link to this plan |

Next action: Begin Step 21 (Search) when ready — stage `ready to brainstorm`.

Roadmap snapshot: Phase 1 still in progress; Step 20 complete.

- [x] **Step 2: Mark every `- [x]` in this plan file as `- [x]`**

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add STATUS.md docs/superpowers/plans/2026-07-23-soft-gnome-css-redesign.md
git commit -m "$(cat <<'EOF'
docs: mark Step 20 Soft GNOME redesign complete in STATUS.

EOF
)"
```

---

## Manual verification (after Task 4; human or agent with display)

1. `cd /home/ramin/CommandCenter/framework && python3 menu.py`
2. Light and dark themes: Soft GNOME cards, blue hover outline
3. Folder / refresh / run scripts
4. Unit tests still pass: `python3 -m unittest test_textutil.py -v`
