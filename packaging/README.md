# Command Center — packaging

## Local install (`~/.local`)

No root required. Layout mirrors the `.deb` (`bin` + `share/command-center`).

```bash
./packaging/install.sh
```

### Uninstall (`~/.local`)

```bash
./packaging/uninstall.sh           # app only — keeps scripts + favorites
./packaging/uninstall.sh --purge   # also delete scripts + ~/.config/command-center
./packaging/uninstall.sh --deb     # also: sudo apt-get remove --purge command-center
./packaging/uninstall.sh --all     # --purge + --deb
```

| Path | Purpose |
|------|---------|
| `~/.local/bin/command-center` | Launcher |
| `~/.local/share/command-center/framework/` | App code + CSS |
| `~/.local/share/applications/command-center.desktop` | App menu / shortcuts |
| `~/.local/share/icons/hicolor/…/apps/command-center.*` | App icon |
| `~/.local/share/command-center/scripts/` | Your commands |

On first install it seeds **Hello Terminal** and **Confirm Demo** if those files are missing. It never overwrites existing scripts. The running app also seeds those demos on startup if missing.

## Build `.deb`

```bash
./packaging/build-deb.sh
# → dist/command-center_<version>_all.deb
```

Requires `dpkg-deb` (usually from the `dpkg` package).

## Install `.deb`

```bash
sudo apt install ./dist/command-center_*.deb
```

This installs:

| Path | Purpose |
|------|---------|
| `/usr/bin/command-center` | Launcher |
| `/usr/share/command-center/framework/` | App code + CSS |
| `/usr/share/command-center/samples/` | Demo templates (seeded into XDG on first run) |
| `/usr/share/applications/command-center.desktop` | App menu / shortcuts |
| `/usr/share/icons/hicolor/…/apps/command-center.*` | App icon (launcher grid) |

User scripts still live under:

```text
~/.local/share/command-center/scripts/
```

### Switching from `~/.local` install

If you previously ran `./packaging/install.sh`, remove the user launcher so `/usr/bin/command-center` wins (many shells put `~/.local/bin` before `/usr/bin`):

```bash
rm -f ~/.local/bin/command-center
```

Your scripts under `~/.local/share/command-center/scripts/` are kept. The old framework copy under `~/.local/share/command-center/framework/` is unused after switching.

## Personal scripts

Copy your own `.sh` commands into:

```text
~/.local/share/command-center/scripts/
```

Do not keep relying on `~/CommandCenter/scripts` for the running app — that path is no longer used at runtime.

## Desktop shortcut

Recommended: **Ctrl+Space** as a GNOME Custom Shortcut running:

```text
/usr/bin/command-center
```

(or `~/.local/bin/command-center` if you only use `install.sh`)

Or use the in-app keyboard button (Copy command / Open Keyboard Settings).

## PATH

For the local install, if `command-center` is not found:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

The `.deb` puts the binary on the normal system PATH.

## Re-install

- `install.sh` — refreshes `~/.local` framework files; user scripts and present samples are left alone.
- `.deb` — `sudo apt install --reinstall ./dist/command-center_*.deb` (or rebuild then install).
