# Packaging prep — relocatable ~/.local install (Step 32 lite)

**Date:** 2026-07-29  
**Phase:** 4 — Framework Release  
**Cycle:** Packaging (Step 32 lite) — prepare for future `.deb` via relocatable layout  
**Status:** Approved for planning  
**Parent:** PROJECT_ROADMAP Step 32; follows desktop summon

## Goal

Install Command Center under `~/.local` with XDG script/data paths so a future distro package (`.deb` / Flatpak) can reuse the same layout. Remove runtime hardcoding of `~/CommandCenter`.

## Decisions

| Topic | Choice |
|-------|--------|
| Target | **Prepare for C via B** — relocatable user install now; no `.deb` this cycle |
| Prefix | **`~/.local`** (`bin` + `share/command-center`) |
| Scripts dir | Always **`~/.local/share/command-center/scripts`** (XDG_DATA_HOME-aware) |
| Personal script migrate | **None** — user copies manually |
| Samples | **Hello Terminal** + **Confirm Demo**; create only if file missing |
| Open Scripts sample | **Rejected** — redundant with header folder button |
| Dev run | `python3 framework/menu.py` still works; scripts still from XDG scripts dir |

## Install layout

```
~/.local/bin/command-center
~/.local/share/command-center/framework/   # app code + style.css
~/.local/share/applications/command-center.desktop
~/.local/share/command-center/scripts/     # user commands + seeded samples
~/.config/command-center/                  # favorites (unchanged)
```

## In scope

- `framework/paths.py` — scripts dir, framework dir, CSS path, XDG helpers
- Replace hardcoded `~/CommandCenter/...` in runtime code
- `packaging/install.sh` — copy framework, wrapper, desktop entry, ensure scripts dir, seed samples
- `packaging/samples/hello-terminal.sh`, `packaging/samples/confirm-demo.sh`
- Update desktop install helper / Exec to use `command-center` when on PATH
- Folder button opens XDG scripts dir
- Short install notes (README section or `packaging/README.md`)
- PATH warning if `~/.local/bin` missing from PATH

## Out of scope

- Building `.deb` / Flatpak / AppImage
- Auto-migrate `~/CommandCenter/scripts`
- `/opt` install
- Uninstall automation (document manual removal)
- Tray, notifications, project generator

## Architecture

```
packaging/install.sh
        │
        ├─► ~/.local/share/command-center/framework/  (copy)
        ├─► ~/.local/bin/command-center               (wrapper)
        ├─► ~/.local/share/applications/*.desktop
        └─► scripts/ + samples if missing

paths.py
        ├─ scripts_dir()  → $XDG_DATA_HOME/command-center/scripts
        ├─ data_dir()     → $XDG_DATA_HOME/command-center
        └─ framework_dir() / css_path() → dirname of running modules
```

### Path rules

1. **Scripts** always XDG data (`…/command-center/scripts`), never `~/CommandCenter/scripts`.
2. **Framework/CSS** = directory containing the running `menu.py` / package (works for both git checkout and installed tree).
3. Favorites remain under `~/.config/command-center/`.

### Samples

| File | NAME | Notes |
|------|------|--------|
| `hello-terminal.sh` | Hello Terminal | `TERMINAL=true`; harmless echo |
| `confirm-demo.sh` | Confirm Demo | `CONFIRM=true`; DESC explains safe demo; `notify-send` or echo |

Seed only when the destination file does not exist.

### Installer steps

1. Create directories  
2. `rsync`/`cp` framework into share tree  
3. Write wrapper invoking installed entrypoint  
4. Install desktop file (`Exec=env … command-center` or absolute wrapper path)  
5. `mkdir -p` scripts; copy missing samples  
6. `update-desktop-database` if available  
7. Print success + “copy personal scripts here” + PATH hint  

## Success criteria

- After install: `command-center` launches; desktop entry works  
- Empty/new scripts dir shows Hello Terminal + Confirm Demo  
- No runtime dependency on `~/CommandCenter` for scripts or CSS  
- Layout mirrors future `/usr/bin` + `/usr/share/command-center`  

## Risks

- User still has scripts only in the git repo until they copy — document clearly  
- `~/.local/bin` not on PATH on some systems — warn at install  
- Re-install must refresh framework without clobbering user scripts  
