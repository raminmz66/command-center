# Confirm Popover Placement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the top confirm banner with a Soft GNOME `Gtk.Popover` anchored to the clicked card, preserving accepted cream/gold chrome.

**Architecture:** Remove banner from content stack; `show_confirm(path, meta, relative_to=card)` pops a popover with inner styled box; hard-block + Escape unchanged.

**Tech Stack:** Python 3, GTK 3

## Global Constraints

- Popover on clicked card; no top banner
- Visual contract: `#fff8e7`, `#f6c32a` border 2px, Cancel / red Run `#c01c28`
- Hard-block launches while pending; Escape cancels
- Dismiss pending if cards rebuild while open
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/menu.py` | Remove banner; popover confirm |
| `framework/style.css` | `.cc-confirm-popover` panel styles |
| `STATUS.md` | Mark 24b done → Step 25 |

---

### Task 1: Popover wiring in `menu.py`

**Files:** Modify `framework/menu.py`

- [ ] **Step 1: Remove banner widget construction and content packing** of `confirm_banner` / label / buttons from `__init__`. Keep `self.pending_confirm = None`. Add `self.confirm_popover = None`.

- [ ] **Step 2: Replace show/hide/handlers**

```python
    def _build_confirm_popover(self, relative_to):
        pop = Gtk.Popover.new(relative_to)
        pop.set_position(Gtk.PositionType.TOP)
        pop.set_modal(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.get_style_context().add_class("cc-confirm-popover")

        label = Gtk.Label(xalign=0)
        label.get_style_context().add_class("cc-confirm-label")
        label.set_line_wrap(True)
        self.confirm_label = label

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel = Gtk.Button(label="Cancel")
        cancel.get_style_context().add_class("cc-confirm-cancel")
        cancel.connect("clicked", self.on_confirm_cancel)
        run = Gtk.Button(label="Run")
        run.get_style_context().add_class("cc-confirm-run")
        run.connect("clicked", self.on_confirm_run)
        btn_row.pack_start(cancel, False, False, 0)
        btn_row.pack_start(run, False, False, 0)

        box.pack_start(label, False, False, 0)
        box.pack_start(btn_row, False, False, 0)
        box.show_all()
        pop.add(box)
        pop.connect("closed", self.on_confirm_popover_closed)
        return pop

    def show_confirm(self, path, meta, relative_to=None):
        self.hide_confirm()
        if relative_to is None:
            return
        self.pending_confirm = (path, meta)
        self.confirm_popover = self._build_confirm_popover(relative_to)
        name = meta.get("name") or "command"
        self.confirm_label.set_text(f"Run {name}?")
        self.confirm_popover.popup()

    def hide_confirm(self):
        self.pending_confirm = None
        pop = self.confirm_popover
        self.confirm_popover = None
        if pop is not None:
            pop.hide()
            pop.destroy()

    def on_confirm_popover_closed(self, *_args):
        self.pending_confirm = None
        self.confirm_popover = None

    def on_confirm_cancel(self, *_args):
        self.hide_confirm()

    def on_confirm_run(self, *_args):
        if not self.pending_confirm:
            return
        path, meta = self.pending_confirm
        self.hide_confirm()
        run_command(None, path, meta.get("terminal", False))

    def on_command_clicked(self, button, path, meta):
        if self.pending_confirm is not None:
            return
        if meta.get("confirm"):
            self.show_confirm(path, meta, relative_to=button)
            return
        run_command(None, path, meta.get("terminal", False))
```

- [ ] **Step 3:** At start of `render_commands`, if `pending_confirm`: `hide_confirm()` (avoid orphan popover).

- [ ] **Step 4:** Update `_qa_show_first_confirm` to find a confirm card widget in `self.grid` (or favorites) and call `show_confirm(..., relative_to=card)`.

- [ ] **Step 5: Commit**

```bash
git add framework/menu.py
git commit -m "feat: anchor confirm UI to clicked card via Gtk.Popover."
```

---

### Task 2: CSS + STATUS

**Files:** `framework/style.css`, `STATUS.md`, this plan

- [ ] **Step 1:** Replace `.cc-confirm-banner` with:

```css
.cc-confirm-popover {
  margin: 0;
  padding: 14px 16px;
  border-radius: 10px;
  background-color: #fff8e7;
  border: 2px solid #f6c32a;
}
```

Keep `.cc-confirm-label` and Cancel/Run button rules.

- [ ] **Step 2:** STATUS → Step 24b done; Step 25 ready to brainstorm; mark plan `[x]`

- [ ] **Step 3: Commit**

```bash
git commit -m "style: Soft GNOME confirm popover chrome; mark Step 24b done."
```

---

## Visual QA loop (≤10)

`CC_QA_CONFIRM=1 python3 menu.py` → screenshot → compare to cream/gold contract + near-card placement → tune CSS/popover → kill → repeat.
