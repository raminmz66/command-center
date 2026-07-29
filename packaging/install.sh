#!/usr/bin/env bash
# Install Command Center into ~/.local (prep for future .deb layout).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEWORK_SRC="${ROOT}/framework"
SAMPLES_SRC="${ROOT}/packaging/samples"
TEMPLATE="${ROOT}/packaging/command-center.desktop"

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
BIN_DIR="${HOME}/.local/bin"
APP_DATA="${DATA_HOME}/command-center"
FRAMEWORK_DST="${APP_DATA}/framework"
SCRIPTS_DST="${APP_DATA}/scripts"
DESKTOP_DIR="${DATA_HOME}/applications"
DESKTOP_DST="${DESKTOP_DIR}/command-center.desktop"
WRAPPER="${BIN_DIR}/command-center"

if [[ ! -d "${FRAMEWORK_SRC}" ]]; then
  echo "error: missing ${FRAMEWORK_SRC}" >&2
  exit 1
fi

mkdir -p "${FRAMEWORK_DST}" "${SCRIPTS_DST}" "${BIN_DIR}" "${DESKTOP_DIR}"

# Refresh app code; never touch user scripts except seeding missing samples.
rsync -a --delete \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'test_*.py' \
  "${FRAMEWORK_SRC}/" "${FRAMEWORK_DST}/"

cat > "${WRAPPER}" <<EOF
#!/usr/bin/env bash
exec python3 "${FRAMEWORK_DST}/menu.py" "\$@"
EOF
chmod 755 "${WRAPPER}"

# Desktop Exec: absolute wrapper so Custom Shortcuts work without PATH.
sed "s|^Exec=.*|Exec=${WRAPPER}|" "${TEMPLATE}" > "${DESKTOP_DST}"
chmod 644 "${DESKTOP_DST}"

if [[ -d "${SAMPLES_SRC}" ]]; then
  for sample in "${SAMPLES_SRC}"/*.sh; do
    [[ -f "${sample}" ]] || continue
    base="$(basename "${sample}")"
    dest="${SCRIPTS_DST}/${base}"
    if [[ ! -e "${dest}" ]]; then
      cp "${sample}" "${dest}"
      chmod 755 "${dest}"
      echo "Seeded sample: ${base}"
    fi
  done
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

echo
echo "Installed Command Center"
echo "  App:     ${FRAMEWORK_DST}"
echo "  Bin:     ${WRAPPER}"
echo "  Desktop: ${DESKTOP_DST}"
echo "  Scripts: ${SCRIPTS_DST}"
echo
echo "Copy any personal scripts into:"
echo "  ${SCRIPTS_DST}"
echo
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
  echo "Note: ${BIN_DIR} is not on your PATH."
  echo "Add this to your shell profile, then re-open the terminal:"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo "Or launch via the app menu / absolute path above."
  echo
fi
echo "Recommended: GNOME Custom Shortcut Ctrl+Space → ${WRAPPER}"
echo "Or: command-center   (once PATH includes ~/.local/bin)"
