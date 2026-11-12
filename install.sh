#!/usr/bin/env bash
# Signed: ASDHEM | AMXME Web Solutions
# Fresh install on Ubuntu/Debian. Run from inside the cloned repo:
#   sudo bash install.sh your-domain.com you@email.com [admin-username]
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"
ADMIN="${3:-admin}"
APP=/opt/amxme
SRC="$(cd "$(dirname "$0")" && pwd)"

if [[ $EUID -ne 0 ]]; then echo "Run with sudo: sudo bash install.sh <domain> <email> [admin-username]"; exit 1; fi
if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then echo "Usage: sudo bash install.sh <domain> <email> [admin-username]"; exit 1; fi
DOMAIN="${DOMAIN#http://}"; DOMAIN="${DOMAIN#https://}"; DOMAIN="${DOMAIN#www.}"; DOMAIN="${DOMAIN%%/*}"
if [[ ! "$DOMAIN" =~ ^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then echo "Invalid domain: $DOMAIN"; exit 1; fi
if [[ -f "$APP/.env" ]]; then echo "$APP already installed. Use: sudo bash update.sh"; exit 1; fi

echo "==> Installing packages"
apt-get update -q
DEBIAN_FRONTEND=noninteractive apt-get install -y -q python3 python3-venv nginx certbot python3-certbot-nginx rsync

echo "==> Creating system user 'amxme'"
id amxme &>/dev/null || useradd --system --home-dir "$APP" --shell /usr/sbin/nologin amxme

echo "==> Copying code to $APP"
mkdir -p "$APP/data/uploads" "$APP/backups"
rsync -a --delete --exclude .git --exclude .env --exclude .venv --exclude data --exclude backups \
  --exclude install.sh --exclude update.sh --exclude README.md "$SRC/" "$APP/"

echo "==> Python environment"
python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install -q --upgrade pip
"$APP/.venv/bin/pip" install -q -r "$APP/requirements.txt"

echo "==> Configuration (.env)"
SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
sed -e "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET|" \
    -e "s|^SITE_URL=.*|SITE_URL=https://$DOMAIN|" \
    "$SRC/.env.example" > "$APP/.env"

echo "==> Permissions"
chown -R amxme:amxme "$APP"
chmod 600 "$APP/.env"
chmod 711 "$APP" "$APP/data"
chmod 700 "$APP/backups"
chmod -R o-rwx "$APP/.venv" "$APP/deploy" "$APP/requirements.txt" "$APP/wsgi.py"
find "$APP/app" -name '*.py' -exec chmod o-r {} +
chmod 751 "$APP/app"
find "$APP/app/templates" -type f -exec chmod o-r {} +
chmod -R o+rX "$APP/app/static"
chmod 755 "$APP/data/uploads"

echo "==> Database + admin user"
cd "$APP"
sudo -u amxme .venv/bin/flask --app wsgi init-db
ADMIN_OUT=$(sudo -u amxme .venv/bin/flask --app wsgi create-admin "$ADMIN")

echo "==> systemd service"
cp "$APP/deploy/amxme.service" /etc/systemd/system/amxme.service
systemctl daemon-reload
systemctl enable --now amxme

echo "==> nginx"
sed "s/__DOMAIN__/$DOMAIN/g" "$APP/deploy/nginx-amxme.conf" > /etc/nginx/sites-available/amxme
ln -sf /etc/nginx/sites-available/amxme /etc/nginx/sites-enabled/amxme
rm -f /etc/nginx/sites-enabled/default
if ! grep -rqs "^\s*gzip_types" /etc/nginx/nginx.conf /etc/nginx/conf.d/; then
  cp "$APP/deploy/gzip.conf" /etc/nginx/conf.d/gzip.conf
fi
nginx -t
systemctl reload nginx

if command -v ufw &>/dev/null && ufw status | grep -q "Status: active"; then
  ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null
fi

echo "==> HTTPS certificate (DNS of $DOMAIN and www.$DOMAIN must point to this server)"
if certbot --nginx -n --agree-tos --redirect -m "$EMAIL" -d "$DOMAIN" -d "www.$DOMAIN"; then
  HTTPS_OK=1
else
  HTTPS_OK=0
fi

echo
echo "================================================================"
echo " AMXME installed."
echo " Website: https://$DOMAIN      Admin: https://$DOMAIN/admin"
echo " $ADMIN_OUT"
echo " Change this password after the first sign-in (Admin -> Account)."
if [[ $HTTPS_OK != 1 ]]; then
  echo
  echo " !! HTTPS failed (DNS probably not pointing here yet). When it does, run:"
  echo "    sudo certbot --nginx --redirect -d $DOMAIN -d www.$DOMAIN"
  echo "    Until then the admin login will not work (secure cookies need HTTPS)."
fi
echo "================================================================"
