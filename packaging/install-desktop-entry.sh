#!/usr/bin/env bash
# Deprecated entry point — use packaging/install.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${ROOT}/packaging/install.sh"
