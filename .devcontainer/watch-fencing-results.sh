#!/bin/bash
# watch-fencing-results.sh
#
# Watches _fencing-results/ for any file changes and re-runs the CSV→post
# converter so Jekyll picks up the new/updated posts and triggers livereload.
#
# This script is started as a background process by the devcontainer
# postStartCommand. It is dev-only and not part of the production build.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[watch-fencing-results] Watching _fencing-results/ for changes..."

while inotifywait -r -q -e modify,create,delete,move \
        "$SCRIPT_DIR/_fencing-results/" 2>/dev/null; do
    echo "[watch-fencing-results] Change detected — regenerating results..."
    python3 "$SCRIPT_DIR/_scripts/convert_fencing_results.py"
done
