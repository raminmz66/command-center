#!/usr/bin/env bash
# Uninstall Command Center user install (~/.local) and optionally purge data / remove .deb.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: packaging/uninstall.sh [options]

Remove the ~/.local install created by packaging/install.sh.

Options:
  --purge     Also delete user scripts and config
                (~/.local/share/command-center/scripts,
                 ~/.config/command-center)
  --deb       Also remove the system package (runs: sudo apt-get remove --purge command-center)
  --all       Same as --purge --deb
  -h, --help  Show this help

Default (no flags): removes launcher, framework, desktop entry, and app icons only.
User scripts and favorites are kept.
EOF
}

PURGE=0
DO_DEB=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge) PURGE=1 ;;
    --deb) DO_DEB=1 ;;
    --all) PURGE=1; DO_DEB=1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
BIN_DIR="${HOME}/.local/bin"
APP_DATA="${DATA_HOME}/command-center"
FRAMEWORK_DST="${APP_DATA}/framework"
SCRIPTS_DST="${APP_DATA}/scripts"
DESKTOP_DST="${DATA_HOME}/applications/command-center.desktop"
WRAPPER="${BIN_DIR}/command-center"
ICONS_DST="${DATA_HOME}/icons/hicolor"
CONFIG_DST="${CONFIG_HOME}/command-center"

removed=0

rm_path() {
  local path="$1"
  if [[ -e "${path}" || -L "${path}" ]]; then
    rm -rf "${path}"
    echo "Removed ${path}"
    removed=1
  fi
}

echo "Uninstalling Command Center (user install)…"
echo

# Launcher + desktop
rm_path "${WRAPPER}"
rm_path "${DESKTOP_DST}"

# App code only — never the whole APP_DATA unless --purge
rm_path "${FRAMEWORK_DST}"

# App icons we installed (do not wipe the whole hicolor tree)
ICON_FILES=(
  "${ICONS_DST}/scalable/apps/command-center.svg"
  "${ICONS_DST}/48x48/apps/command-center.png"
  "${ICONS_DST}/64x64/apps/command-center.png"
  "${ICONS_DST}/128x128/apps/command-center.png"
  "${ICONS_DST}/256x256/apps/command-center.png"
)
for f in "${ICON_FILES[@]}"; do
  rm_path "${f}"
done

# Drop empty icon size dirs we may have created (best-effort, ignore failures)
for d in \
  "${ICONS_DST}/scalable/apps" \
  "${ICONS_DST}/48x48/apps" \
  "${ICONS_DST}/64x64/apps" \
  "${ICONS_DST}/128x128/apps" \
  "${ICONS_DST}/256x256/apps" \
  "${ICONS_DST}/scalable" \
  "${ICONS_DST}/48x48" \
  "${ICONS_DST}/64x64" \
  "${ICONS_DST}/128x128" \
  "${ICONS_DST}/256x256"
do
  if [[ -d "${d}" ]] && [[ -z "$(ls -A "${d}" 2>/dev/null || true)" ]]; then
    rmdir "${d}" 2>/dev/null || true
  fi
done

if [[ "${PURGE}" -eq 1 ]]; then
  echo
  echo "Purging user data (--purge)…"
  rm_path "${SCRIPTS_DST}"
  rm_path "${CONFIG_DST}"
  # Remove empty app data root if nothing left
  if [[ -d "${APP_DATA}" ]] && [[ -z "$(ls -A "${APP_DATA}" 2>/dev/null || true)" ]]; then
    rm_path "${APP_DATA}"
  fi
else
  if [[ -d "${SCRIPTS_DST}" ]] || [[ -d "${CONFIG_DST}" ]]; then
    echo
    echo "Kept user data (use --purge to delete):"
    [[ -d "${SCRIPTS_DST}" ]] && echo "  Scripts: ${SCRIPTS_DST}"
    [[ -d "${CONFIG_DST}" ]] && echo "  Config:  ${CONFIG_DST}"
  fi
fi

# Refresh caches after removals
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DATA_HOME}/applications" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1 && [[ -d "${ICONS_DST}" ]]; then
  gtk-update-icon-cache -f -t "${ICONS_DST}" >/dev/null 2>&1 || true
fi

echo

if [[ "${DO_DEB}" -eq 1 ]]; then
  if dpkg -l command-center 2>/dev/null | grep -q '^ii'; then
    echo "Removing system package command-center…"
    if sudo apt-get remove --purge -y command-center; then
      echo "Removed .deb package command-center"
      removed=1
    else
      echo "error: failed to remove .deb (try: sudo apt-get remove --purge command-center)" >&2
      exit 1
    fi
  else
    echo "No installed .deb package named command-center (skipped)."
  fi
  echo
elif dpkg -l command-center 2>/dev/null | grep -q '^ii'; then
  echo "Note: system package command-center is still installed."
  echo "  Remove with:  ./packaging/uninstall.sh --deb"
  echo "  Or:           sudo apt-get remove --purge command-center"
  echo
fi

if [[ "${removed}" -eq 0 ]]; then
  echo "Nothing to remove for the user install."
else
  echo "Done."
fi

echo
echo "If you set a GNOME Custom Shortcut to command-center, clear or update it in"
echo "Settings → Keyboard → Custom Shortcuts."
