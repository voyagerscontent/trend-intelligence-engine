#!/usr/bin/env bash
# One-shot push of the whole engine to an EMPTY (or README-only) GitHub repo.
# Usage: bash push.sh https://github.com/voyagerscontent/trend-intelligence-engine.git
set -euo pipefail
REMOTE="${1:-}"
if [ -z "$REMOTE" ]; then
  echo "Usage: bash push.sh https://github.com/<owner>/<repo>.git" >&2
  exit 1
fi
rm -rf .git
git init -b main
git add .
git commit -m "Trend Intelligence Engine: pipeline, sources, scoring, briefs, delivery, tests, CI, auditor + cross-repo interop (reusable workflow, INTEGRATION.md)"
git remote add origin "$REMOTE"
# --force so it overwrites the auto-init README commit on a fresh repo.
git push -u origin main --force
echo "Pushed to $REMOTE"
