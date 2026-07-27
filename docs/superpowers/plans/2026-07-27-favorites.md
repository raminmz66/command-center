# Favorites Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add an in-app Favorites strip above the main grid, toggled via edit mode, persisted to JSON under `~/.config/command-center/`.

**Architecture:** Pure `favorites.py` for load/save/toggle by script basename; `menu.py` owns edit mode, dual render (Favorites strip + filtered main grid), and click wiring; `CommandCard` shows a display-only star in edit mode; Soft GNOME CSS for section/edit/star.

**Tech Stack:** Python 3, GTK 3, `unittest`, JSON

## Global Constraints

- Persist basenames in `~/.config/command-center/favorites.json` (XDG: `os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "command-center", "favorites.json")`)
- Favorites section above main grid; hide when empty
- Favorited cards also appear in main grid when filters match
- Favorites strip ignores category + search
- Edit mode: card click toggles favorite (no launch); star is display-only
- Normal mode: card click launches
- Preserve search focus fix (no window `show_all()` on rebuild; restore caret)
- Preserve Soft GNOME cards, category chips, hover tint, `# COLOR=`
- Do not change `launcher.py` or `metadata.py`
- No `# FAVORITE=` metadata in v1
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/favorites.py` | Config path, load/save/is_favorite/toggle_favorite |
| `framework/test_favorites.py` | Unit tests with temp config dir |
| `framework/widgets.py` | Star indicator on `CommandCard` (edit mode) |
| `framework/menu.py` | Edit toggle, Favorites strip, dual render, click wiring |
| `framework/style.css` | Section / edit button / star styles |
| `STATUS.md` | Mark Step 23 done → next cycle |

---

### Task 1: `favorites.py` + unit tests

**Files:**
- Create: `framework/favorites.py`
- Create: `framework/test_favorites.py`

**Interfaces:**
- Produces:
  - `favorites_path() -> str`
  - `load_favorites() -> list[str]`
  - `save_favorites(names: list) -> None` — creates parent dirs; on OSError leave file unchanged (caller keeps memory)
  - `is_favorite(basename: str) -> bool`
  - `toggle_favorite(basename: str, known: set|list|None = None) -> bool` — add append / remove; if `known` provided, prune to members of `known` before save; returns new favorited state; on save failure return previous logical state after reload attempt or keep list without writing (tests: writable path)

- [x] **Step 1: Write failing tests** in `framework/test_favorites.py`

```python
#!/usr/bin/env python3
import json
import os
import tempfile
import unittest
from unittest import mock

import favorites


class FavoritesTests(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.cfg = os.path.join(self._tmpdir.name, "command-center", "favorites.json")
        self.patcher = mock.patch.object(favorites, "favorites_path", return_value=self.cfg)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_missing_file_is_empty(self):
        self.assertEqual(favorites.load_favorites(), [])

    def test_corrupt_json_is_empty(self):
        os.makedirs(os.path.dirname(self.cfg), exist_ok=True)
        with open(self.cfg, "w", encoding="utf-8") as fh:
            fh.write("{not-json")
        self.assertEqual(favorites.load_favorites(), [])

    def test_round_trip(self):
        favorites.save_favorites(["a.sh", "b.sh"])
        self.assertEqual(favorites.load_favorites(), ["a.sh", "b.sh"])

    def test_toggle_add_append(self):
        favorites.save_favorites(["a.sh"])
        self.assertTrue(favorites.toggle_favorite("b.sh"))
        self.assertEqual(favorites.load_favorites(), ["a.sh", "b.sh"])

    def test_toggle_remove(self):
        favorites.save_favorites(["a.sh", "b.sh"])
        self.assertFalse(favorites.toggle_favorite("a.sh"))
        self.assertEqual(favorites.load_favorites(), ["b.sh"])

    def test_is_favorite(self):
        favorites.save_favorites(["x.sh"])
        self.assertTrue(favorites.is_favorite("x.sh"))
        self.assertFalse(favorites.is_favorite("y.sh"))

    def test_toggle_prunes_unknown_when_known_given(self):
        favorites.save_favorites(["gone.sh", "keep.sh"])
        self.assertTrue(favorites.toggle_favorite("new.sh", known={"keep.sh", "new.sh"}))
        self.assertEqual(favorites.load_favorites(), ["keep.sh", "new.sh"])

    def test_non_list_json_is_empty(self):
        os.makedirs(os.path.dirname(self.cfg), exist_ok=True)
        with open(self.cfg, "w", encoding="utf-8") as fh:
            json.dump({"a": 1}, fh)
        self.assertEqual(favorites.load_favorites(), [])


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run tests — expect FAIL**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_favorites.py -v
```

Expected: ImportError or failures (module missing).

- [x] **Step 3: Implement** `framework/favorites.py`

```python
#!/usr/bin/env python3
import json
import os


def favorites_path():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "command-center", "favorites.json")


def load_favorites():
    path = favorites_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for item in data:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def save_favorites(names):
    path = favorites_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(list(names), fh, indent=2)
            fh.write("\n")
    except OSError:
        return


def is_favorite(basename):
    return basename in load_favorites()


def toggle_favorite(basename, known=None):
    names = load_favorites()
    if basename in names:
        names = [n for n in names if n != basename]
        now = False
    else:
        names = names + [basename]
        now = True
    if known is not None:
        known_set = set(known)
        names = [n for n in names if n in known_set]
    save_favorites(names)
    return now
```

- [x] **Step 4: Run tests — expect PASS**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_favorites.py -v
```

- [x] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/favorites.py framework/test_favorites.py
git commit -m "$(cat <<'EOF'
feat: add favorites JSON persistence helpers.

EOF
)"
```

---

### Task 2: Star display on `CommandCard`

**Files:**
- Modify: `framework/widgets.py`

**Interfaces:**
- Consumes: none from Task 1 at runtime (menu will pass flags)
- Produces: `CommandCard(meta, favorited=False, edit_mode=False)` — when `edit_mode` is True, show a `Gtk.Label` with class `cc-favorite-star` (and `favorited` class when favorited) displaying ★ / ☆; label must not be a separate button (whole card remains click target)

- [x] **Step 1: Update `CommandCard.__init__` signature and star UI**

Change:

```python
class CommandCard(Gtk.Button):

    def __init__(self, meta, favorited=False, edit_mode=False):
```

After creating `box` (vertical), if `edit_mode`, create star label first (or overlay at top). Preferred structure: put star in a horizontal header row above icon, or pack star as first child with `halign=END`:

```python
        if edit_mode:
            star = Gtk.Label(label="★" if favorited else "☆")
            star.get_style_context().add_class("cc-favorite-star")
            if favorited:
                star.get_style_context().add_class("favorited")
            star.set_halign(Gtk.Align.END)
            star.set_valign(Gtk.Align.START)
            box.pack_start(star, False, False, 0)
```

Keep existing icon/title/desc packing. Do not connect star to any signal.

- [x] **Step 2: Syntax check**

```bash
python3 -m py_compile /home/ramin/CommandCenter/framework/widgets.py
```

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/widgets.py
git commit -m "$(cat <<'EOF'
feat: show display-only favorite star on cards in edit mode.

EOF
)"
```

---

### Task 3: Favorites strip + edit mode in `menu.py`

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `load_favorites`, `toggle_favorite`, `is_favorite` from `favorites`; `CommandCard(..., favorited=, edit_mode=)`
- Produces: working edit toggle, Favorites section, dual render, edit-vs-launch click wiring

- [x] **Step 1: Imports + state**

```python
from favorites import load_favorites, toggle_favorite, is_favorite
```

In `__init__` after `self.commands = []`:

```python
        self.favorites = load_favorites()
        self.edit_favorites = False
```

- [x] **Step 2: HeaderBar edit button**

After packing `refresh_button` (before search), add:

```python
        self.edit_fav_button = Gtk.Button()
        self.edit_fav_button.set_tooltip_text("Edit favorites")
        self.edit_fav_button.get_style_context().add_class("cc-header-button")
        self.edit_fav_button.get_style_context().add_class("cc-edit-favorites")
        self._sync_edit_fav_button()
        self.edit_fav_button.connect("clicked", self.on_edit_favorites_clicked)
        header.pack_start(self.edit_fav_button)
```

Helpers:

```python
    def _sync_edit_fav_button(self):
        if self.edit_favorites:
            self.edit_fav_button.set_label("Done")
            self.edit_fav_button.set_image(None)
            self.edit_fav_button.set_tooltip_text("Finish editing favorites")
            self.edit_fav_button.get_style_context().add_class("active")
        else:
            icon = Gtk.Image.new_from_icon_name(
                "starred-symbolic",
                Gtk.IconSize.BUTTON,
            )
            self.edit_fav_button.set_label(None)
            self.edit_fav_button.set_image(icon)
            self.edit_fav_button.set_tooltip_text("Edit favorites")
            self.edit_fav_button.get_style_context().remove_class("active")

    def on_edit_favorites_clicked(self, *_args):
        self.edit_favorites = not self.edit_favorites
        self._sync_edit_fav_button()
        self.render_commands()
```

If `starred-symbolic` missing on some themes, fallback `"emblem-favorite-symbolic"` or `"starred"` via IconTheme check similar to widgets.

- [x] **Step 3: Favorites section widgets in layout**

Replace content packing so order is: chips → favorites_box → grid:

```python
        self.favorites_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.favorites_box.get_style_context().add_class("cc-favorites-section")
        self.favorites_label = Gtk.Label(label="Favorites", xalign=0)
        self.favorites_label.get_style_context().add_class("cc-favorites-label")
        self.favorites_grid = Gtk.Grid()
        self.favorites_grid.set_row_spacing(12)
        self.favorites_grid.set_column_spacing(12)
        self.favorites_grid.set_halign(Gtk.Align.CENTER)
        self.favorites_box.pack_start(self.favorites_label, False, False, 0)
        self.favorites_box.pack_start(self.favorites_grid, False, False, 0)

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.content.pack_start(self.chip_box, False, False, 0)
        self.content.pack_start(self.favorites_box, False, False, 0)
        self.content.pack_start(self.grid, True, True, 0)
        self.add(self.content)
```

- [x] **Step 4: Render + click wiring**

Add:

```python
    def _known_basenames(self):
        return {os.path.basename(path) for path, _meta in self.commands}

    def _clear_container(self, container):
        for child in container.get_children():
            container.remove(child)

    def _attach_cards(self, container, items, columns=3):
        self._clear_container(container)
        row = col = 0
        for path, meta in items:
            basename = os.path.basename(path)
            favorited = basename in self.favorites
            card = CommandCard(
                meta,
                favorited=favorited,
                edit_mode=self.edit_favorites,
            )
            card.set_can_focus(False)
            if self.edit_favorites:
                card.connect("clicked", self.on_favorite_card_clicked, path)
            else:
                card.connect("clicked", run_command, path, meta["terminal"])
            container.attach(card, col, row, 1, 1)
            col += 1
            if col == columns:
                col = 0
                row += 1

    def on_favorite_card_clicked(self, _button, path):
        basename = os.path.basename(path)
        toggle_favorite(basename, known=self._known_basenames())
        self.favorites = load_favorites()
        self.render_commands()
```

Rewrite `render_commands` to:

1. Preserve search focus/caret as today
2. Build `by_base = {os.path.basename(p): (p, m) for p, m in self.commands}`
3. Favorites items: for each name in `self.favorites`, if in `by_base`, append (ignore filters)
4. If favorites items empty: `self.favorites_box.hide()` else show + `_attach_cards(self.favorites_grid, fav_items)`
5. Main items: filter with `matches_filters` as today; `_attach_cards(self.grid, main_items)`
6. `self.favorites_box.show_all()` only when visible; `self.grid.show_all()`; restore search focus

Update `load_commands` / `refresh` to `self.favorites = load_favorites()` before render.

- [x] **Step 5: Verify**

```bash
python3 -m py_compile /home/ramin/CommandCenter/framework/menu.py
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_favorites.py test_textutil.py -q
```

- [x] **Step 6: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/menu.py
git commit -m "$(cat <<'EOF'
feat: add favorites strip and edit-mode toggle in menu.

EOF
)"
```

---

### Task 4: Soft GNOME CSS + STATUS + plan checkboxes

**Files:**
- Modify: `framework/style.css`
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-27-favorites.md` (this file — mark all steps `[x]`)

- [x] **Step 1: Append CSS**

```css
.cc-favorites-section {
  margin: 2px 4px 6px;
}

.cc-favorites-label {
  font-weight: 700;
  font-size: 0.85em;
  opacity: 0.75;
  margin: 0 4px 2px;
}

.cc-edit-favorites.active {
  background-color: #f6c32a;
  color: #1a1a1a;
  border-radius: 6px;
}

.cc-favorite-star {
  font-size: 14px;
  color: alpha(@theme_fg_color, 0.35);
  margin: 0 4px;
}

.cc-favorite-star.favorited {
  color: #f6c32a;
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

- [x] **Step 3: Update STATUS**

- Cycle Step 23 Favorites → done conceptually; next action: Phase 1 complete or ready for Phase 2 / next roadmap step
- Per roadmap, Step 23 is last of Phase 1 UI Professionalization — set Cycle to note Phase 1 complete / ready for Phase 2 Step 24 Confirmation, stage `ready to brainstorm`
- Active spec/plan: favorites (completed)
- Note manual QA pending for favorites edit/persist/strip

- [x] **Step 4: Mark every `- [x]` in this plan as `- [x]`**

- [x] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/style.css STATUS.md docs/superpowers/plans/2026-07-27-favorites.md
git commit -m "$(cat <<'EOF'
docs: mark Step 23 favorites complete in STATUS.

EOF
)"
```

---

## Manual verification (human)

```bash
cd ~/CommandCenter/framework && python3 menu.py
```

1. Click star header → Done label; click cards → stars toggle; no script runs  
2. Done → Favorites section shows starred; same cards still in main grid  
3. Category/search do not shrink Favorites strip  
4. Empty favorites → section hidden  
5. Search multi-char + chips + Soft GNOME + `# COLOR=` still work
