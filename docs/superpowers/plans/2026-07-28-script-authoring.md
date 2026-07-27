# Script Authoring UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** In-app create / edit / delete for Command Center scripts (metadata + body), matching Soft GNOME visual reference.

**Architecture:** `scriptio.py` owns file read/write; `authoring.py` owns the full-window form; `menu.py` uses a `Gtk.Stack` (launcher ↔ authoring), Edit-commands mode with card ✎/🗑, and delete confirm; CSS mirrors the visual HTML.

**Tech Stack:** Python 3, GTK 3, `unittest`

## Global Constraints

- Visual contract: `docs/superpowers/visuals/2026-07-28-script-authoring.html` (screens 1–4)
- Tokens: accent `#f6c32a`, cream `#fff8e7`, danger `#c01c28`
- Scripts remain source of truth under `~/CommandCenter/scripts` with `# NAME=` etc. compatible with `metadata.read_metadata`
- Filename: slug on create; no rename on edit; collisions → `-2`, `-3`, …
- Edit commands ⊕ Edit favorites mutually exclusive (entering one discards pending favorites / exits the other)
- Preserve search focus fix, Soft GNOME cards, categories, favorites Apply, confirm popover
- Do not change `launcher.py` behavior
- Work from `/home/ramin/CommandCenter`; commit after each task; do not push unless asked

## File structure

| File | Responsibility |
|------|----------------|
| `framework/scriptio.py` | read/write/delete script files; slug; unique_path |
| `framework/test_scriptio.py` | Unit tests |
| `framework/authoring.py` | Full-window form widget |
| `framework/widgets.py` | Card overlay edit/delete when commands-edit |
| `framework/menu.py` | Stack, modes, wire create/edit/delete |
| `framework/style.css` | Authoring / edit-mode / delete dialog styles |
| `STATUS.md` | Stage updates |

---

### Task 1: `scriptio.py` + unit tests

**Files:**
- Create: `framework/scriptio.py`
- Create: `framework/test_scriptio.py`

**Interfaces:**
- Produces:
  - `slug_filename(name: str) -> str`
  - `unique_path(directory: str, filename: str) -> str`
  - `read_script(path: str) -> {"meta": dict, "body": str}`
  - `write_script(path: str, meta: dict, body: str) -> None`
  - `delete_script(path: str) -> None`

- [x] **Step 1: Write failing tests** in `framework/test_scriptio.py`

```python
#!/usr/bin/env python3
import os
import stat
import tempfile
import unittest

import scriptio


class ScriptioTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def test_slug_filename(self):
        self.assertEqual(scriptio.slug_filename("My Backup"), "my-backup.sh")
        self.assertEqual(scriptio.slug_filename("  VPN  "), "vpn.sh")

    def test_unique_path_collision(self):
        open(os.path.join(self.dir, "a.sh"), "w").close()
        p = scriptio.unique_path(self.dir, "a.sh")
        self.assertTrue(p.endswith("a-2.sh"))

    def test_round_trip(self):
        path = os.path.join(self.dir, "demo.sh")
        meta = {
            "name": "Demo",
            "icon": "folder-symbolic",
            "desc": "Hello",
            "category": "System",
            "terminal": True,
            "confirm": False,
            "color": "b",
        }
        scriptio.write_script(path, meta, "echo hi\n")
        data = scriptio.read_script(path)
        self.assertEqual(data["meta"]["name"], "Demo")
        self.assertEqual(data["meta"]["terminal"], True)
        self.assertEqual(data["meta"]["color"], "b")
        self.assertEqual(data["body"].strip(), "echo hi")
        mode = os.stat(path).st_mode
        self.assertTrue(mode & stat.S_IXUSR)

    def test_delete(self):
        path = os.path.join(self.dir, "x.sh")
        scriptio.write_script(path, {"name": "X"}, "true\n")
        scriptio.delete_script(path)
        self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run tests — expect FAIL** (`ModuleNotFoundError` or missing attrs)

Run: `cd /home/ramin/CommandCenter/framework && python3 -m unittest test_scriptio -v`

- [x] **Step 3: Implement `scriptio.py`**

```python
#!/usr/bin/env python3
import os
import re

from metadata import read_metadata


def slug_filename(name):
    raw = (name or "").strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    if not raw:
        raw = "command"
    return raw + ".sh"


def unique_path(directory, filename):
    base, ext = os.path.splitext(filename)
    if not ext:
        ext = ".sh"
    candidate = os.path.join(directory, base + ext)
    n = 2
    while os.path.exists(candidate):
        candidate = os.path.join(directory, f"{base}-{n}{ext}")
        n += 1
    return candidate


def read_script(path):
    meta = read_metadata(path)
    body_lines = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("#!"):
                continue
            if s.startswith("# ") and "=" in s[2:40]:
                key = s[2:].split("=", 1)[0].strip().upper()
                if key in {
                    "NAME", "ICON", "DESC", "CATEGORY",
                    "TERMINAL", "CONFIRM", "COLOR",
                }:
                    continue
            body_lines.append(line)
    body = "".join(body_lines).lstrip("\n")
    return {"meta": meta, "body": body}


def write_script(path, meta, body):
    lines = ["#!/bin/bash\n"]
    def add(key, value):
        if value is None or value == "":
            return
        lines.append(f"# {key}={value}\n")
    add("NAME", meta.get("name"))
    add("ICON", meta.get("icon"))
    add("DESC", meta.get("desc"))
    if meta.get("color"):
        add("COLOR", meta.get("color"))
    term = meta.get("terminal", False)
    add("TERMINAL", "true" if term else "false")
    conf = meta.get("confirm", False)
    add("CONFIRM", "true" if conf else "false")
    add("CATEGORY", meta.get("category") or "General")
    lines.append("\n")
    body_text = body if body.endswith("\n") or body == "" else body + "\n"
    lines.append(body_text)
    with open(path, "w", encoding="utf-8") as fh:
        fh.writelines(lines)
    os.chmod(path, 0o755)


def delete_script(path):
    os.remove(path)
```

- [x] **Step 4: Run tests — expect PASS**

- [x] **Step 5: Commit**

```bash
git add framework/scriptio.py framework/test_scriptio.py
git commit -m "feat: add scriptio read/write helpers for authoring."
```

---

### Task 2: `authoring.py` form widget

**Files:**
- Create: `framework/authoring.py`

**Interfaces:**
- Consumes: curated icon names (local list); `normalize_icon_color` from textutil
- Produces: `AuthoringForm(Gtk.Box)` with:
  - `set_mode(create|edit)`, `load(path=None, meta=None, body="")`, `get_values() -> (meta, body)`, `is_dirty()`, `validate() -> str|None`
  - signals via callbacks: `on_save`, `on_cancel` set by menu
  - Header row: Back, title label, Save — matching visual screen 2/3
  - Cream `.cc-authoring-shell` with fields

- [x] **Step 1: Implement form UI** (Name, Desc, Category, icon grid + custom entry, color swatches, Terminal/Confirm switches, multiline Script, Cancel/Save footer). Track baseline for dirty.

- [x] **Step 2: Smoke import**

Run: `cd /home/ramin/CommandCenter/framework && python3 -c "from authoring import AuthoringForm; print('ok')"`

- [x] **Step 3: Commit**

```bash
git add framework/authoring.py
git commit -m "feat: add Soft GNOME script authoring form widget."
```

---

### Task 3: Card edit/delete actions + CSS shell

**Files:**
- Modify: `framework/widgets.py`
- Modify: `framework/style.css`

**Interfaces:**
- `CommandCard(..., commands_edit=False, on_edit=None, on_delete=None)`
- When `commands_edit`: wrap content in `Gtk.Overlay`; top-right ✎ and 🗑 buttons (classes `cc-card-edit`, `cc-card-delete`); card itself not used for launch
- CSS: match visual — cream edit btn, red-tint delete, gold Edit header `.cc-edit-commands.active`, banner `.cc-edit-banner`, authoring shell, delete dialog

- [x] **Step 1: Extend CommandCard + CSS classes from visual reference**

- [x] **Step 2: Commit**

```bash
git add framework/widgets.py framework/style.css
git commit -m "feat: card edit/delete controls and authoring CSS."
```

---

### Task 4: Wire menu — stack, Edit mode, create/edit/delete

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- `self.stack` with `launcher` and `authoring` pages
- `edit_commands` bool; header Edit + **+**
- Create → `show_authoring(None)`; Edit → `show_authoring(path)`; Delete → cream confirm → `scriptio.delete_script` + prune favorites → reload
- Save → validate → write (unique path if create) → show launcher → `load_commands`
- Dirty Back/Cancel → discard confirm
- Mutual exclusion with favorites edit

- [x] **Step 1: Implement stack + mode + dialogs in `menu.py`**

- [x] **Step 2: Manual smoke** — launch app, open Edit, open +, Esc/Back

Run: `cd /home/ramin/CommandCenter/framework && timeout 2 python3 menu.py || true`

- [x] **Step 3: Commit**

```bash
git add framework/menu.py
git commit -m "feat: wire create/edit/delete authoring into Command Center."
```

---

### Task 5: STATUS + plan checkboxes

**Files:**
- Modify: `STATUS.md`
- Modify: this plan (check boxes)

- [ ] **Step 1: Mark cycle execute→done readiness; next QA**

- [ ] **Step 2: Commit**

```bash
git add STATUS.md docs/superpowers/plans/2026-07-28-script-authoring.md
git commit -m "docs: mark script authoring implementation ready for visual QA."
```

---

### Task 6: Visual QA loop (≤10 iterations)

**Reference:** `docs/superpowers/visuals/2026-07-28-script-authoring.html`

For each iteration (max 10):

1. Run app (optionally `CC_QA_AUTHORING=edit|new|delete` helpers if added)
2. Screenshot relevant state
3. Close app
4. Compare to reference screens 1–4
5. Fix CSS/layout gaps
6. Commit fixes as needed; final commit when matched

- [x] **Step 1–N: Iterate until satisfied or 10 attempts**

- [x] **Final commit:** `fix: align authoring UI with Soft GNOME visual reference.`

---

## Execution handoff

Plan complete and saved. Implementing next (commit per task, then screenshot QA).
