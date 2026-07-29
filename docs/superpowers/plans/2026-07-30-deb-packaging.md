# Step 32 — Debian `.deb` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a shippable `command-center_*.deb` with `/usr` layout, first-launch demo seed, and docs for switching from `~/.local` install.

**Architecture:** Lightweight `packaging/build-deb.sh` stages `/usr` + `DEBIAN/control` and runs `dpkg-deb --build`. Runtime `paths.samples_dir()` + `seed_sample_scripts()` copy demos into the XDG scripts dir only when missing. `install.sh` stays for no-sudo/dev.

**Tech Stack:** bash, `dpkg-deb`, Python 3, PyGObject, unittest

**Spec:** [docs/superpowers/specs/2026-07-30-deb-packaging-design.md](../specs/2026-07-30-deb-packaging-design.md)

## Global Constraints

- Scripts always `$XDG_DATA_HOME/command-center/scripts` (default `~/.local/share/...`)
- Seed Hello Terminal + Confirm Demo only if missing — never overwrite
- Architecture `all`; Depends: `python3`, `python3-gi`, `gir1.2-gtk-3.0`
- No Flatpak/AppImage; no full `debian/` source package; no auto-delete of `~/.local` in postinst
- Exclude `__pycache__/`, `*.pyc`, `test_*.py` from packaged framework
- Commit after each task

## File map

| File | Role |
|------|------|
| `packaging/VERSION` | Single version string for the `.deb` |
| `framework/paths.py` | Add `samples_dir()`, `seed_sample_scripts()` |
| `framework/test_paths.py` | Tests for samples + seed |
| `framework/menu.py` | Call seed before discover |
| `packaging/build-deb.sh` | Stage + `dpkg-deb --build` |
| `packaging/deb/postinst` | Optional desktop DB refresh |
| `packaging/README.md` | Build / apt install / switch from install.sh |
| `dist/` | Build output (gitignored if not already) |
| `STATUS.md` | Cycle gate |

---

### Task 1: Sample seed helper + tests

**Files:**
- Modify: `framework/paths.py`
- Modify: `framework/test_paths.py`

**Interfaces:**
- Produces: `samples_dir() -> str`, `seed_sample_scripts() -> list[str]` (basenames newly copied)
- Consumes: `ensure_scripts_dir()`, `scripts_dir()`, `framework_dir()`

- [x] **Step 1: Write failing tests**

In `framework/test_paths.py`, add:

```python
def test_samples_dir_prefers_usr_share(self):
    # When /usr/share/command-center/samples exists conceptually —
    # implement via mock of os.path.isdir on preferred path.
    usr = "/usr/share/command-center/samples"
    with mock.patch("paths.os.path.isdir", side_effect=lambda p: p == usr):
        self.assertEqual(paths.samples_dir(), usr)

def test_seed_copies_missing_only(self):
    samples = os.path.join(self._tmpdir.name, "samples")
    os.makedirs(samples)
    src = os.path.join(samples, "hello-terminal.sh")
    with open(src, "w") as f:
        f.write("#!/bin/bash\n")
    os.chmod(src, 0o755)
    with mock.patch.object(paths, "samples_dir", return_value=samples):
        created = paths.seed_sample_scripts()
        self.assertEqual(created, ["hello-terminal.sh"])
        dest = os.path.join(paths.scripts_dir(), "hello-terminal.sh")
        self.assertTrue(os.path.isfile(dest))
        # second call: no overwrite / no re-create
        with open(dest, "w") as f:
            f.write("USER\n")
        created2 = paths.seed_sample_scripts()
        self.assertEqual(created2, [])
        with open(dest) as f:
            self.assertEqual(f.read(), "USER\n")
```

- [x] **Step 2: Run tests — expect FAIL**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_paths -v
```

Expected: FAIL — `samples_dir` / `seed_sample_scripts` missing.

- [x] **Step 3: Implement**

In `framework/paths.py`:

```python
def samples_dir():
    """Demo script templates for first-launch seed."""
    candidates = [
        "/usr/share/command-center/samples",
        os.path.join(os.path.dirname(framework_dir()), "packaging", "samples"),
        os.path.join(framework_dir(), "samples"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return candidates[1]


def seed_sample_scripts():
    """Copy missing sample *.sh into scripts_dir. Never overwrite. Returns new basenames."""
    ensure_scripts_dir()
    src_root = samples_dir()
    created = []
    if not os.path.isdir(src_root):
        return created
    dest_root = scripts_dir()
    for name in sorted(os.listdir(src_root)):
        if not name.endswith(".sh"):
            continue
        src = os.path.join(src_root, name)
        if not os.path.isfile(src):
            continue
        dest = os.path.join(dest_root, name)
        if os.path.exists(dest):
            continue
        import shutil
        shutil.copy2(src, dest)
        os.chmod(dest, 0o755)
        created.append(name)
    return created
```

Put `import shutil` at module top instead of inline.

- [x] **Step 4: Run tests — expect PASS**

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_paths -v
```

- [x] **Step 5: Commit**

```bash
git add framework/paths.py framework/test_paths.py
git commit -m "feat: seed demo scripts into XDG on first launch."
```

---

### Task 2: Wire seed into menu startup

**Files:**
- Modify: `framework/menu.py`

**Interfaces:**
- Consumes: `paths.seed_sample_scripts`

- [x] **Step 1:** Add `seed_sample_scripts` to the paths import.

- [x] **Step 2:** At start of `discover_commands`, call `seed_sample_scripts()` after or instead of bare `ensure_scripts_dir()` (seed already ensures dir):

```python
def discover_commands(self):
    seed_sample_scripts()
    root = scripts_dir()
    ...
```

- [x] **Step 3:** Smoke: empty temp XDG → discover should pick up samples when `packaging/samples` resolves.

```bash
cd /home/ramin/CommandCenter/framework && \
  XDG_DATA_HOME=/tmp/cc-seed-test/share python3 -c '
from paths import seed_sample_scripts, scripts_dir
import os, shutil
shutil.rmtree("/tmp/cc-seed-test", ignore_errors=True)
print(seed_sample_scripts())
print(sorted(os.listdir(scripts_dir())))
'
```

Expected: both sample basenames listed.

- [x] **Step 4: Commit**

```bash
git add framework/menu.py
git commit -m "feat: seed sample commands before discovering scripts."
```

---

### Task 3: `VERSION` + `build-deb.sh`

**Files:**
- Create: `packaging/VERSION` (contents: `0.1.0` unless repo already has a version — use `0.1.0`)
- Create: `packaging/build-deb.sh`
- Create: `packaging/deb/postinst` (optional small script)
- Modify: `.gitignore` to ignore `/dist/` if needed

**Interfaces:**
- Produces: `dist/command-center_<VERSION>_all.deb`

- [x] **Step 1:** Write `packaging/VERSION` with `0.1.0`.

- [x] **Step 2:** Write `packaging/deb/postinst`:

```bash
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
exit 0
```

- [x] **Step 3:** Write `packaging/build-deb.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT}/packaging/VERSION")"
PKG="command-center"
ARCH="all"
STAGE="${ROOT}/dist/stage"
OUT_DIR="${ROOT}/dist"
DEB="${OUT_DIR}/${PKG}_${VERSION}_${ARCH}.deb"

rm -rf "${STAGE}"
mkdir -p \
  "${STAGE}/usr/bin" \
  "${STAGE}/usr/share/command-center/framework" \
  "${STAGE}/usr/share/command-center/samples" \
  "${STAGE}/usr/share/applications" \
  "${STAGE}/DEBIAN"

rsync -a --delete \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'test_*.py' \
  "${ROOT}/framework/" "${STAGE}/usr/share/command-center/framework/"

cp -a "${ROOT}/packaging/samples/"*.sh "${STAGE}/usr/share/command-center/samples/"
chmod 755 "${STAGE}/usr/share/command-center/samples/"*.sh

cat > "${STAGE}/usr/bin/command-center" <<'EOF'
#!/usr/bin/env bash
exec python3 /usr/share/command-center/framework/menu.py "$@"
EOF
chmod 755 "${STAGE}/usr/bin/command-center"

sed 's|^Exec=.*|Exec=/usr/bin/command-center|' \
  "${ROOT}/packaging/command-center.desktop" \
  > "${STAGE}/usr/share/applications/command-center.desktop"
chmod 644 "${STAGE}/usr/share/applications/command-center.desktop"

SIZE="$(du -sk "${STAGE}/usr" | cut -f1)"
cat > "${STAGE}/DEBIAN/control" <<EOF
Package: ${PKG}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: Command Center maintainers <command-center@localhost>
Depends: python3, python3-gi, gir1.2-gtk-3.0
Installed-Size: ${SIZE}
Description: Soft GNOME personal command launcher
 Command Center launches metadata-driven shell scripts from a GTK UI.
 User scripts live under ~/.local/share/command-center/scripts.
EOF

cp "${ROOT}/packaging/deb/postinst" "${STAGE}/DEBIAN/postinst"
chmod 755 "${STAGE}/DEBIAN/postinst"

mkdir -p "${OUT_DIR}"
dpkg-deb --build "${STAGE}" "${DEB}"
echo "Built ${DEB}"
dpkg-deb -c "${DEB}" | head -40
```

- [x] **Step 4:** `chmod +x packaging/build-deb.sh packaging/deb/postinst`

- [x] **Step 5:** Ensure `dist/` is gitignored:

```bash
grep -q '^dist/$' .gitignore 2>/dev/null || echo 'dist/' >> .gitignore
```

- [x] **Step 6:** Build and verify contents

```bash
./packaging/build-deb.sh
dpkg-deb -c dist/command-center_0.1.0_all.deb | grep -E 'usr/bin/command-center|samples/hello|framework/menu.py|applications/command-center'
```

Expected: those paths present.

- [x] **Step 7: Commit**

```bash
git add packaging/VERSION packaging/build-deb.sh packaging/deb/postinst .gitignore
git commit -m "feat: add lightweight dpkg-deb build for command-center."
```

---

### Task 4: Docs + STATUS

**Files:**
- Modify: `packaging/README.md`
- Modify: `STATUS.md`

- [x] **Step 1:** Extend `packaging/README.md` with sections:

```markdown
## Build `.deb`

```bash
./packaging/build-deb.sh
# → dist/command-center_<version>_all.deb
```

## Install `.deb`

```bash
sudo apt install ./dist/command-center_*.deb
```

### Switching from `~/.local` install

If you previously ran `./packaging/install.sh`, remove the user launcher so `/usr/bin/command-center` wins:

```bash
rm -f ~/.local/bin/command-center
```

Your scripts under `~/.local/share/command-center/scripts/` are kept. The old copy of framework under `~/.local/share/command-center/framework/` is unused after switching.
```

Keep existing `install.sh` docs.

- [x] **Step 2:** Update `STATUS.md`: cycle Step 32, stage `done` when complete; next action ready to brainstorm.

- [x] **Step 3: Commit**

```bash
git add packaging/README.md STATUS.md
git commit -m "docs: document .deb build, install, and switch from ~/.local."
```

---

### Task 5: Final verification

- [x] **Step 1:** Re-run unit tests

```bash
cd /home/ramin/CommandCenter/framework && python3 -m unittest test_paths -v
```

- [x] **Step 2:** Rebuild `.deb` and confirm control Depends line

```bash
./packaging/build-deb.sh
dpkg-deb -I dist/command-center_0.1.0_all.deb | grep -E 'Depends|Version|Architecture'
```

- [x] **Step 3:** Mark plan checkboxes done in this file; commit if needed

```bash
git add docs/superpowers/plans/2026-07-30-deb-packaging.md
git commit -m "docs: mark deb packaging plan tasks complete."
```

---

## Spec coverage check

| Spec requirement | Task |
|------------------|------|
| `build-deb.sh` + `dpkg-deb` | 3 |
| `/usr` layout + samples in package | 3 |
| First-launch seed, no overwrite | 1–2 |
| Depends listed | 3 |
| README coexistence | 4 |
| Unit tests | 1, 5 |
| Keep `install.sh` | 4 (docs only; script unchanged) |
| No postinst auto-delete `~/.local` | 3 (postinst desktop DB only) |
