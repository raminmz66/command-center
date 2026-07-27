# Confirmation System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Inline Soft GNOME confirm banner for `# CONFIRM=true` scripts — `Run {Name}?`, Cancel/Run/Esc, hard-block other launches while open.

**Architecture:** `menu.py` owns banner widget + `pending_confirm`; normal card clicks go through `on_command_clicked`; Run calls existing `run_command`. CSS matches brainstorm mockup. Sample lockdown script tagged.

**Tech Stack:** Python 3, GTK 3

## Global Constraints

- Inline banner (not modal); copy `Run {Name}?`
- Hard block launches while pending; Escape cancels when search not focused
- Match mockup: warm fill, `#f6c32a` border, red Run
- Do not change `launcher.py` / `metadata.py` parser
- Work from `/home/ramin/CommandCenter`; commit after logical units; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/menu.py` | Banner, pending state, click/Escape wiring |
| `framework/style.css` | Banner / button styles |
| `scripts/update-lockdown-status.sh` | `# CONFIRM=true` |
| `STATUS.md` | Step 24 done → Step 25 |

---

### Task 1: Banner UI + click wiring in `menu.py`

**Files:** Modify `framework/menu.py`

- [x] **Step 1: State + banner widgets**

After favorites box setup (or after chips), add:

```python
        self.pending_confirm = None  # (path, meta) or None

        self.confirm_banner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.confirm_banner.get_style_context().add_class("cc-confirm-banner")
        self.confirm_banner.set_no_show_all(True)
        self.confirm_banner.hide()

        self.confirm_label = Gtk.Label(xalign=0)
        self.confirm_label.get_style_context().add_class("cc-confirm-label")
        self.confirm_label.set_line_wrap(True)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_halign(Gtk.Align.START)
        self.confirm_cancel = Gtk.Button(label="Cancel")
        self.confirm_cancel.get_style_context().add_class("cc-confirm-cancel")
        self.confirm_cancel.connect("clicked", self.on_confirm_cancel)
        self.confirm_run = Gtk.Button(label="Run")
        self.confirm_run.get_style_context().add_class("cc-confirm-run")
        self.confirm_run.connect("clicked", self.on_confirm_run)
        btn_row.pack_start(self.confirm_cancel, False, False, 0)
        btn_row.pack_start(self.confirm_run, False, False, 0)

        self.confirm_banner.pack_start(self.confirm_label, False, False, 0)
        self.confirm_banner.pack_start(btn_row, False, False, 0)

        # Pack order: chips → confirm → favorites → grid
        self.content.pack_start(self.chip_box, False, False, 0)
        self.content.pack_start(self.confirm_banner, False, False, 0)
        self.content.pack_start(self.favorites_box, False, False, 0)
        self.content.pack_start(self.grid, True, True, 0)
```

(Adjust `__init__` so content packing includes confirm between chips and favorites.)

- [x] **Step 2: Show / hide / handlers**

```python
    def show_confirm(self, path, meta):
        self.pending_confirm = (path, meta)
        name = meta.get("name") or "command"
        self.confirm_label.set_text(f"Run {name}?")
        self.confirm_banner.set_no_show_all(False)
        self.confirm_banner.show_all()

    def hide_confirm(self):
        self.pending_confirm = None
        self.confirm_banner.set_no_show_all(True)
        self.confirm_banner.hide()

    def on_confirm_cancel(self, *_args):
        self.hide_confirm()

    def on_confirm_run(self, *_args):
        if not self.pending_confirm:
            return
        path, meta = self.pending_confirm
        self.hide_confirm()
        run_command(None, path, meta.get("terminal", False))

    def on_command_clicked(self, _button, path, meta):
        if self.pending_confirm is not None:
            return  # hard block
        if meta.get("confirm"):
            self.show_confirm(path, meta)
            return
        run_command(None, path, meta.get("terminal", False))
```

In `_attach_cards` normal mode:

```python
                card.connect("clicked", self.on_command_clicked, path, meta)
```

- [x] **Step 3: Escape**

In `on_window_key_press`, before other handling: if pending and search not focused and Escape → `hide_confirm(); return True`.

- [x] **Step 4: Compile + commit**

```bash
python3 -m py_compile framework/menu.py
git add framework/menu.py
git commit -m "feat: add inline confirmation banner for CONFIRM scripts."
```

---

### Task 2: CSS + sample + STATUS

**Files:** `framework/style.css`, `scripts/update-lockdown-status.sh`, `STATUS.md`, this plan

- [x] **Step 1: CSS** (mockup-matched)

```css
.cc-confirm-banner {
  margin: 8px 8px 10px;
  padding: 12px 14px;
  border-radius: 10px;
  background-color: #fff8e7;
  border: 1px solid #f6c32a;
}

.cc-confirm-label {
  font-weight: 700;
  font-size: 14px;
  color: @theme_fg_color;
  margin-bottom: 2px;
}

button.cc-confirm-cancel {
  background-image: none;
  background-color: @theme_base_color;
  border: 1px solid alpha(@borders, 0.9);
  border-radius: 6px;
  padding: 6px 12px;
  font-weight: 600;
}

button.cc-confirm-run {
  background-image: none;
  background-color: #c01c28;
  border: 1px solid #c01c28;
  border-radius: 6px;
  padding: 6px 12px;
  font-weight: 600;
  color: white;
}

button.cc-confirm-run:hover {
  background-image: none;
  background-color: #a51d2d;
  border-color: #a51d2d;
  color: white;
}
```

- [x] **Step 2:** Add `# CONFIRM=true` to lockdown script

- [x] **Step 3:** STATUS → Step 25 ready; mark plan checkboxes

- [x] **Step 4: Commit**

---

## Visual QA loop

Relaunch `menu.py`, trigger confirm (Lockdown card), screenshot, compare to mockup, fix CSS/layout, kill app, repeat ≤10.
