# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Uptime monitoring for our own and our clients' websites.
Run every 5 minutes by a systemd timer: `flask --app wsgi check-monitors`."""
import socket
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import current_app

from .extensions import db
from .mailer import send_mail
from .models import Monitor, MonitorCheck, utcnow

UA = "AMXME-Monitor/1.0 (+https://amxme.info/status)"
KEEP_DAYS = 90


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def _probe(url, timeout=10):
    """(ok, http_code, ms, error)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    opener = urllib.request.build_opener(_NoRedirect)
    t0 = time.monotonic()
    try:
        with opener.open(req, timeout=timeout) as r:
            r.read(2048)
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except (urllib.error.URLError, socket.timeout, ConnectionError, ssl.SSLError, OSError) as e:
        return False, 0, int((time.monotonic() - t0) * 1000), str(getattr(e, "reason", e))[:200]
    ms = int((time.monotonic() - t0) * 1000)
    return 200 <= code < 400, code, ms, "" if code < 400 else f"HTTP {code}"


def ssl_expiry(url):
    u = urlparse(url)
    if u.scheme != "https" or not u.hostname:
        return None
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((u.hostname, u.port or 443), timeout=6) as s, \
                ctx.wrap_socket(s, server_hostname=u.hostname) as tls:
            return datetime.strptime(tls.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z")
    except (OSError, ssl.SSLError, KeyError, ValueError):
        return None


def _notify(m, went_down):
    from .templating import get_content
    c = get_content("en")
    to = c.notify_email or c.contact_email
    if not to:
        return
    if went_down:
        subj = f"DOWN: {m.name} is not reachable"
        body = f"{m.name} ({m.url}) stopped responding at {utcnow():%Y-%m-%d %H:%M} UTC.\nError: {m.last_error or m.last_code}\n"
    else:
        mins = int((utcnow() - m.down_since).total_seconds() // 60) if m.down_since else 0
        subj = f"UP again: {m.name}"
        body = f"{m.name} ({m.url}) is reachable again after about {mins} minutes.\n"
    send_mail(to, subj, body + f"\n{current_app.config['SITE_URL']}/admin/monitors\n", from_name="AMXME Monitor")


def check_monitor(m):
    ok, code, ms, err = _probe(m.url)
    if not ok:                       # one quick retry before declaring a site down
        time.sleep(3)
        ok, code, ms, err = _probe(m.url)
    before = m.status
    m.last_code, m.last_ms, m.last_error, m.last_checked = code, ms, err, utcnow()
    m.status = "up" if ok else "down"
    if m.url.startswith("https://") and (not m.ssl_expires or m.last_checked.minute < 5):
        m.ssl_expires = ssl_expiry(m.url) or m.ssl_expires
    db.session.add(MonitorCheck(monitor_id=m.id, ok=ok, ms=ms))
    if before != m.status and before != "unknown":
        if m.status == "down":
            m.down_since = utcnow()
            _notify(m, True)
        else:
            _notify(m, False)
            m.down_since = None
    elif m.status == "down" and not m.down_since:
        m.down_since = utcnow()


def check_all():
    monitors = db.session.query(Monitor).filter_by(enabled=True).all()
    for m in monitors:
        check_monitor(m)
        db.session.commit()
    db.session.query(MonitorCheck).filter(MonitorCheck.created_at < utcnow() - timedelta(days=KEEP_DAYS)).delete()
    db.session.commit()
    return len(monitors)


def uptime(monitor_id, days):
    since = utcnow() - timedelta(days=days)
    q = db.session.query(MonitorCheck).filter(MonitorCheck.monitor_id == monitor_id, MonitorCheck.created_at >= since)
    total = q.count()
    if not total:
        return None
    return round(q.filter(MonitorCheck.ok.is_(True)).count() / total * 100, 2)


def daily_bars(monitor_id, days=30):
    """[(date, pct or None)] for the status page bars."""
    start = (utcnow() - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.session.query(MonitorCheck.created_at, MonitorCheck.ok).filter(
        MonitorCheck.monitor_id == monitor_id, MonitorCheck.created_at >= start).all()
    agg = {}
    for ts, ok in rows:
        a = agg.setdefault(ts.date(), [0, 0])
        a[0] += 1
        a[1] += 1 if ok else 0
    out = []
    for i in range(days):
        d = (start + timedelta(days=i)).date()
        a = agg.get(d)
        out.append((d, round(a[1] / a[0] * 100, 1) if a else None))
    return out
