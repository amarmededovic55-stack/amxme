# Signed: ASDHEM | AMXME Web Solutions
import re
from datetime import timedelta

from flask import Blueprint, Response, current_app, flash, jsonify, redirect, render_template, request, url_for

from .extensions import db
from .mailer import send_mail
from .models import Feature, Message, Project, Service, Visit, utcnow
from .templating import get_content
from flask import session
import random
import json
import secrets
import time
from itsdangerous import BadSignature, URLSafeSerializer

from .models import Setting

# ASDHEM | preview links while "under construction" is on.
# Only ACTIVE links are kept (one small settings row); expired ones are dropped automatically.
PREVIEW_KEY = "preview_links"
PREVIEW_MAX_ACTIVE = 30
PREVIEW_DURATIONS = [
    (15, "15 minutes"), (30, "30 minutes"), (60, "1 hour"), (120, "2 hours"), (360, "6 hours"),
    (720, "12 hours"), (1440, "1 day"), (4320, "3 days"), (10080, "7 days"),
]
PREVIEW_DEFAULT = 30


def _preview_serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="amxme-preview-link")


def preview_links():
    """Active (non-expired) preview links, newest first."""
    row = db.session.get(Setting, PREVIEW_KEY)
    try:
        links = json.loads(row.value) if row and row.value else []
    except ValueError:
        links = []
    now = int(time.time())
    return [l for l in links if isinstance(l, dict) and int(l.get("e", 0)) > now]


def _save_preview_links(links):
    row = db.session.get(Setting, PREVIEW_KEY)
    value = json.dumps(links, separators=(",", ":"))
    if row is None:
        db.session.add(Setting(key=PREVIEW_KEY, value=value))
    else:
        row.value = value
    db.session.commit()


def create_preview_link(minutes, label=""):
    links = preview_links()
    if len(links) >= PREVIEW_MAX_ACTIVE:
        raise ValueError(f"You already have {PREVIEW_MAX_ACTIVE} active links. Delete some first.")
    now = int(time.time())
    link_id = secrets.token_urlsafe(12)
    links.insert(0, {"i": link_id, "e": now + minutes * 60, "c": now, "m": minutes,
                     "l": label, "t": _preview_serializer().dumps(link_id)})
    _save_preview_links(links)
    return link_id


def delete_preview_link(link_id=None):
    """Delete one link (or all when link_id is None). Returns how many were removed."""
    links = preview_links()
    keep = [] if link_id is None else [l for l in links if l.get("i") != link_id]
    _save_preview_links(keep)
    return len(links) - len(keep)


def preview_seconds_left():
    """Seconds left on this browser's preview access (0 = none). Deleting the link ends it immediately."""
    pid = session.get("preview_id")
    if not pid:
        return 0
    for l in preview_links():
        if l.get("i") == pid:
            return int(l["e"]) - int(time.time())
    session.pop("preview_id", None)
    return 0


BOT_RE = re.compile(r"bot|crawl|spider|slurp|curl|wget|python|httpclient|headless|scan|preview|monitor|facebookexternalhit|go-http|java/|okhttp|axios|node-fetch", re.I)
VISIT_RETENTION_DAYS = 90
VISIT_MAX_ROWS = 200_000         # ASDHEM | hard cap, oldest rows are dropped


def record_visit():
    """Log a page view (skipped for the logged-in admin). Never breaks the page."""
    if session.get("admin_id"):
        return
    try:
        ua = (request.headers.get("User-Agent") or "")[:300]
        db.session.add(Visit(
            ip=(request.remote_addr or "")[:64],
            path=request.full_path.rstrip("?")[:200],
            user_agent=ua,
            referrer=(request.referrer or "")[:300],
            is_bot=not ua or bool(BOT_RE.search(ua)),
        ))
        if random.random() < 0.02:  # occasional cleanup of old data
            db.session.query(Visit).filter(
                Visit.created_at < utcnow() - timedelta(days=VISIT_RETENTION_DAYS)).delete()
            over = db.session.query(Visit).count() - VISIT_MAX_ROWS
            if over > 0:
                oldest = db.session.query(Visit.id).order_by(Visit.id).limit(over).subquery()
                db.session.query(Visit).filter(Visit.id.in_(db.select(oldest.c.id))).delete(synchronize_session=False)
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()

bp = Blueprint("public", __name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]{1,64}@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,24}$")
RATE_LIMIT_PER_HOUR = 5          # per IP
GLOBAL_LIMIT_PER_HOUR = 40       # all visitors together (botnet flood protection)
AUTOREPLY_LIMIT_PER_HOUR = 15    # stops the form being used to spam other people's inboxes
LINK_RE = re.compile(r"(?i)\b(?:https?://|www\.)\S*|\b\S+\.(?:com|net|org|ru|xyz|top|info|io|ly)\S*")
CTRL_RE = re.compile(r"[\x00-\x1f\x7f]+")


def enabled(model, **filters):
    return db.session.execute(
        db.select(model).filter_by(enabled=True, **filters).order_by(model.position, model.id)
    ).scalars().all()


@bp.route("/")
def index():
    record_visit()
    c = get_content()
    preview_left = 0
    if c.maintenance_enabled == "1" and not session.get("admin_id"):
        preview_left = preview_seconds_left()
        if not preview_left:
            return render_template("maintenance.html")
    projects = enabled(Project)
    categories = sorted({p.category for p in projects if p.category})
    return render_template(
        "index.html",
        services=enabled(Service),
        why=enabled(Feature, group="why"),
        hosting=enabled(Feature, group="hosting"),
        badges=enabled(Feature, group="badge"),
        projects=projects,
        categories=categories,
        preview_left=preview_left,
    )


@bp.route("/preview/<token>")
def preview(token):
    """Open a preview link: gives this browser access for as long as the link is active."""
    try:
        link_id = _preview_serializer().loads(token)
    except BadSignature:
        return render_template("error.html", code=404,
                               message="The page you are looking for does not exist."), 404
    if not any(l.get("i") == link_id for l in preview_links()):
        return render_template("error.html", code=410,
                               message="This preview link has expired or was deleted. Ask for a new one."), 410
    session["preview_id"] = link_id
    session.pop("preview_until", None)
    resp = redirect(url_for("public.index"))
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


@bp.post("/contact")
def contact():
    f = request.form
    is_fetch = request.headers.get("X-Requested-With") == "fetch"
    c = get_content()

    def respond(ok, errors=None, status=200):
        if is_fetch:
            return jsonify(ok=ok, errors=errors or {}, message=c.form_success if ok else ""), status
        if ok:
            flash(c.form_success, "success")
        else:
            flash(" ".join((errors or {}).values()), "error")
        return redirect(url_for("public.index") + "#contact")

    # honeypot: bots fill the hidden field – pretend success
    if f.get("website"):
        return respond(True)

    def one_line(v):  # no CR/LF/control chars -> no email header injection
        return CTRL_RE.sub(" ", v or "").strip()

    name = one_line(f.get("name"))
    email = (f.get("email") or "").strip()
    service = one_line(f.get("service"))[:150]
    body = (f.get("message") or "").strip()

    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your full name."
    elif len(name) > 120:
        errors["name"] = "Name is too long."
    if not EMAIL_RE.match(email) or len(email) > 200:
        errors["email"] = "Please enter a valid email address."
    if not service:
        errors["service"] = "Please choose the service you are interested in."
    if len(body) < 10:
        errors["message"] = "Please write a message of at least 10 characters."
    elif len(body) > 5000:
        errors["message"] = "Message is too long (max 5000 characters)."
    if errors:
        return respond(False, errors, 422)

    ip = request.remote_addr or ""
    recent = db.session.query(Message).filter(
        Message.ip == ip, Message.created_at > utcnow() - timedelta(hours=1)
    ).count()
    hour_ago = utcnow() - timedelta(hours=1)
    total_recent = db.session.query(Message).filter(Message.created_at > hour_ago).count()
    if recent >= RATE_LIMIT_PER_HOUR or total_recent >= GLOBAL_LIMIT_PER_HOUR:
        return respond(False, {"_": "Too many messages sent. Please try again later or email us directly."}, 429)

    msg = Message(name=name, email=email, service=service, body=body, ip=ip)
    db.session.add(msg)
    db.session.commit()

    to = c.notify_email or c.contact_email
    if to:
        ok, _ = send_mail(
            to,
            f"New inquiry: {service} – {name}",
            f"New message from the AMXME website contact form\n\n"
            f"Name:    {name}\nEmail:   {email}\nService: {service}\n\n{body}\n\n"
            f"---\nView in admin: {current_app.config['SITE_URL']}/admin/messages/{msg.id}\n",
            reply_to=email,
        )
        if ok:
            msg.emailed = True
            db.session.commit()

    if c.autoreply_enabled == "1" and c.autoreply_body.strip() and total_recent < AUTOREPLY_LIMIT_PER_HOUR:
        safe_name = LINK_RE.sub("", name).strip()[:60] or "there"
        safe_service = LINK_RE.sub("", service).strip()[:80]

        def fill(text):
            for k, v in (("{name}", safe_name), ("{service}", safe_service), ("{email}", email)):
                text = text.replace(k, v)
            return text
        subject = fill(c.autoreply_subject or "We received your message").replace("\n", " ")
        send_mail(email, subject, fill(c.autoreply_body), reply_to=c.contact_email or None,
                  from_name=c.company_name or "AMXME Web Solutions")
    return respond(True)


@bp.route("/robots.txt")
def robots():
    site = current_app.config["SITE_URL"]
    return Response(f"User-agent: *\nDisallow: /admin\nSitemap: {site}/sitemap.xml\n", mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    site = current_app.config["SITE_URL"]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f"<url><loc>{site}/</loc></url></urlset>\n")
    return Response(xml, mimetype="application/xml")
