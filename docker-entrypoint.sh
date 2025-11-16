#!/bin/bash
set -euo pipefail

if [ -n "${DATABASE_URL:-}" ]; then
  export SQLALCHEMY_DATABASE_URI="$DATABASE_URL"
fi

if flask --app run db upgrade; then
  echo "Database migrations applied"
else
  echo "Database migration step failed; creating tables via SQLAlchemy" >&2
  python - <<'PY'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
PY
fi

exec "$@"
