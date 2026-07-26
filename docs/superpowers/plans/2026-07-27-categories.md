# Categories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Soft GNOME category filter chips under the HeaderBar that AND with search, using dynamic categories with a preferred order.

**Architecture:** Pure helpers `ordered_categories` and `matches_filters` in `textutil.py`; `menu.py` hosts a chip row above the grid and filters via both category + query; Soft GNOME CSS for chips. Sample scripts get `# CATEGORY=` tags.

**Tech Stack:** Python 3, GTK 3, `unittest`

## Global Constraints

- UI: horizontal filter chips under HeaderBar (above card grid)
- Chips: dynamic from scripts + **All**; preferred order Desktop, System, Network, Maintenance, Security, General then extras A–Z
- Default selection: **All**
- Filter: category AND search (`matches_filters`)
- Missing/empty meta category → treat as `General`
- Preserve search focus fix (do not call window `show_all()` on each filter; restore caret without select-all)
- Do not change `widgets.py`, `launcher.py`, `metadata.py`
- Preserve Soft GNOME cards, hover tint, `# COLOR=`
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/textutil.py` | `PREFERRED_CATEGORIES`, `ordered_categories`, `matches_filters` |
| `framework/test_textutil.py` | Unit tests for ordering + filters |
| `framework/menu.py` | Chip row, selection state, filter wiring |
| `framework/style.css` | `.cc-category-chip` idle/active |
| `scripts/*.sh` | Demo `# CATEGORY=` values |
| `STATUS.md` | Mark Step 22 done |

---

### Task 1: Category filter helpers

**Files:**
- Modify: `framework/textutil.py`
- Modify: `framework/test_textutil.py`

**Interfaces:**
- Produces:
  - `PREFERRED_CATEGORIES = ("Desktop", "System", "Network", "Maintenance", "Security", "General")`
  - `ordered_categories(categories) -> list` — unique display names; preferred first (canonical spelling from `PREFERRED_CATEGORIES`); remaining sorted by casefold; empty/whitespace inputs ignored; normalize blank to skip (callers pass raw names)
  - `normalize_category(value) -> str` — strip; empty/None → `"General"`; otherwise return stripped string (preserve caller casing for display from first seen, or use preferred canonical if casefold matches preferred)
  - `matches_filters(meta, query, category) -> bool` — requires `matches_query(meta, query)`; if `category` is None/empty/`"All"` (casefold) → True for category part; else compare `normalize_category(meta.get("category"))` to `normalize_category(category)` casefold

- [ ] **Step 1: Append failing tests** to `framework/test_textutil.py`

Update import:

```python
from textutil import (
    truncate_description,
    normalize_icon_color,
    matches_query,
    ordered_categories,
    matches_filters,
    normalize_category,
)
```

Append:

```python
class NormalizeCategoryTests(unittest.TestCase):

    def test_empty_becomes_general(self):
        self.assertEqual(normalize_category(""), "General")
        self.assertEqual(normalize_category(None), "General")
        self.assertEqual(normalize_category("  "), "General")

    def test_strip(self):
        self.assertEqual(normalize_category("  System  "), "System")


class OrderedCategoriesTests(unittest.TestCase):

    def test_preferred_order(self):
        self.assertEqual(
            ordered_categories(["General", "Desktop", "Security"]),
            ["Desktop", "Security", "General"],
        )

    def test_extras_sorted(self):
        self.assertEqual(
            ordered_categories(["Zoo", "Desktop", "Alpha"]),
            ["Desktop", "Alpha", "Zoo"],
        )

    def test_unique_casefold(self):
        self.assertEqual(
            ordered_categories(["desktop", "Desktop", "System"]),
            ["Desktop", "System"],
        )

    def test_skips_empty(self):
        self.assertEqual(
            ordered_categories(["", None, "Network"]),
            ["Network"],
        )


class MatchesFiltersTests(unittest.TestCase):

    def setUp(self):
        self.meta = {
            "name": "Conky",
            "desc": "Start desktop widgets",
            "category": "Desktop",
        }

    def test_all_with_query(self):
        self.assertTrue(matches_filters(self.meta, "con", "All"))
        self.assertFalse(matches_filters(self.meta, "vpn", "All"))

    def test_category_only(self):
        self.assertTrue(matches_filters(self.meta, "", "Desktop"))
        self.assertFalse(matches_filters(self.meta, "", "System"))

    def test_and_miss(self):
        self.assertFalse(matches_filters(self.meta, "con", "System"))

    def test_category_case_insensitive(self):
        self.assertTrue(matches_filters(self.meta, "", "desktop"))

    def test_missing_category_is_general(self):
        meta = {"name": "X", "desc": ""}
        self.assertTrue(matches_filters(meta, "", "General"))
        self.assertFalse(matches_filters(meta, "", "Desktop"))
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.OrderedCategoriesTests test_textutil.MatchesFiltersTests test_textutil.NormalizeCategoryTests -v
```

Expected: ImportError / AttributeError for new symbols.

- [ ] **Step 3: Implement** in `framework/textutil.py` (append):

```python
PREFERRED_CATEGORIES = (
    "Desktop",
    "System",
    "Network",
    "Maintenance",
    "Security",
    "General",
)

_PREFERRED_BY_CASEFOLD = {
    name.casefold(): name for name in PREFERRED_CATEGORIES
}


def normalize_category(value):
    if value is None:
        return "General"
    text = str(value).strip()
    if not text:
        return "General"
    return _PREFERRED_BY_CASEFOLD.get(text.casefold(), text)


def ordered_categories(categories):
    seen = set()
    unique = []
    for raw in categories or []:
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            continue
        canonical = normalize_category(text)
        key = canonical.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(canonical)

    preferred = [name for name in PREFERRED_CATEGORIES if name.casefold() in seen]
    extras = sorted(
        [name for name in unique if name.casefold() not in _PREFERRED_BY_CASEFOLD],
        key=lambda n: n.casefold(),
    )
    return preferred + extras


def matches_filters(meta, query, category):
    if not matches_query(meta, query):
        return False
    if category is None or not str(category).strip():
        return True
    if str(category).strip().casefold() == "all":
        return True
    meta_cat = normalize_category(meta.get("category") if meta else None)
    want = normalize_category(category)
    return meta_cat.casefold() == want.casefold()
```

- [ ] **Step 4: Run full unit tests — expect PASS**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -v
```

- [ ] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/textutil.py framework/test_textutil.py
git commit -m "$(cat <<'EOF'
feat: add category ordering and matches_filters helpers.

EOF
)"
```

---

### Task 2: Category chips in `menu.py`

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `matches_filters`, `ordered_categories`, `normalize_category` from `textutil`
- `self.selected_category` starts as `"All"`
- `self.chip_box`: `Gtk.FlowBox` (homogeneous False, selection NONE, max children per line high) or `Gtk.Box` with wrap — prefer `Gtk.FlowBox` with `set_selection_mode(NONE)` and button children
- Vertical `self.content` `Gtk.Box` packs `chip_box` then `grid`; window `add(content)` instead of adding grid alone
- `rebuild_category_chips()` clears chip_box, adds All + ordered categories as `Gtk.ToggleButton`s with class `cc-category-chip`, exclusive selection
- `discover_commands` then `rebuild_category_chips`; if `selected_category` not in {All}∪categories → set All
- `render_commands` uses `matches_filters(meta, query, self.selected_category)` instead of `matches_query` alone
- Keep search focus restore behavior; show `chip_box.show_all()` and `grid.show_all()` after rebuilds (not window `show_all`)

- [ ] **Step 1: Update imports**

```python
from textutil import matches_filters, ordered_categories, normalize_category
```

Remove unused `matches_query` import if no longer referenced.

- [ ] **Step 2: In `__init__`, replace `self.add(self.grid)` with content box + chips**

After creating `self.grid` and before `load_commands()`:

```python
        self.selected_category = "All"
        self.chip_buttons = {}

        self.chip_box = Gtk.FlowBox()
        self.chip_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.chip_box.set_max_children_per_line(12)
        self.chip_box.set_min_children_per_line(1)
        self.chip_box.set_homogeneous(False)
        self.chip_box.set_column_spacing(6)
        self.chip_box.set_row_spacing(6)
        self.chip_box.set_halign(Gtk.Align.START)
        self.chip_box.get_style_context().add_class("cc-category-bar")

        self.content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
        )
        self.content.pack_start(self.chip_box, False, False, 0)
        self.content.pack_start(self.grid, True, True, 0)
        self.add(self.content)
```

Remove the old `self.add(self.grid)` call.

- [ ] **Step 3: Add chip rebuild + click handlers; wire discover/load/render**

```python
    def rebuild_category_chips(self):
        for child in self.chip_box.get_children():
            self.chip_box.remove(child)
        self.chip_buttons = {}

        cats = []
        for _path, meta in self.commands:
            cats.append(normalize_category(meta.get("category")))
        labels = ["All"] + ordered_categories(cats)

        if (
            self.selected_category != "All"
            and self.selected_category.casefold()
            not in {c.casefold() for c in labels[1:]}
        ):
            self.selected_category = "All"

        for label in labels:
            button = Gtk.ToggleButton(label=label)
            button.get_style_context().add_class("cc-category-chip")
            button.set_can_focus(False)
            active = label.casefold() == self.selected_category.casefold()
            button.set_active(active)
            if active:
                button.get_style_context().add_class("active")
            button.connect("toggled", self.on_category_toggled, label)
            self.chip_box.add(button)
            self.chip_buttons[label] = button

        self.chip_box.show_all()

    def on_category_toggled(self, button, label):
        if not button.get_active():
            # Prevent fully clearing selection — re-assert if user clicks active chip off
            if label.casefold() == self.selected_category.casefold():
                button.handler_block_by_func(self.on_category_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(self.on_category_toggled)
            return
        self.selected_category = label
        for name, other in self.chip_buttons.items():
            is_sel = name.casefold() == label.casefold()
            if other is not button:
                other.handler_block_by_func(self.on_category_toggled)
                other.set_active(False)
                other.handler_unblock_by_func(self.on_category_toggled)
            ctx = other.get_style_context()
            if is_sel:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")
        self.render_commands()
```

Update `discover`/`load`/`render`:

```python
    def load_commands(self):
        self.discover_commands()
        self.rebuild_category_chips()
        self.render_commands()
```

In `render_commands`, replace `matches_query` check with:

```python
            if not matches_filters(meta, query, self.selected_category):
                continue
```

- [ ] **Step 4: Syntax + unit tests**

```bash
python3 -m py_compile /home/ramin/CommandCenter/framework/menu.py
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -q
```

- [ ] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/menu.py
git commit -m "$(cat <<'EOF'
feat: add category filter chips with search AND filtering.

EOF
)"
```

---

### Task 3: Soft GNOME chip CSS + sample `# CATEGORY=`

**Files:**
- Modify: `framework/style.css`
- Modify: `scripts/conky.sh`, `scripts/test-terminal.sh`, `scripts/update-lockdown-status.sh`

- [ ] **Step 1: Append CSS**

```css
.cc-category-bar {
  margin: 0 2px 2px;
}

.cc-category-chip {
  border-radius: 999px;
  padding: 4px 12px;
  border: 1px solid alpha(@borders, 0.9);
  background-color: @theme_base_color;
  color: @theme_fg_color;
  font-weight: 600;
  box-shadow: none;
}

.cc-category-chip:hover {
  background-color: alpha(@theme_fg_color, 0.06);
}

.cc-category-chip:checked,
.cc-category-chip.active {
  background-color: #3584e4;
  border-color: #3584e4;
  color: white;
}

.cc-category-chip:checked:hover,
.cc-category-chip.active:hover {
  background-color: #1c71d8;
  border-color: #1c71d8;
  color: white;
}
```

- [ ] **Step 2: Add CATEGORY lines to samples**

`scripts/conky.sh` — add `# CATEGORY=Desktop` (near other metadata).

`scripts/test-terminal.sh` — add `# CATEGORY=System`.

`scripts/update-lockdown-status.sh` — add `# CATEGORY=Security`.

- [ ] **Step 3: CSS load check**

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

- [ ] **Step 4: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/style.css scripts/conky.sh scripts/test-terminal.sh scripts/update-lockdown-status.sh
git commit -m "$(cat <<'EOF'
feat: style category chips and tag sample script categories.

EOF
)"
```

---

### Task 4: STATUS + plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-27-categories.md` (this file)

- [ ] **Step 1: Update STATUS** — Cycle Step 22 `done`; next Step 23 Favorites `ready to brainstorm`; active spec/plan links for Step 22; note manual QA for chips.

- [ ] **Step 2: Mark every `- [ ]` in this plan as `- [x]`**

- [ ] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add STATUS.md docs/superpowers/plans/2026-07-27-categories.md
git commit -m "$(cat <<'EOF'
docs: mark Step 22 categories complete in STATUS.

EOF
)"
```

---

## Manual verification (human)

```bash
cd ~/CommandCenter/framework && python3 menu.py
```

Check chips All / Desktop / System / Security; category filter; search AND; multi-char search still works; Soft GNOME + colors.
