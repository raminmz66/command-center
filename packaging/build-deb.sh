#!/usr/bin/env bash
# Build a local command-center .deb (dpkg-deb). Output: dist/command-center_<ver>_all.deb
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT}/packaging/VERSION")"
PKG="command-center"
ARCH="all"
STAGE="${ROOT}/dist/stage"
OUT_DIR="${ROOT}/dist"
DEB="${OUT_DIR}/${PKG}_${VERSION}_${ARCH}.deb"

if [[ ! -d "${ROOT}/framework" ]]; then
  echo "error: missing ${ROOT}/framework" >&2
  exit 1
fi
if ! command -v dpkg-deb >/dev/null 2>&1; then
  echo "error: dpkg-deb not found (install dpkg)" >&2
  exit 1
fi

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
