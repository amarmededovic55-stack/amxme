#!/bin/bash
# Signed: ASDHEM | AMXME v13 – redesign of the coming-soon page (template + CSS + UI strings, no DB changes)
set -euo pipefail
SRC=/home/administrator/amxme-github/app
DST=/opt/amxme/app
TS=$(date +%Y%m%d-%H%M%S)
tar -czf /opt/amxme/backups/app-before-v13-$TS.tgz -C /opt/amxme app
chown amxme: /opt/amxme/backups/app-before-v13-$TS.tgz
for f in i18n.py templates/maintenance.html static/css/site.css; do
  install -o amxme -g amxme -m "$(stat -c %a $DST/$f)" $SRC/$f $DST/$f
done
gzip -k -9 -c $DST/static/css/site.css > $DST/static/css/site.css.gz
chown amxme: $DST/static/css/site.css.gz
systemctl restart amxme
sleep 2
systemctl is-active amxme
curl -s -o /dev/null -w "amxme.info -> %{http_code}\n" https://amxme.info/
echo "Rollback: sudo tar -xzf /opt/amxme/backups/app-before-v13-$TS.tgz -C /opt/amxme && sudo systemctl restart amxme"
