# Arrow + Enter on cards — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Arrow-key card highlight while search keeps focus; Enter runs highlighted card; Esc clears highlight first.

**Architecture:** Pure `nav.py` computes next index. `menu.py` keeps an ordered list of visible cards, applies CSS class `keyboard-focus`, handles keys in search + window handlers. No GTK focus on cards.

**Tech Stack:** Python 3, PyGObject GTK3, unittest, CSS

**Spec:** [docs/superpowers/specs/2026-08-08-arrow-enter-cards-design.md](../specs/2026-08-08-arrow-enter-cards-design.md)

## Global Constraints

- Search caret stays in search; cards `can_focus=False`
- Favorites then main in one sequence
- No highlight until first arrow; clear on render/filter
- Esc clears highlight before search/close ladder
- Enter uses same launch path as click (incl. confirm)
- Disable nav/launch in edit_commands, edit_favorites, authoring
- Commit after each task; QA via screenshot

## File map

| File | Role |
|------|------|
| `framework/nav.py` | `next_highlight_index(...)` |
| `framework/test_nav.py` | Unit tests |
| `framework/menu.py` | State, keys, apply class, Enter/Esc |
| `framework/style.css` | `.command-card.keyboard-focus` |
| `STATUS.md` | Cycle gate |

---

### Task 1: `nav.py` + tests

**Files:**
- Create: `framework/nav.py`
- Create: `framework/test_nav.py`

**Interfaces:**
- Produces: `next_highlight_index(current: int|None, key: str, n: int, columns: int = 3) -> int|None`
- `key` in `{"Left","Right","Up","Down"}`; returns `None` if `n==0`

- [ ] **Step 1: Write failing tests**

```python
# framework/test_nav.py
import unittest
from nav import next_highlight_index

class NavTest(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(next_highlight_index(None, "Down", 0))

    def test_first_down_right(self):
        self.assertEqual(next_highlight_index(None, "Down", 5), 0)
        self.assertEqual(next_highlight_index(None, "Right", 5), 0)

    def test_first_up_left(self):
        self.assertEqual(next_highlight_index(None, "Up", 5), 4)
        self.assertEqual(next_highlight_index(None, "Left", 5), 4)

    def test_horizontal(self):
        self.assertEqual(next_highlight_index(1, "Right", 5), 2)
        self.assertEqual(next_highlight_index(0, "Left", 5), 0)

    def test_vertical(self):
        self.assertEqual(next_highlight_index(0, "Down", 6, columns=3), 3)
        self.assertEqual(next_highlight_index(4, "Up", 6, columns=3), 1)
        self.assertEqual(next_highlight_index(5, "Down", 6, columns=3), 5)
```

- [ ] **Step 2:** `cd framework && python3 -m unittest test_nav -v` — FAIL

- [ ] **Step 3: Implement**

```python
# framework/nav.py
def next_highlight_index(current, key, n, columns=3):
    if n <= 0:
        return None
    if current is None:
        if key in ("Up", "Left"):
            return n - 1
        return 0
    if key == "Right":
        return min(current + 1, n - 1)
    if key == "Left":
        return max(current - 1, 0)
    if key == "Down":
        return min(current + columns, n - 1)
    if key == "Up":
        return max(current - columns, 0)
    return current
```

- [ ] **Step 4:** Tests PASS

- [ ] **Step 5: Commit** `feat: add keyboard highlight index helper.`

---

### Task 2: CSS + menu highlight plumbing

**Files:**
- Modify: `framework/style.css`
- Modify: `framework/menu.py`

- [ ] **Step 1:** Add CSS:

```css
button.command-card.keyboard-focus {
  border-color: #3584e4;
  border-width: 2px;
  background-color: alpha(@theme_selected_bg_color, 0.14);
  box-shadow: 0 4px 12px alpha(#3584e4, 0.22);
}
```

- [ ] **Step 2:** In `CommandCenter.__init__` (after grids): `self._nav_cards = []`, `self._highlight_index = None`

- [ ] **Step 3:** After `_attach_cards` for favorites and main in `render_commands`, rebuild `_nav_cards` as list of card widgets in order (favorites children then main). Clear highlight via `_set_highlight(None)` at start of `render_commands`.

- [ ] **Step 4:** Add helpers:

```python
def _clear_highlight(self):
    self._set_highlight(None)

def _set_highlight(self, index):
    for i, card in enumerate(self._nav_cards):
        ctx = card.get_style_context()
        if index is not None and i == index:
            ctx.add_class("keyboard-focus")
        else:
            ctx.remove_class("keyboard-focus")
    self._highlight_index = index

def _nav_enabled(self):
    if self.stack.get_visible_child_name() == "authoring":
        return False
    if self.edit_commands or self.edit_favorites:
        return False
    return True

def _move_highlight(self, key):
    if not self._nav_enabled():
        return False
    n = len(self._nav_cards)
    nxt = next_highlight_index(self._highlight_index, key, n, columns=3)
    if nxt is None:
        return False
    self._set_highlight(nxt)
    return True

def _activate_highlight(self):
    if not self._nav_enabled():
        return False
    if self._highlight_index is None:
        return False
    if not (0 <= self._highlight_index < len(self._nav_cards)):
        return False
    card = self._nav_cards[self._highlight_index]
    path = getattr(card, "_cc_script_path", None)
    if path is None:
        return False
    meta = None
    for p, m in self.commands:
        if p == path:
            meta = m
            break
    if meta is None:
        return False
    self.on_command_clicked(card, path, meta)
    return True
```

Rebuild `_nav_cards` inside `render_commands` after attaching both grids (iterate `favorites_grid.get_children()` then `grid.get_children()` — Gtk.Grid child order may not be visual order; prefer collecting during `_attach_cards`).

**Prefer:** change `_attach_cards` to return list of cards attached, then:

```python
fav_cards = self._attach_cards(...) if fav else []
main_cards = self._attach_cards(...)
self._nav_cards = list(fav_cards) + list(main_cards)
```

- [ ] **Step 5: Commit** `feat: wire card keyboard-focus highlight state and CSS.`

---

### Task 3: Key handling (arrows, Enter, Esc)

**Files:**
- Modify: `framework/menu.py`

- [ ] **Step 1:** Import `next_highlight_index` from `nav` (if not already). Map Gdk keys:

```python
_ARROW = {
    Gdk.KEY_Up: "Up", Gdk.KEY_KP_Up: "Up",
    Gdk.KEY_Down: "Down", Gdk.KEY_KP_Down: "Down",
    Gdk.KEY_Left: "Left", Gdk.KEY_KP_Left: "Left",
    Gdk.KEY_Right: "Right", Gdk.KEY_KP_Right: "Right",
}
```

- [ ] **Step 2:** In `on_search_key_press`, before Esc:

```python
key = _ARROW.get(event.keyval)
if key and self._move_highlight(key):
    return True
if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
    if self._activate_highlight():
        return True
if event.keyval == Gdk.KEY_Escape:
    if self._highlight_index is not None:
        self._clear_highlight()
        return True
    return self._escape_main_launcher()
```

- [ ] **Step 3:** In `on_window_key_press`, when search does **not** have focus (or always for arrows when nav enabled), handle same arrows/Enter/Esc-highlight before existing logic. Simplest: extract `_handle_launcher_nav_keys(event) -> bool` used from both handlers.

- [ ] **Step 4:** Update `_escape_main_launcher` — highlight already cleared in search handler; if called with highlight still set, clear first:

```python
if self._highlight_index is not None:
    self._clear_highlight()
    return True
```

- [ ] **Step 5: Commit** `feat: arrow-navigate cards and Enter to run from search.`

---

### Task 4: QA screenshot + STATUS

**Files:**
- Modify: `framework/menu.py` (`on_map_event` QA)
- Modify: `STATUS.md`

- [ ] **Step 1:** If `CC_QA_NAV=1`, after show: timeout to `_move_highlight("Down")` then shot (existing `CC_QA_SHOT`).

- [ ] **Step 2:** Run:

```bash
cd framework
# kill stray menu if needed
CC_QA_NAV=1 CC_QA_SHOT=/home/ramin/CommandCenter/.superpowers/qa/arrow-enter-highlight.png \
  python3 menu.py
```

Verify PNG shows blue highlight on first card.

- [ ] **Step 3:** Mark cycle done in `STATUS.md`; advance backlog pointer to item 2 as next.

- [ ] **Step 4: Commit** `docs: QA arrow-enter highlight; mark cycle done.`

---

## Spec coverage

| Spec | Task |
|------|------|
| Index helper + first arrow | 1 |
| CSS + card list + clear on render | 2 |
| Arrows / Enter / Esc | 3 |
| Screenshot QA + STATUS | 4 |
