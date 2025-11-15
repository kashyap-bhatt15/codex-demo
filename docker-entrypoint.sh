#!/bin/sh
set -euo pipefail

if [ -d "migrations" ]; then
  echo "Applying database migrations..."
  flask db upgrade || echo "Flask migrations not applied (missing database or migrations)."
else
  echo "No migrations directory detected; skipping 'flask db upgrade'."
fi

exec "$@"
