#!/usr/bin/env bash
set -euo pipefail
echo "Creating demo workspace files..."
mkdir -p "${WORKSPACE_DIR:-workspace}"
echo "# Demo" > "${WORKSPACE_DIR:-workspace}/README.md"
echo "Done."
