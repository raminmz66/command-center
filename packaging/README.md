# Command Center — local install

User install under `~/.local` (layout mirrors a future `/usr` package).

## Install

```bash
./packaging/install.sh
```

This installs:

| Path | Purpose |
|------|---------|
| `~/.local/bin/command-center` | Launcher |
| `~/.local/share/command-center/framework/` | App code + CSS |
| `~/.local/share/applications/command-center.desktop` | App menu / shortcuts |
| `~/.local/share/command-center/scripts/` | Your commands |

On first install it seeds **Hello Terminal** and **Confirm Demo** if those files are missing. It never overwrites existing scripts.

## Personal scripts

Copy your own `.sh` commands into:

```text
~/.local/share/command-center/scripts/
```

Do not keep relying on `~/CommandCenter/scripts` for the running app — that path is no longer used at runtime.

## Desktop shortcut

Recommended: **Ctrl+Space** as a GNOME Custom Shortcut running:

```text
~/.local/bin/command-center
```

Or use the in-app keyboard button (Copy command / Open Keyboard Settings).

## PATH

If `command-center` is not found:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Re-install

Re-running `install.sh` refreshes framework files. User scripts and already-present samples are left alone.

## Future

A `.deb` / Flatpak can reuse the same `bin` + `share/command-center` layout with system prefixes.
