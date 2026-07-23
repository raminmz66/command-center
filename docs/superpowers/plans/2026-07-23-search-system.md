# Search System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. (Completed tasks marked `- [x]`.)

**Goal:** Add HeaderBar `Gtk.SearchEntry` that instantly filters command cards by name + description, with focus on open and `Ctrl+F` / `/`.

**Architecture:** Pure `matches_query` in `textutil.py`; `menu.py` keeps `(path, meta)` list, filters, rebuilds the 3-column grid; Soft GNOME CSS for `.cc-search-entry`.

**Tech Stack:** Python 3, GTK 3, `unittest`

## Global Constraints

- Placement: HeaderBar search (Soft GNOME)
- Match: case-insensitive substring on `name` OR `desc`
- Empty query → all cards; Escape clears query (focus stays)
- Focus on open; accelerators `Ctrl+F` and `/`
- Do not change `widgets.py`, `launcher.py`, `metadata.py`
- Preserve Soft GNOME cards, hover tint, `# COLOR=`
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push

## File structure

| File | Responsibility |
|------|----------------|
| `framework/textutil.py` | Add `matches_query` |
| `framework/test_textutil.py` | Tests for `matches_query` |
| `framework/menu.py` | SearchEntry, filter, rebuild grid, shortcuts |
| `framework/style.css` | `.cc-search-entry` Soft GNOME styles |
| `STATUS.md` | Mark Step 21 done |

---

### Task 1: `matches_query` helper

**Files:**
- Modify: `framework/textutil.py`
- Modify: `framework/test_textutil.py`

**Interfaces:**
- Produces: `matches_query(meta, query) -> bool`
  - Whitespace-only / empty query → `True`
  - Casefold substring on `meta.get("name","")` or `meta.get("desc","")`
  - Missing keys → treat as `""`

- [x] **Step 1: Append failing tests** to `framework/test_textutil.py`:

```python
from textutil import truncate_description, normalize_icon_color, matches_query


class MatchesQueryTests(unittest.TestCase):

    def setUp(self):
        self.meta = {
            "name": "Conky",
            "desc": "Start desktop widgets",
        }

    def test_empty_query_matches(self):
        self.assertTrue(matches_query(self.meta, ""))
        self.assertTrue(matches_query(self.meta, "   "))

    def test_name_hit(self):
        self.assertTrue(matches_query(self.meta, "con"))

    def test_desc_hit(self):
        self.assertTrue(matches_query(self.meta, "widgets"))

    def test_miss(self):
        self.assertFalse(matches_query(self.meta, "vpn"))

    def test_case_insensitive(self):
        self.assertTrue(matches_query(self.meta, "CONKY"))

    def test_missing_desc(self):
        self.assertTrue(matches_query({"name": "Backup"}, "back"))
        self.assertFalse(matches_query({"name": "Backup"}, "widgets"))
```

Update the import line at the top of the test file accordingly.

- [x] **Step 2: Run tests — expect FAIL**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.MatchesQueryTests -v
```

Expected: ImportError or AttributeError for `matches_query`.

- [x] **Step 3: Implement** in `framework/textutil.py`:

```python
def matches_query(meta, query):
    if query is None or not str(query).strip():
        return True

    needle = str(query).casefold()
    name = str(meta.get("name") or "").casefold()
    desc = str(meta.get("desc") or "").casefold()
    return needle in name or needle in desc
```

- [x] **Step 4: Run tests — expect PASS**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -v
```

Expected: all OK (existing + new).

- [x] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/textutil.py framework/test_textutil.py
git commit -m "$(cat <<'EOF'
feat: add matches_query helper for command search.

EOF
)"
```

---

### Task 2: HeaderBar search + filter in `menu.py`

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `matches_query` from `textutil`
- `self.commands`: list of `(path, meta)` dict pairs
- `self.search_entry`: `Gtk.SearchEntry`
- `discover_commands()` fills `self.commands` from `SCRIPTS_DIR`
- `render_commands()` clears grid and attaches cards for commands matching current query
- `load_commands()` = discover + render
- Escape on search entry clears text
- `Ctrl+F` and `/` focus search (window key-press or accel group)
- Focus search after `show_all` / `map-event` or idle add

- [x] **Step 1: Update imports**

```python
from gi.repository import Gtk, Gdk, GLib
from textutil import matches_query
```

- [x] **Step 2: In `__init__`, after header setup, before grid:**

Replace the simple title-only header packing end-state with search entry. Keep folder/refresh `pack_start`. After packing refresh:

```python
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search commands…")
        self.search_entry.get_style_context().add_class("cc-search-entry")
        self.search_entry.set_hexpand(True)
        self.search_entry.set_size_request(220, -1)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.search_entry.connect("key-press-event", self.on_search_key_press)
        header.pack_end(self.search_entry)

        self.commands = []
```

Keep `header.set_title` / `set_subtitle` as today (search sits on the end).

- [x] **Step 3: Replace `load_commands` with discover + render**

```python
    def discover_commands(self):
        self.commands = []
        if not os.path.exists(SCRIPTS_DIR):
            return
        for file in sorted(os.listdir(SCRIPTS_DIR)):
            if not file.endswith(".sh"):
                continue
            path = os.path.join(SCRIPTS_DIR, file)
            meta = read_metadata(path)
            self.commands.append((path, meta))

    def render_commands(self):
        self.clear_grid()
        query = ""
        if hasattr(self, "search_entry") and self.search_entry is not None:
            query = self.search_entry.get_text()
        row = 0
        col = 0
        for path, meta in self.commands:
            if not matches_query(meta, query):
                continue
            card = CommandCard(meta)
            card.connect("clicked", run_command, path, meta["terminal"])
            self.grid.attach(card, col, row, 1, 1)
            col += 1
            if col == 3:
                col = 0
                row += 1
        self.show_all()

    def load_commands(self):
        self.discover_commands()
        self.render_commands()

    def on_search_changed(self, entry):
        self.render_commands()

    def on_search_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.search_entry.set_text("")
            return True
        return False

    def focus_search(self, *args):
        self.search_entry.grab_focus()
        return True

    def on_window_key_press(self, widget, event):
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval in (Gdk.KEY_f, Gdk.KEY_F):
            return self.focus_search()
        # Slash focuses search when not already typing in the entry
        if event.keyval == Gdk.KEY_slash and not self.search_entry.is_focus():
            return self.focus_search()
        return False
```

After creating the window content, connect:

```python
        self.connect("key-press-event", self.on_window_key_press)
        self.connect("map-event", lambda *a: GLib.idle_add(self.focus_search) or False)
```

Or after `load_commands()` in `__init__`:

```python
        GLib.idle_add(self.focus_search)
```

- [x] **Step 4: Syntax check**

```bash
python3 -m py_compile /home/ramin/CommandCenter/framework/menu.py
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_textutil.py -q
```

Expected: exit 0.

- [x] **Step 5: Commit**

```bash
cd /home/ramin/CommandCenter
git add framework/menu.py
git commit -m "$(cat <<'EOF'
feat: add HeaderBar search with live command filtering.

EOF
)"
```

---

### Task 3: Soft GNOME search CSS

**Files:**
- Modify: `framework/style.css`

**Interfaces:**
- Style class `cc-search-entry` (and `entry.cc-search-entry` if needed)

- [x] **Step 1: Append to `framework/style.css`:**

```css
entry.cc-search-entry,
.cc-search-entry {
  border-radius: 10px;
  border: 1px solid alpha(@borders, 0.9);
  padding: 4px 8px;
  min-width: 180px;
  background-color: @theme_base_color;
  box-shadow: inset 0 1px 2px alpha(black, 0.04);
}

entry.cc-search-entry:focus,
.cc-search-entry:focus {
  border-color: #3584e4;
}
```

- [x] **Step 2: Load CSS check**

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
feat: style HeaderBar search entry for Soft GNOME.

EOF
)"
```

---

### Task 4: STATUS + plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-23-search-system.md` (this file)

- [x] **Step 1: Set STATUS** — Cycle Step 21 stage `done`; next Step 22 Categories `ready to brainstorm`; note search accepted pending manual QA.

- [x] **Step 2: Mark all `- [ ]` in this plan as `- [x]`**

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add STATUS.md docs/superpowers/plans/2026-07-23-search-system.md
git commit -m "$(cat <<'EOF'
docs: mark Step 21 search complete in STATUS.

EOF
)"
```

---

## Manual verification (human)

```bash
cd ~/CommandCenter/framework && python3 menu.py
```

Type `con`, Escape, `Ctrl+F`, `/`; confirm Soft GNOME + colors still work.
