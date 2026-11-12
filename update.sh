#!/usr/bin/env bash
# Signed: ASDHEM | AMXME Web Solutions
# Update an existing install with the latest code. From inside the repo:
#   git pull && sudo bash update.sh
# Keeps .env, the database, uploads and backups untouched.
set -euo pipefail

APP=/opt/amxme
SRC="$(cd "$(dirname "$0")" && pwd)"

if [[ $EUID -ne 0 ]]; then echo "Run with sudo: sudo bash update.sh"; exit 1; fi
if [[ ! -f "$APP/.env" ]]; then echo "Not installed yet. Use: sudo bash install.sh <domain> <email>"; exit 1; fi

STAMP=$(date +%F-%H%M)
echo "==> Backup -> $APP/backups/*-$STAMP"
tar -C "$APP" -czf "$APP/backups/app-$STAMP.tgz" app
if [[ -f "$APP/data/amxme.db" ]]; then
  sudo -u amxme "$APP/.venv/bin/python" -c "
import sqlite3; s = sqlite3.connect('$APP/data/amxme.db'); d = sqlite3.connect('$APP/backups/amxme-$STAMP.db'); s.backup(d); d.close()"
fi

echo "==> Copying code"
rsync -a --delete --exclude .git --exclude .env --exclude .venv --exclude data --exclude backups \
  --exclude install.sh --exclude update.sh --exclude README.md --exclude .cache --exclude .gunicorn \
  "$SRC/" "$APP/"

echo "==> Python packages"
"$APP/.venv/bin/pip" install -q -r "$APP/requirements.txt"

echo "==> Database (new tables/columns)"
chown -R amxme:amxme "$APP"
cd "$APP"
sudo -u amxme .venv/bin/python - <<'PY'
# add columns that create_all() cannot add to existing tables
import sqlite3
import os
if not os.path.exists("/opt/amxme/data/amxme.db"):
    raise SystemExit(0)
c = sqlite3.connect("/opt/amxme/data/amxme.db")
cols = {r[1] for r in c.execute("PRAGMA table_info(admin_user)")}
if "session_gen" not in cols:
    c.execute("ALTER TABLE admin_user ADD COLUMN session_gen INTEGER NOT NULL DEFAULT 0")
    c.commit()
PY
sudo -u amxme .venv/bin/flask --app wsgi init-db

echo "==> Permissions"
chmod -R o-rwx "$APP/.venv" "$APP/deploy" "$APP/requirements.txt" "$APP/wsgi.py"
find "$APP/app" -name '*.py' -exec chmod o-r {} +
find "$APP/app/templates" -type f -exec chmod o-r {} +
chmod -R o+rX "$APP/app/static"

systemctl restart amxme
sleep 2
systemctl is-active --quiet amxme && echo "==> Updated and running." || { echo "!! Service failed - see: journalctl -u amxme -n 50"; exit 1; }
