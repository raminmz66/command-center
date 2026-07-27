# Favorites Apply Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Larger edit-mode stars; defer Favorites strip/persist updates until header **Apply** (then exit edit mode).

**Architecture:** Keep saved `self.favorites` for strip membership; while editing, mutate `self.pending_favorites` only and drive star glyphs from pending. Apply writes pending via `save_favorites`, reloads, exits edit. CSS bump for star size. Include already-needed visibility/`no_show_all` behavior.

**Tech Stack:** Python 3, GTK 3, existing `favorites.py`

## Global Constraints

- Apply replaces Done: saves pending, refreshes strip, exits edit mode
- While editing: no live strip membership changes; no disk writes until Apply
- Stars display-only; whole card click toggles pending
- Favorites strip still ignores category/search; dual-render of saved favorites in main grid unchanged
- Preserve search focus fix; Favorites empty hide via `no_show_all` True/False toggle
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/style.css` | Larger `.cc-favorite-star` |
| `framework/menu.py` | Pending list, Apply flow, strip from saved favorites |
| `STATUS.md` | Mark 23b done / return to Step 24 |

---

### Task 1: Bigger stars (CSS)

**Files:**
- Modify: `framework/style.css`

- [x] **Step 1: Update star CSS**

Replace `.cc-favorite-star` rules with:

```css
.cc-favorite-star {
  font-size: 22px;
  line-height: 1;
  color: alpha(@theme_fg_color, 0.35);
  margin: 0 6px 0 0;
}

.cc-favorite-star.favorited {
  color: #f6c32a;
  font-size: 22px;
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
fix: enlarge favorite stars in edit mode.

EOF
)"
```

---

### Task 2: Pending favorites + Apply (menu.py)

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- `self.pending_favorites: list[str] | None` — `None` when not editing; copy of favorites when entering edit
- Enter edit: set pending from `self.favorites`; label button **Apply**
- Card click in edit: toggle basename in `pending_favorites` only; `render_commands()` (stars from pending; strip from `self.favorites`)
- Apply click when editing: `save_favorites` pruned pending → reload favorites → exit edit → render
- Star glyph: `favorited = basename in (self.pending_favorites if self.edit_favorites else self.favorites)`
- Strip membership: always from `self.favorites` (saved), never from pending

- [x] **Step 1: Init pending + fix Apply label in `_sync_edit_fav_button`**

After `self.edit_favorites = False`:

```python
        self.pending_favorites = None
```

In `_sync_edit_fav_button` when editing, use label **Apply** (not Done):

```python
        if self.edit_favorites:
            self.edit_fav_button.set_label("Apply")
            self.edit_fav_button.set_image(Gtk.Image())
            self.edit_fav_button.set_always_show_image(False)
            self.edit_fav_button.set_tooltip_text("Apply favorite changes")
            self.edit_fav_button.get_style_context().add_class("active")
```

Keep the non-edit branch (star icon) as today.

- [x] **Step 2: Enter / Apply handler**

Replace `on_edit_favorites_clicked` with:

```python
    def on_edit_favorites_clicked(self, *_args):
        if not self.edit_favorites:
            self.edit_favorites = True
            self.pending_favorites = list(self.favorites)
            self._sync_edit_fav_button()
            self.render_commands()
            return
        # Apply pending → disk, exit edit
        known = self._known_basenames()
        names = [n for n in (self.pending_favorites or []) if n in known]
        save_favorites(names)
        self.favorites = load_favorites()
        self.pending_favorites = None
        self.edit_favorites = False
        self._sync_edit_fav_button()
        self.render_commands()
```

Update imports: need `save_favorites` from `favorites` (keep `load_favorites`, `toggle_favorite` only if still used — remove `toggle_favorite` if unused after this change).

- [x] **Step 3: Card click toggles pending only**

```python
    def on_favorite_card_clicked(self, _button, path):
        basename = os.path.basename(path)
        pending = list(self.pending_favorites or [])
        if basename in pending:
            pending = [n for n in pending if n != basename]
        else:
            pending.append(basename)
        self.pending_favorites = pending
        self.render_commands()
```

- [x] **Step 4: `_attach_cards` uses pending for star state**

```python
            if self.edit_favorites and self.pending_favorites is not None:
                favorited = basename in self.pending_favorites
            else:
                favorited = basename in self.favorites
```

Favorites strip construction in `render_commands` must continue to iterate `self.favorites` (saved), not pending.

Ensure visibility logic remains:

```python
        if not fav_items:
            self.favorites_box.set_no_show_all(True)
            self.favorites_box.hide()
        else:
            self.favorites_box.set_no_show_all(False)
            self._attach_cards(self.favorites_grid, fav_items)
            self.favorites_box.show_all()
```

And module bottom still has:

```python
window.show_all()
window.render_commands()
Gtk.main()
```

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
feat: defer favorite strip updates until Apply.

EOF
)"
```

---

### Task 3: STATUS + plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: `docs/superpowers/plans/2026-07-27-favorites-apply.md` (this file)

- [x] **Step 1: Update STATUS**

- Note Step 23b favorites polish done (or in progress→done after execute)
- Return Next action to Step 24 Confirmation `ready to brainstorm`
- Mention manual QA: bigger stars; edit toggles don’t move strip until Apply

- [x] **Step 2: Mark all `- [ ]` in this plan as `- [x]`**

- [x] **Step 3: Commit**

```bash
cd /home/ramin/CommandCenter
git add STATUS.md docs/superpowers/plans/2026-07-27-favorites-apply.md
git commit -m "$(cat <<'EOF'
docs: mark favorites Apply polish complete in STATUS.

EOF
)"
```

---

## Manual verification (human)

```bash
cd ~/CommandCenter/framework && python3 menu.py
```

1. Edit → stars larger; click cards → stars flip; Favorites strip membership unchanged  
2. Apply → strip updates; edit exits; JSON matches  
3. Empty favorites → no Favorites label on load  
4. Search/chips still work
