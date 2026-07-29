#!/usr/bin/env bash
# Install Command Center .desktop for GNOME Custom Shortcuts / app menus.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK="${ROOT}/framework"
TEMPLATE="${ROOT}/packaging/command-center.desktop"
DEST_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DEST="${DEST_DIR}/command-center.desktop"

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "error: missing ${TEMPLATE}" >&2
  exit 1
fi
if [[ ! -f "${FRAMEWORK}/menu.py" ]]; then
  echo "error: missing ${FRAMEWORK}/menu.py" >&2
  exit 1
fi

mkdir -p "${DEST_DIR}"
# Absolute Exec so Custom Shortcuts work from any cwd.
EXEC_LINE="python3 ${FRAMEWORK}/menu.py"
sed "s|^Exec=.*|Exec=${EXEC_LINE}|" "${TEMPLATE}" > "${DEST}"
chmod 644 "${DEST}"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DEST_DIR}" >/dev/null 2>&1 || true
fi

echo "Installed ${DEST}"
echo "Exec: ${EXEC_LINE}"
echo "Add a GNOME Custom Shortcut (recommended Ctrl+Space) that runs that Exec,"
echo "or pick “Command Center” from the app list after the desktop database refreshes."
