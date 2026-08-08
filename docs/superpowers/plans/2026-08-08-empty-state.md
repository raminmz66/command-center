# Empty-state that teaches — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** When the scripts library has zero commands, show a centered “No commands yet” CTA that opens Create command.

**Architecture:** Pure helper for empty-library check + copy. `menu.py` builds a reusable empty-state box, toggles it vs chips/grid in `render_commands` / `rebuild_category_chips`. CSS matches Soft GNOME yellow primary. QA via empty XDG + demo tombstones + `CC_QA_SHOT`.

**Tech Stack:** Python 3, PyGObject GTK3, unittest, CSS

**Spec:** [docs/superpowers/specs/2026-08-08-empty-state-design.md](../specs/2026-08-08-empty-state-design.md)

## Global Constraints

- True empty only (`len(commands) == 0`); no filter-empty UI
- Layout A: centered hero; hide category chips
- CTA → `show_authoring(None)`; copy fixed in spec
- Commit after each task; screenshot QA required
- Do not change seed/tombstone logic except using tombstones for QA setup

## File map

| File | Role |
|------|------|
| `framework/empty_state.py` | `is_library_empty(commands)`, copy constants |
| `framework/test_empty_state.py` | Unit tests |
| `framework/style.css` | `.cc-empty-state*` classes |
| `framework/menu.py` | Widget + show/hide in render; chip skip when empty |
| `STATUS.md` | Cycle gate |

---

### Task 1: `empty_state.py` + tests

**Files:**
- Create: `framework/empty_state.py`
- Create: `framework/test_empty_state.py`

**Interfaces:**
- Produces: `is_library_empty(commands) -> bool` where `commands` is a sequence
- Produces: `TITLE`, `BODY`, `CTA` string constants matching the spec

- [ ] **Step 1: Write failing tests**

```python
# framework/test_empty_state.py
import unittest
import empty_state

class EmptyStateTests(unittest.TestCase):
    def test_empty_when_no_commands(self):
        self.assertTrue(empty_state.is_library_empty([]))

    def test_not_empty_with_commands(self):
        self.assertFalse(empty_state.is_library_empty([("/x.sh", {})]))

    def test_copy_constants(self):
        self.assertEqual(empty_state.TITLE, "No commands yet")
        self.assertEqual(
            empty_state.BODY,
            "Create your first command to fill this launcher.",
        )
        self.assertEqual(empty_state.CTA, "Create command")
```

- [ ] **Step 2:** `cd framework && python3 -m unittest test_empty_state -v` — FAIL (module missing)

- [ ] **Step 3: Implement**

```python
# framework/empty_state.py
TITLE = "No commands yet"
BODY = "Create your first command to fill this launcher."
CTA = "Create command"

def is_library_empty(commands):
    return len(commands) == 0
```

- [ ] **Step 4:** Tests PASS

- [ ] **Step 5: Commit** `feat: add empty-library helper and copy constants.`

---

### Task 2: CSS + wire empty-state in menu

**Files:**
- Modify: `framework/style.css`
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `empty_state.is_library_empty`, `TITLE`, `BODY`, `CTA`
- Produces: empty-state box shown when library empty; chips hidden; CTA → `show_authoring(None)`

- [ ] **Step 1: Add CSS**

```css
.cc-empty-state {
  /* expand and center children in content area */
}
.cc-empty-state-title { font-weight: 700; font-size: 17px; }
.cc-empty-state-body { opacity: 0.75; font-size: 13px; }
button.cc-empty-state-cta {
  /* same yellow primary as button.cc-shortcut-primary */
}
```

- [ ] **Step 2: Build widget once in `__init__` (after content packed)**

Vertical box: title label, body label (wrap), CTA button with class `cc-empty-state-cta` + `cc-shortcut-primary` (or dedicated class matching yellow). Pack into `self.content` (e.g. after grid). Start hidden (`set_no_show_all(True); hide()`). Connect CTA to `on_add_command_clicked` or lambda → `show_authoring(None)`.

- [ ] **Step 3: Toggle in `render_commands`**

If `is_library_empty(self.commands)`:
- Hide chip_box, favorites_box, commands_label, grid (clear grid children)
- Show empty-state box
Else:
- Hide empty-state
- Existing favorites/grid/label logic unchanged

- [ ] **Step 4: `rebuild_category_chips`**

If library empty: clear chip_box children and hide chip_box; return early. Else existing chip rebuild + show.

- [ ] **Step 5:** `cd framework && python3 -m unittest discover` — PASS

- [ ] **Step 6: Commit** `feat: show centered empty-state CTA when no scripts.`

---

### Task 3: Screenshot QA + STATUS

**Files:**
- Modify: `STATUS.md`
- Create: `.superpowers/qa/empty-state-cta.png` (via QA run; gitignored under `.superpowers/` — still capture for local QA; STATUS links path)

- [ ] **Step 1: Capture screenshot**

```bash
QA_ROOT=/tmp/cc-qa-empty-state
rm -rf "$QA_ROOT"
mkdir -p "$QA_ROOT/share/command-center/scripts" \
         "$QA_ROOT/config/command-center"
printf '%s\n' '["confirm-demo.sh", "hello-terminal.sh"]' \
  > "$QA_ROOT/config/command-center/deleted-samples.json"
mkdir -p /home/ramin/CommandCenter/.superpowers/qa
cd /home/ramin/CommandCenter/framework
XDG_DATA_HOME="$QA_ROOT/share" XDG_CONFIG_HOME="$QA_ROOT/config" \
  CC_QA_SHOT=/home/ramin/CommandCenter/.superpowers/qa/empty-state-cta.png \
  python3 menu.py
```

Expected: window shows centered “No commands yet” + Create button; no All chip.

- [ ] **Step 2:** Read PNG; if chips visible or layout off-center, fix CSS/packing and re-shot.

- [ ] **Step 3: Update STATUS** — cycle Empty-state that teaches → `done`; next = Reorder favorites by drag; link QA path.

- [ ] **Step 4: Commit** `docs: mark empty-state cycle done after CTA screenshot QA.`

---

## Plan self-review

- Spec coverage: true empty, layout A, copy, CTA, hide chips, QA — all tasked  
- TDD: Task 1 red/green before GTK wire  
- Commit per task  
- No restore-demos / filter-empty creep
