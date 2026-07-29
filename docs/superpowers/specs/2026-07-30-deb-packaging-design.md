# Step 32 — Debian `.deb` packaging

**Date:** 2026-07-30  
**Phase:** 4 — Framework Release  
**Cycle:** Step 32 — Packaging (`.deb`)  
**Status:** Approved  
**Parent:** PROJECT_ROADMAP Step 32; builds on [2026-07-29-packaging-prep-design.md](2026-07-29-packaging-prep-design.md)

## Goal

Ship an installable Debian package for Ubuntu/Debian that installs Command Center under `/usr`, keeps user scripts in XDG, and never shows an empty launcher (seed demo commands on first run).

## Decisions

| Topic | Choice |
|-------|--------|
| Format | **`.deb` only** this cycle (no Flatpak/AppImage) |
| Build | **`packaging/build-deb.sh` + `dpkg-deb --build`** (lightweight; not full `debian/` source) |
| Scripts | Always **`~/.local/share/command-center/scripts`** (XDG_DATA_HOME-aware) |
| Demos | **First launch** seeds Hello Terminal + Confirm Demo if missing (never overwrite) |
| Coexistence | **`.deb` wins** — document removing `~/.local/bin/command-center` after switching; no auto-delete in `postinst` |
| `install.sh` | **Keep** for no-sudo / developer local install |
| Architecture | **`all`** (pure Python / architecture-independent) |

## Package layout

```
/usr/bin/command-center
/usr/share/command-center/framework/             # app + style.css (no tests / __pycache__)
/usr/share/command-center/samples/               # demo .sh templates for seeding
/usr/share/applications/command-center.desktop   # Exec=/usr/bin/command-center
```

User data (not packaged):

```
~/.local/share/command-center/scripts/
~/.config/command-center/
```

## In scope

- `packaging/VERSION` — single version source for the `.deb`
- `packaging/build-deb.sh` — stage tree, `DEBIAN/control`, `dpkg-deb --build` → `dist/`
- Optional `DEBIAN/postinst` — `update-desktop-database` if available
- Runtime sample seed helper (shared by app startup; `install.sh` may keep its own seed or call the same logic)
- Wire seed into startup before `discover_commands`
- Update `packaging/README.md` — build, `apt install ./….deb`, switch from `install.sh`
- Unit tests for seed (idempotent, no overwrite)
- Smoke: build `.deb`, list contents, run seed tests

## Out of scope

- Flatpak / AppImage
- Full Debian source package (`debian/` + `dpkg-buildpackage`) / PPA
- Auto-delete of `~/.local` install in `postinst`
- Auto-migrate `~/CommandCenter/scripts` or personal scripts
- Project generator (Step 30), templates (Step 31)
- Uninstall of user scripts or favorites

## Architecture

```
packaging/build-deb.sh
        │
        ├─► stage/usr/bin/command-center
        ├─► stage/usr/share/command-center/framework/
        ├─► stage/usr/share/command-center/samples/
        ├─► stage/usr/share/applications/*.desktop
        └─► stage/DEBIAN/control (+ optional postinst)
                │
                └─► dpkg-deb --build → dist/command-center_<ver>_all.deb

paths.py / seed helper
        ├─ scripts_dir() → XDG …/command-center/scripts
        ├─ samples_dir() → /usr/share/…/samples or repo packaging/samples
        └─ seed_sample_scripts() → copy missing *.sh only
```

### Path rules

1. **Scripts** always XDG user data — never under `/usr`.
2. **Framework/CSS** = directory of running modules (`/usr/share/command-center/framework` when packaged).
3. **Samples for seeding** = `/usr/share/command-center/samples` when present; else repo `packaging/samples` relative to source tree for git / `install.sh` users.
4. Favorites remain under `~/.config/command-center/`.

### Control metadata

- **Package:** `command-center`
- **Depends:** `python3`, `python3-gi`, `gir1.2-gtk-3.0`
- **Section:** `utils`
- **Priority:** `optional`
- **Maintainer:** project maintainer string in `control` (reasonable default; editable in build script / VERSION notes)

### First-launch seed

On startup (before discovering commands):

1. `ensure_scripts_dir()`
2. For each `*.sh` in `samples_dir()`, if destination basename does not exist in scripts dir, copy and `chmod 755`
3. Never overwrite existing user files

Same sample pair as packaging prep: Hello Terminal, Confirm Demo.

### Coexistence with `~/.local`

- Document: after installing the `.deb`, remove `~/.local/bin/command-center` so `/usr/bin/command-center` is used (PATH often prefers `~/.local/bin`).
- Old `~/.local/share/command-center/framework` becomes unused; user scripts under XDG stay.
- Do not remove anything automatically from `postinst`.

## Success criteria

1. `./packaging/build-deb.sh` produces `dist/command-center_*_all.deb`
2. Package contains `/usr/bin/command-center`, framework, samples, desktop entry with correct Exec
3. Fresh user with empty scripts dir sees Hello Terminal + Confirm Demo after first launch
4. Existing scripts are never overwritten by seed
5. README documents build, install, and switching from `install.sh`
6. Unit tests for seed pass

## Non-goals reminder

This cycle produces a **local/GitHub-Releases-style `.deb`**, not Debian archive readiness. A future cycle can add a proper `debian/` source package if a PPA is needed.
