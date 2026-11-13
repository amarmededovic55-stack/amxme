# Signed: ASDHEM | AMXME Web Solutions
import base64
import hashlib
import hmac
import io
import json
import secrets as _secrets
import time

import pyotp
import qrcode
from datetime import timedelta
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from .content import SECTION_MAP, SECTIONS
from .extensions import db
from .icons import PICKER
from .mailer import smtp_configured
from .models import Activity, AdminUser, Feature, Message, Project, Service, Setting, Visit, utcnow
from sqlalchemy import func
from .uploads import UploadError, delete_upload, save_image

bp = Blueprint("admin", __name__)

MAX_FAILED_LOGINS = 8            # per IP
MAX_FAILED_PER_USER = 20         # per username, from all IPs (distributed guessing)
MAX_FAILED_2FA_PER_USER = 10     # 2FA codes per account, from all IPs
LOCKOUT = timedelta(minutes=15)
IDLE_TIMEOUT = 2 * 60 * 60       # seconds without activity before the admin is signed out
MIN_PASSWORD_LEN = 12
# used so a login for a non-existent user takes as long as a real one (no username probing via timing)
_DUMMY_HASH = generate_password_hash("not-a-real-password-amxme")


def pw_fingerprint(user):
    """Changes whenever the password changes -> old sessions stop working."""
    key = current_app.config["SECRET_KEY"].encode()
    material = user.password_hash
    if user.session_gen:  # ASDHEM | bumped on logout -> stolen/copied session cookies stop working too
        material += f":{user.session_gen}"
    return hmac.new(key, material.encode(), hashlib.sha256).hexdigest()[:32]


TOTP_ISSUER = "AMXME Admin"
PENDING_2FA_TTL = 5 * 60         # seconds to complete the second step
BACKUP_CODE_COUNT = 10


def gen_backup_codes():
    """Return (plaintext list to show once, hashed text to store)."""
    plain = ["-".join([_secrets.token_hex(2) for _ in range(2)]) for _ in range(BACKUP_CODE_COUNT)]
    hashed = "\n".join(generate_password_hash(c) for c in plain)
    return plain, hashed


def check_backup_code(user, code):
    """Consume a backup code if it matches. Returns True and removes it."""
    code = (code or "").strip().lower()
    if not code or not user.backup_codes:
        return False
    rows = [h for h in user.backup_codes.splitlines() if h]
    for i, h in enumerate(rows):
        if check_password_hash(h, code):
            del rows[i]
            user.backup_codes = "\n".join(rows)
            return True
    return False


def verify_totp(user, code):
    """Verify a 6-digit TOTP code, blocking reuse of the same time-step."""
    code = (code or "").strip().replace(" ", "")
    if not (user.totp_secret and code.isdigit()):
        return False
    totp = pyotp.TOTP(user.totp_secret)
    now = time.time()
    for offset in (-1, 0, 1):               # +/- 30s clock drift
        step = int(now // 30) + offset
        if hmac.compare_digest(totp.at(step * 30), code):
            if step <= (user.totp_last or 0):
                return False                 # already used this step -> replay blocked
            user.totp_last = step
            return True
    return False


# ---------------------------------------------------------------- helpers
def log(action, kind="change", user=None):
    db.session.add(Activity(
        action=action[:300], kind=kind, ip=request.remote_addr or "",
        user=user if user is not None else (g.user.username if getattr(g, "user", None) else ""),
    ))


@bp.before_request
def load_user():
    g.user = None
    uid = session.get("admin_id")
    if uid:
        g.user = db.session.get(AdminUser, uid)
        now = int(time.time())
        idle = now - int(session.get("seen", 0) or 0)
        if (not g.user or idle > IDLE_TIMEOUT
                or not hmac.compare_digest(session.get("pw_fp", ""), pw_fingerprint(g.user))):
            g.user = None
            session.clear()
        elif idle > 60:  # refresh at most once a minute
            session["seen"] = now


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.user:
            return redirect(url_for("admin.login", next=request.path))
        return view(*a, **kw)
    return wrapped


@bp.context_processor
def admin_ctx():
    unread = 0
    if getattr(g, "user", None):
        unread = db.session.query(Message).filter_by(is_read=False).count()
    return {"sections": SECTIONS, "collections": COLLECTIONS, "unread": unread}


# ---------------------------------------------------------------- auth
@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("admin.dashboard"))
    error = None
    if request.method == "POST":
        ip = request.remote_addr or ""
        fails = db.session.query(Activity).filter(
            Activity.kind == "auth_fail", Activity.ip == ip, Activity.created_at > utcnow() - LOCKOUT
        ).count()
        username = (request.form.get("username") or "").strip()[:80]
        password = (request.form.get("password") or "")[:200]
        user_fails = db.session.query(Activity).filter(
            Activity.kind == "auth_fail", Activity.action == _fail_msg(username),
            Activity.created_at > utcnow() - LOCKOUT
        ).count()
        if fails >= MAX_FAILED_LOGINS or user_fails >= MAX_FAILED_PER_USER:
            error = "Too many failed attempts. Please wait 15 minutes and try again."
        else:
            user = db.session.execute(db.select(AdminUser).filter_by(username=username)).scalar()
            ok = check_password_hash(user.password_hash if user else _DUMMY_HASH, password)
            if user and ok:
                nxt = request.args.get("next") or ""
                if not nxt.startswith("/admin") or nxt.startswith("//"):
                    nxt = url_for("admin.dashboard")
                if user.totp_enabled and user.totp_secret:
                    session.clear()
                    session["2fa_uid"] = user.id
                    session["2fa_exp"] = int(time.time()) + PENDING_2FA_TTL
                    session["2fa_next"] = nxt
                    return redirect(url_for("admin.login_2fa"))
                _complete_login(user)
                db.session.commit()
                return redirect(nxt)
            log(_fail_msg(username), "auth_fail", "")
            db.session.commit()
            error = "Invalid username or password."
    return render_template("admin/login.html", error=error)


def _fail_msg(username):
    return f"Failed sign-in attempt for '{username[:40]}'"


def _complete_login(user):
    session.clear()
    session.permanent = True
    session["admin_id"] = user.id
    session["pw_fp"] = pw_fingerprint(user)
    session["seen"] = int(time.time())
    user.last_login = utcnow()
    log("Signed in", "auth", user.username)


@bp.route("/login/2fa", methods=["GET", "POST"])
def login_2fa():
    uid = session.get("2fa_uid")
    if not uid or int(session.get("2fa_exp", 0)) < int(time.time()):
        session.pop("2fa_uid", None)
        return redirect(url_for("admin.login"))
    user = db.session.get(AdminUser, uid)
    if not user or not user.totp_enabled:
        session.clear()
        return redirect(url_for("admin.login"))
    error = None
    if request.method == "POST":
        ip = request.remote_addr or ""
        fails = db.session.query(Activity).filter(
            Activity.kind == "auth_fail", Activity.ip == ip, Activity.created_at > utcnow() - LOCKOUT
        ).count()
        user_2fa_fails = db.session.query(Activity).filter(  # ASDHEM | per-account, from all IPs
            Activity.kind == "auth_fail", Activity.action == f"Failed 2FA for '{user.username[:40]}'",
            Activity.created_at > utcnow() - LOCKOUT
        ).count()
        if fails >= MAX_FAILED_LOGINS or user_2fa_fails >= MAX_FAILED_2FA_PER_USER:
            error = "Too many failed attempts. Please wait 15 minutes and try again."
        else:
            code = request.form.get("code") or ""
            if verify_totp(user, code) or check_backup_code(user, code):
                nxt = session.get("2fa_next") or url_for("admin.dashboard")
                _complete_login(user)
                db.session.commit()
                return redirect(nxt)
            log(f"Failed 2FA for '{user.username[:40]}'", "auth_fail", "")
            db.session.commit()
            error = "Invalid authentication code."
    return render_template("admin/login_2fa.html", error=error)


@bp.post("/logout")
def logout():
    if g.user:
        g.user.session_gen = (g.user.session_gen or 0) + 1  # revoke this and every other session
        log("Signed out", "auth")
        db.session.commit()
    session.clear()
    return redirect(url_for("admin.login"))


# ---------------------------------------------------------------- dashboard
@bp.route("/")
@login_required
def dashboard():
    def count(model, **kw):
        return db.session.query(model).filter_by(**kw).count()

    stats = [
        ("Services", count(Service, enabled=True), count(Service), "layers", url_for("admin.collection", kind="services")),
        ("Portfolio projects", count(Project, enabled=True), count(Project), "briefcase", url_for("admin.collection", kind="portfolio")),
        ("Advantages", count(Feature, group="why", enabled=True), count(Feature, group="why"), "award", url_for("admin.collection", kind="why")),
        ("Messages", count(Message, is_read=False), count(Message), "inbox", url_for("admin.messages")),
    ]
    recent = db.session.execute(
        db.select(Activity).where(Activity.kind != "auth_fail").order_by(Activity.created_at.desc()).limit(12)
    ).scalars().all()
    latest = db.session.execute(db.select(Message).order_by(Message.created_at.desc()).limit(5)).scalars().all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent, latest=latest,
                           smtp=smtp_configured())


# ---------------------------------------------------------------- text content
@bp.route("/content/<slug>", methods=["GET", "POST"])
@login_required
def content(slug):
    section = SECTION_MAP.get(slug) or abort(404)
    if request.method == "POST":
        changed = 0
        try:
            for f in section["fields"]:
                key = f["key"]
                row = db.session.get(Setting, key)
                if f["type"] == "image":
                    new = None
                    if request.form.get(f"{key}__remove"):
                        new = ""
                    upload = request.files.get(key)
                    if upload and upload.filename:
                        new = save_image(upload)
                    if new is None:
                        continue
                    if row and row.value:
                        delete_upload(row.value)
                    value = new
                elif f["type"] == "bool":
                    value = "1" if "1" in request.form.getlist(key) else "0"
                else:
                    value = (request.form.get(key) or "").replace("\r\n", "\n").strip()
                if row is None:
                    db.session.add(Setting(key=key, value=value))
                    changed += 1
                elif row.value != value:
                    row.value = value
                    changed += 1
        except UploadError as e:
            db.session.rollback()
            flash(str(e), "error")
            return redirect(request.url)
        if changed:
            log(f"Updated “{section['title']}” ({changed} field{'s' if changed != 1 else ''})")
        db.session.commit()
        flash("Changes saved." if changed else "No changes to save.", "success")
        return redirect(request.url)
    extra = {}
    if slug == "maintenance":
        from .public import PREVIEW_DEFAULT, PREVIEW_DURATIONS, preview_links
        now = int(time.time())
        extra = dict(preview_links=preview_links(), preview_durations=PREVIEW_DURATIONS,
                     preview_default=PREVIEW_DEFAULT, now=now,
                     preview_base=current_app.config["SITE_URL"] + "/preview/",
                     new_link=request.args.get("new", ""))
    return render_template("admin/content_form.html", section=section, **extra)


@bp.post("/preview-link")
@login_required
def preview_link():
    """ASDHEM | Create a preview link with a chosen duration."""
    from .public import PREVIEW_DURATIONS, create_preview_link
    try:
        minutes = int(request.form.get("minutes", ""))
    except ValueError:
        minutes = 0
    if minutes not in dict(PREVIEW_DURATIONS):
        flash("Please choose how long the link should work.", "error")
        return redirect(url_for("admin.content", slug="maintenance"))
    label = " ".join((request.form.get("label") or "").split())[:60]
    try:
        link_id = create_preview_link(minutes, label)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("admin.content", slug="maintenance"))
    flash(f"Preview link created – valid for {dict(PREVIEW_DURATIONS)[minutes]}.", "success")
    return redirect(url_for("admin.content", slug="maintenance", new=link_id) + "#preview-links")


@bp.post("/preview-link/<link_id>/delete")
@login_required
def preview_link_delete(link_id):
    from .public import delete_preview_link
    n = delete_preview_link(link_id)
    flash("Preview link deleted – it no longer works." if n else "That link had already expired.", "success")
    return redirect(url_for("admin.content", slug="maintenance") + "#preview-links")


@bp.post("/preview-links/delete-all")
@login_required
def preview_link_delete_all():
    from .public import delete_preview_link
    n = delete_preview_link(None)
    flash(f"Deleted {n} preview link{'s' if n != 1 else ''}.", "success")
    return redirect(url_for("admin.content", slug="maintenance") + "#preview-links")


# ---------------------------------------------------------------- collections (generic CRUD)
def fld(key, label, type="text", required=False, help=""):
    return {"key": key, "label": label, "type": type, "required": required, "help": help}


COLLECTIONS = {
    "services": {
        "model": Service, "title": "Services", "singular": "Service", "icon": "layers",
        "intro": "Service cards in the “Our Services” section. Drag to reorder.",
        "fields": [
            fld("title", "Service name", required=True),
            fld("description", "Description", "textarea"),
            fld("items", "Included items (one per line)", "lines"),
            fld("icon", "Icon", "icon"),
        ],
        "subtitle": lambda o: o.description,
    },
    "portfolio": {
        "model": Project, "title": "Portfolio", "singular": "Project", "icon": "briefcase",
        "intro": "Projects in the “Our Work” section. Drag to reorder.",
        "fields": [
            fld("title", "Project name", required=True),
            fld("description", "Short description", "textarea"),
            fld("category", "Category", help="Used for the filter buttons, e.g. Business Website, Forum, E-commerce."),
            fld("technologies", "Technologies", help="Comma separated, e.g. WordPress, PHP, MySQL"),
            fld("url", "Project URL", "url", help="Link for the “View Project” button. Leave empty to hide the button."),
            fld("image", "Screenshot / preview", "image", help="Landscape image works best (16:10)."),
        ],
        "subtitle": lambda o: " · ".join(x for x in [o.category, o.technologies] if x),
    },
    "why": {
        "model": Feature, "group": "why", "title": "Why Choose Us", "singular": "Advantage", "icon": "award",
        "intro": "Advantage cards in the “Why Choose AMXME?” section.",
        "fields": [fld("title", "Title", required=True), fld("text", "Text", "textarea"), fld("icon", "Icon", "icon")],
        "subtitle": lambda o: o.text,
    },
    "hosting": {
        "model": Feature, "group": "hosting", "title": "Hosting Highlights", "singular": "Highlight", "icon": "server",
        "intro": "Highlights listed in the Hosting section.",
        "fields": [fld("title", "Title", required=True), fld("text", "Text", "textarea"), fld("icon", "Icon", "icon")],
        "subtitle": lambda o: o.text,
    },
    "badges": {
        "model": Feature, "group": "badge", "title": "Trust Badges", "singular": "Badge", "icon": "shield-check",
        "intro": "Short badges shown in the strip under the hero.",
        "fields": [fld("title", "Text", required=True), fld("icon", "Icon", "icon")],
        "subtitle": lambda o: "",
    },
}


def get_cfg(kind):
    return COLLECTIONS.get(kind) or abort(404)


def query_items(cfg):
    q = db.select(cfg["model"])
    if cfg.get("group"):
        q = q.filter_by(group=cfg["group"])
    return db.session.execute(q.order_by(cfg["model"].position, cfg["model"].id)).scalars().all()


def get_item(cfg, item_id):
    obj = db.session.get(cfg["model"], item_id)
    if not obj or (cfg.get("group") and obj.group != cfg["group"]):
        abort(404)
    return obj


@bp.route("/c/<kind>")
@login_required
def collection(kind):
    cfg = get_cfg(kind)
    return render_template("admin/collection_list.html", kind=kind, cfg=cfg, items=query_items(cfg))


@bp.route("/c/<kind>/new", methods=["GET", "POST"])
@bp.route("/c/<kind>/<int:item_id>", methods=["GET", "POST"])
@login_required
def collection_edit(kind, item_id=None):
    cfg = get_cfg(kind)
    model = cfg["model"]
    obj = get_item(cfg, item_id) if item_id else None
    errors = {}
    if request.method == "POST":
        is_new = obj is None
        if is_new:
            obj = model()
            if cfg.get("group"):
                obj.group = cfg["group"]
            last = query_items(cfg)
            obj.position = (max((i.position or 0) for i in last) + 1) if last else 0
        pending_image = None
        for f in cfg["fields"]:
            key = f["key"]
            if f["type"] == "image":
                if request.form.get(f"{key}__remove"):
                    pending_image = ("", getattr(obj, key, ""))
                up = request.files.get(key)
                if up and up.filename:
                    try:
                        pending_image = (save_image(up), getattr(obj, key, ""))
                    except UploadError as e:
                        errors[key] = str(e)
                continue
            value = (request.form.get(key) or "").replace("\r\n", "\n").strip()
            if f["required"] and not value:
                errors[key] = f"{f['label']} is required."
            if f["type"] == "url" and value and not value.startswith(("http://", "https://", "/", "#")):
                value = "https://" + value
            setattr(obj, key, value)
        obj.enabled = bool(request.form.get("enabled"))
        if errors:
            db.session.rollback()
            if pending_image and pending_image[0]:
                delete_upload(pending_image[0])
            if is_new:
                obj = None
            flash("Please fix the highlighted fields.", "error")
            return render_template("admin/collection_form.html", kind=kind, cfg=cfg, obj=obj,
                                   form=request.form, errors=errors, icons=PICKER), 422
        if pending_image:
            new, old = pending_image
            setattr(obj, "image", new)
            if old and old != new:
                delete_upload(old)
        if is_new:
            db.session.add(obj)
        log(f"{'Added' if is_new else 'Edited'} {cfg['singular'].lower()} “{obj.title}”")
        db.session.commit()
        flash(f"{cfg['singular']} {'added' if is_new else 'saved'}.", "success")
        return redirect(url_for("admin.collection", kind=kind))
    return render_template("admin/collection_form.html", kind=kind, cfg=cfg, obj=obj, form=None,
                           errors=errors, icons=PICKER)


@bp.post("/c/<kind>/<int:item_id>/delete")
@login_required
def collection_delete(kind, item_id):
    cfg = get_cfg(kind)
    obj = get_item(cfg, item_id)
    if getattr(obj, "image", None):
        delete_upload(obj.image)
    log(f"Deleted {cfg['singular'].lower()} “{obj.title}”")
    db.session.delete(obj)
    db.session.commit()
    flash(f"{cfg['singular']} deleted.", "success")
    return redirect(url_for("admin.collection", kind=kind))


@bp.post("/c/<kind>/<int:item_id>/toggle")
@login_required
def collection_toggle(kind, item_id):
    cfg = get_cfg(kind)
    obj = get_item(cfg, item_id)
    obj.enabled = not obj.enabled
    log(f"{'Enabled' if obj.enabled else 'Disabled'} {cfg['singular'].lower()} “{obj.title}”")
    db.session.commit()
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify(ok=True, enabled=obj.enabled)
    return redirect(url_for("admin.collection", kind=kind))


@bp.post("/c/<kind>/reorder")
@login_required
def collection_reorder(kind):
    cfg = get_cfg(kind)
    ids = (request.get_json(silent=True) or {}).get("ids") or []
    items = {i.id: i for i in query_items(cfg)}
    for pos, item_id in enumerate(ids):
        try:
            item = items.get(int(item_id))
        except (TypeError, ValueError):
            continue
        if item:
            item.position = pos
    log(f"Reordered {cfg['title'].lower()}")
    db.session.commit()
    return jsonify(ok=True)


# ---------------------------------------------------------------- messages
@bp.route("/messages")
@login_required
def messages():
    from .public import privacy_cleanup  # ASDHEM | GDPR retention runs before the inbox is shown
    try:
        privacy_cleanup()
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()
    items = db.session.execute(db.select(Message).order_by(Message.created_at.desc())).scalars().all()
    return render_template("admin/messages.html", items=items, smtp=smtp_configured())


@bp.route("/messages/<int:msg_id>")
@login_required
def message(msg_id):
    m = db.session.get(Message, msg_id) or abort(404)
    if not m.is_read:
        m.is_read = True
        db.session.commit()
    return render_template("admin/message.html", m=m)


@bp.post("/messages/<int:msg_id>/delete")
@login_required
def message_delete(msg_id):
    m = db.session.get(Message, msg_id) or abort(404)
    log(f"Deleted message from {m.name}")
    db.session.delete(m)
    db.session.commit()
    flash("Message deleted.", "success")
    return redirect(url_for("admin.messages"))


@bp.post("/messages/<int:msg_id>/unread")
@login_required
def message_unread(msg_id):
    m = db.session.get(Message, msg_id) or abort(404)
    m.is_read = False
    db.session.commit()
    return redirect(url_for("admin.messages"))


# ---------------------------------------------------------------- account
@bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        current = request.form.get("current") or ""
        new = request.form.get("new") or ""
        confirm = request.form.get("confirm") or ""
        if not check_password_hash(g.user.password_hash, current):
            flash("Current password is incorrect.", "error")
        elif len(new) < MIN_PASSWORD_LEN or len(new) > 200:
            flash(f"New password must be {MIN_PASSWORD_LEN}–200 characters long.", "error")
        elif g.user.username.lower() in new.lower() or len(set(new)) < 6:
            flash("New password is too weak (don't use the username or repeated characters).", "error")
        elif new != confirm:
            flash("New passwords do not match.", "error")
        elif new == current:
            flash("New password must be different from the current one.", "error")
        else:
            g.user.password_hash = generate_password_hash(new)
            session["pw_fp"] = pw_fingerprint(g.user)  # keep this session, log out all others
            log("Changed password", "auth")
            db.session.commit()
            flash("Password changed.", "success")
        return redirect(url_for("admin.account"))
    activity = db.session.execute(
        db.select(Activity).where(Activity.kind.in_(["auth", "auth_fail"]))
        .order_by(Activity.created_at.desc()).limit(15)
    ).scalars().all()
    return render_template("admin/account.html", activity=activity,
                           twofa=g.user.totp_enabled)


@bp.post("/account/2fa/setup")
@login_required
def twofa_setup():
    """Step 1: create a fresh secret (kept in the session until confirmed) and show the QR code."""
    if g.user.totp_enabled:
        return redirect(url_for("admin.account"))
    secret = pyotp.random_base32()
    session["twofa_pending"] = secret
    uri = pyotp.TOTP(secret).provisioning_uri(name=g.user.username, issuer_name=TOTP_ISSUER)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_data = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return render_template("admin/twofa_setup.html", secret=secret, qr=qr_data)


@bp.post("/account/2fa/enable")
@login_required
def twofa_enable():
    """Step 2: verify the first code, turn 2FA on, and show one-time backup codes."""
    secret = session.get("twofa_pending")
    if g.user.totp_enabled or not secret:
        return redirect(url_for("admin.account"))
    code = (request.form.get("code") or "").strip().replace(" ", "")
    if not (code.isdigit() and pyotp.TOTP(secret).verify(code, valid_window=1)):
        flash("That code was not correct. Scan the QR code again and enter a fresh code.", "error")
        return redirect(url_for("admin.account"))
    plain, hashed = gen_backup_codes()
    g.user.totp_secret = secret
    g.user.totp_enabled = True
    g.user.totp_last = 0
    g.user.backup_codes = hashed
    session.pop("twofa_pending", None)
    log("Enabled two-factor authentication", "auth")
    db.session.commit()
    flash("Two-factor authentication is now on. Save your backup codes below.", "success")
    return render_template("admin/twofa_codes.html", codes=plain)


@bp.post("/account/2fa/disable")
@login_required
def twofa_disable():
    """Turn 2FA off - requires the current password."""
    if not check_password_hash(g.user.password_hash, request.form.get("password") or ""):
        flash("Password is incorrect. Two-factor authentication was not changed.", "error")
        return redirect(url_for("admin.account"))
    g.user.totp_enabled = False
    g.user.totp_secret = ""
    g.user.totp_last = 0
    g.user.backup_codes = ""
    session.pop("twofa_pending", None)
    log("Disabled two-factor authentication", "auth")
    db.session.commit()
    flash("Two-factor authentication is now off.", "success")
    return redirect(url_for("admin.account"))


# ---------------------------------------------------------------- visitors
PERIODS = {"today": ("Today", None), "7d": ("Last 7 days", 7), "30d": ("Last 30 days", 30), "all": ("Last 90 days", 90)}


def _period_start(period):
    now = utcnow()
    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    return now - timedelta(days=PERIODS[period][1])


@bp.route("/visitors")
@login_required
def visitors():
    period = request.args.get("period", "7d")
    if period not in PERIODS:
        period = "7d"
    show_bots = request.args.get("bots") == "1"
    start = _period_start(period)

    base = db.session.query(Visit).filter(Visit.created_at >= start)
    total_views = base.filter(Visit.is_bot.is_(False)).count()
    unique_ips = base.filter(Visit.is_bot.is_(False)).with_entities(func.count(func.distinct(Visit.ip))).scalar()
    bot_views = base.filter(Visit.is_bot.is_(True)).count()
    today_views = db.session.query(Visit).filter(
        Visit.created_at >= _period_start("today"), Visit.is_bot.is_(False)).count()

    q = db.session.query(
        Visit.ip,
        func.count(Visit.id).label("views"),
        func.min(Visit.created_at).label("first"),
        func.max(Visit.created_at).label("last"),
        func.max(Visit.id).label("last_id"),
        func.max(Visit.is_bot).label("bot"),
    ).filter(Visit.created_at >= start)
    if not show_bots:
        q = q.filter(Visit.is_bot.is_(False))
    rows = q.group_by(Visit.ip).order_by(func.count(Visit.id).desc(), func.max(Visit.created_at).desc()).limit(300).all()
    last_visits = {v.id: v for v in db.session.query(Visit).filter(Visit.id.in_([r.last_id for r in rows])).all()} if rows else {}

    return render_template("admin/visitors.html", rows=rows, last_visits=last_visits, period=period,
                           periods=PERIODS, show_bots=show_bots, total_views=total_views,
                           unique_ips=unique_ips, bot_views=bot_views, today_views=today_views)


@bp.route("/visitors/ip/<path:ip>")
@login_required
def visitor_ip(ip):
    visits = db.session.query(Visit).filter_by(ip=ip).order_by(Visit.created_at.desc()).limit(200).all()
    if not visits:
        abort(404)
    total = db.session.query(Visit).filter_by(ip=ip).count()
    return render_template("admin/visitor_ip.html", ip=ip, visits=visits, total=total)


@bp.post("/visitors/clear")
@login_required
def visitors_clear():
    n = db.session.query(Visit).delete()
    log(f"Cleared visitor statistics ({n} records)")
    db.session.commit()
    flash("Visitor statistics cleared.", "success")
    return redirect(url_for("admin.visitors"))
