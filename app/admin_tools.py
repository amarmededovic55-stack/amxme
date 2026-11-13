# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Admin tools: version history, live preview, media library, replies, backups,
dashboard widgets, GDPR data requests and users with roles. Routes live on the admin blueprint."""
import io
import json
import os
import re
import secrets
import shutil
import socket
import sqlite3
import ssl
import tempfile
import time
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse

from flask import (abort, current_app, flash, g, redirect, render_template, request, send_file, url_for)
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash

from .admin import bp, log, login_required, smtp_configured
from .content import FIELD_SECTION, SECTION_MAP
from .extensions import db
from .history import prune, restore
from .i18n import LANGS
from .mailer import send_mail
from .models import (AdminUser, Client, Invoice, Media, Message, MessageReply, Monitor, Revision, Ticket,
                     TicketMessage, Visit, utcnow)
from .templating import get_content
from .uploads import UploadError, delete_upload, save_image


def owner_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.user:
            return redirect(url_for("admin.login", next=request.path))
        if not g.user.is_owner:
            flash("Only the owner account can open this page.", "error")
            return redirect(url_for("admin.dashboard"))
        return view(*a, **kw)
    return wrapped


# ====================================================================== version history
@bp.route("/history")
@login_required
def history():
    q = db.session.query(Revision)
    section = request.args.get("section")
    if section in SECTION_MAP:
        keys = [f["key"] for f in SECTION_MAP[section]["fields"]]
        keys += [f"{k}__{lang}" for k in keys for lang in LANGS if lang != "en"]
        q = q.filter(Revision.table == "setting", Revision.row_key.in_(keys))
    items = q.order_by(Revision.id.desc()).limit(300).all()
    for r in items:
        try:
            d = json.loads(r.data or "{}")
        except ValueError:
            d = {}
        old = d.get("value") if r.table == "setting" else (d.get("title") or d.get("text") or "")
        r.preview = (str(old or "") if r.action != "create" else "")[:160]
    return render_template("admin/history.html", items=items, section=SECTION_MAP.get(section))


@bp.post("/history/<int:rev_id>/restore")
@login_required
def history_restore(rev_id):
    rev = db.session.get(Revision, rev_id) or abort(404)
    restore(rev)
    log(f"Restored “{rev.label}” from {rev.created_at:%d %b %Y %H:%M}")
    db.session.commit()
    flash("Previous version restored. (This restore can itself be undone in the history.)", "success")
    return redirect(request.referrer or url_for("admin.history"))


# ====================================================================== live preview
@bp.post("/live-preview/<slug>")
@login_required
def live_preview(slug):
    """Render the homepage with the UNSAVED form values of one section (shown in an iframe)."""
    from .public import home_context
    section = SECTION_MAP.get(slug) or abort(404)
    lang = request.form.get("lang", "en")
    g.lang = lang if lang in LANGS else "en"
    c = get_content(g.lang)
    for f in section["fields"]:
        if f["type"] in ("image", "bool"):
            continue
        if g.lang != "en" and not f["i18n"]:
            continue
        v = (request.form.get(f["key"]) or "").replace("\r\n", "\n")
        c[f["key"]] = v if v.strip() or g.lang == "en" else c[f["key"]]
    ctx = home_context()
    ctx["preview_left"] = 0
    resp = current_app.make_response(render_template("index.html", **ctx))
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ====================================================================== media library
def _register_media(url):
    if db.session.query(Media.id).filter_by(url=url).first():
        return
    path = os.path.join(current_app.config["UPLOAD_DIR"], os.path.basename(url))
    w = h = 0
    try:
        with Image.open(path) as im:
            w, h = im.size
    except (OSError, ValueError):
        pass
    db.session.add(Media(url=url, name=os.path.basename(url), width=w, height=h,
                         size=os.path.getsize(path) if os.path.exists(path) else 0))


@bp.route("/media", methods=["GET", "POST"])
@login_required
def media():
    if request.method == "POST":
        done = 0
        for up in request.files.getlist("files")[:20]:
            try:
                url = save_image(up)
            except UploadError as e:
                flash(f"{up.filename}: {e}", "error")
                continue
            if url:
                _register_media(url)
                done += 1
        if done:
            log(f"Uploaded {done} image{'s' if done != 1 else ''} to the media library")
        db.session.commit()
        if done:
            flash(f"{done} image{'s' if done != 1 else ''} uploaded.", "success")
        return redirect(url_for("admin.media"))
    # pick up images uploaded through other forms
    folder = current_app.config["UPLOAD_DIR"]
    for name in sorted(os.listdir(folder)):
        if re.fullmatch(r"[0-9a-f]{32}\.webp", name):
            _register_media(f"/uploads/{name}")
    db.session.commit()
    items = db.session.query(Media).order_by(Media.created_at.desc()).all()
    used = _used_urls()
    for m in items:
        m.used = m.url in used
    return render_template("admin/media.html", items=items, total=sum(m.size or 0 for m in items))


def _used_urls():
    from .models import Post, Project, Setting
    urls = {v for (v,) in db.session.query(Setting.value).filter(Setting.value.like("/uploads/%"))}
    urls |= {v for (v,) in db.session.query(Project.image) if v}
    urls |= {v for (v,) in db.session.query(Post.image) if v}
    text = " ".join(v or "" for (v,) in db.session.query(Post.body))
    urls |= set(re.findall(r"/uploads/[0-9a-f]{32}\.webp", text))
    return urls


@bp.post("/media/<int:media_id>")
@login_required
def media_update(media_id):
    m = db.session.get(Media, media_id) or abort(404)
    m.alt = (request.form.get("alt") or "").strip()[:300]
    db.session.commit()
    flash("Description saved.", "success")
    return redirect(url_for("admin.media") + f"#m{m.id}")


@bp.post("/media/<int:media_id>/delete")
@login_required
def media_delete(media_id):
    m = db.session.get(Media, media_id) or abort(404)
    if m.url in _used_urls():
        flash("This image is still used on the website. Remove it there first.", "error")
        return redirect(url_for("admin.media"))
    delete_upload(m.url)
    log(f"Deleted image {m.name}")
    db.session.delete(m)
    db.session.commit()
    flash("Image deleted.", "success")
    return redirect(url_for("admin.media"))


# ====================================================================== reply to messages
@bp.post("/messages/<int:msg_id>/reply")
@login_required
def message_reply(msg_id):
    m = db.session.get(Message, msg_id) or abort(404)
    body = (request.form.get("body") or "").strip()
    if len(body) < 2:
        flash("Please write a reply.", "error")
        return redirect(url_for("admin.message", msg_id=m.id))
    c = get_content()
    subject = (request.form.get("subject") or f"Re: {m.service}").replace("\n", " ")[:200]
    ok, err = send_mail(m.email, subject, body, reply_to=c.contact_email or None,
                        from_name=c.company_name or "AMXME Web Solutions")
    db.session.add(MessageReply(message_id=m.id, body=body, user=g.user.username, sent=ok))
    log(f"Replied to {m.name}" + ("" if ok else " (email NOT sent)"))
    db.session.commit()
    flash("Reply sent." if ok else f"Reply saved, but the email could not be sent: {err}", "success" if ok else "error")
    return redirect(url_for("admin.message", msg_id=m.id))


def message_replies(msg_id):
    return db.session.query(MessageReply).filter_by(message_id=msg_id).order_by(MessageReply.id).all()


# ====================================================================== backups
BACKUP_RE = re.compile(r"^amxme-backup-\d{8}-\d{6}(-[a-z-]+)?\.zip$")
KEEP_AUTO_BACKUPS = 14


def _db_path():
    return current_app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "", 1)


def create_backup(tag=""):
    """Zip of a consistent database snapshot + all uploaded images. Returns the file name."""
    folder = current_app.config["BACKUP_DIR"]
    os.makedirs(folder, mode=0o700, exist_ok=True)
    name = f"amxme-backup-{datetime.now():%Y%m%d-%H%M%S}{('-' + tag) if tag else ''}.zip"
    with tempfile.TemporaryDirectory() as tmp:
        snap = os.path.join(tmp, "amxme.db")
        src, dst = sqlite3.connect(_db_path()), sqlite3.connect(snap)
        with dst:
            src.backup(dst)
        src.close(); dst.close()
        path = os.path.join(folder, name)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(snap, "amxme.db")
            up = current_app.config["UPLOAD_DIR"]
            for f in os.listdir(up):
                full = os.path.join(up, f)
                if os.path.isfile(full):
                    z.write(full, f"uploads/{f}")
            z.writestr("README.txt", "AMXME Web Solutions backup – signed ASDHEM\n"
                                     f"Created {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        os.chmod(path, 0o600)
    return name


def prune_auto_backups():
    folder = current_app.config["BACKUP_DIR"]
    auto = sorted(f for f in os.listdir(folder) if BACKUP_RE.match(f) and f.endswith("-auto.zip"))
    for f in auto[:-KEEP_AUTO_BACKUPS]:
        os.remove(os.path.join(folder, f))


def list_backups():
    folder = current_app.config["BACKUP_DIR"]
    if not os.path.isdir(folder):
        return []
    out = []
    for f in sorted(os.listdir(folder), reverse=True):
        if BACKUP_RE.match(f):
            st = os.stat(os.path.join(folder, f))
            out.append({"name": f, "size": st.st_size, "time": datetime.fromtimestamp(st.st_mtime)})
    return out


def restore_backup(path):
    with zipfile.ZipFile(path) as z:
        if "amxme.db" not in z.namelist():
            raise ValueError("This file is not an AMXME backup (amxme.db missing).")
        with tempfile.TemporaryDirectory() as tmp:
            z.extract("amxme.db", tmp)
            snap = os.path.join(tmp, "amxme.db")
            con = sqlite3.connect(snap)
            try:
                if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("The database in the backup is damaged.")
                tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {"setting", "admin_user"} <= tables:
                    raise ValueError("The backup does not contain the website tables.")
            finally:
                con.close()
            create_backup("before-restore")
            db.session.remove()
            db.engine.dispose()
            src, dst = sqlite3.connect(snap), sqlite3.connect(_db_path())
            with dst:
                src.backup(dst)
            src.close(); dst.close()
        up = current_app.config["UPLOAD_DIR"]
        for member in z.namelist():
            base = os.path.basename(member)
            if member.startswith("uploads/") and re.fullmatch(r"[0-9a-f]{32}\.webp", base):
                target = os.path.join(up, base)
                if not os.path.exists(target):
                    with z.open(member) as srcf, open(target, "wb") as out:
                        shutil.copyfileobj(srcf, out)


@bp.route("/backups", methods=["GET", "POST"])
@owner_required
def backups():
    if request.method == "POST":
        name = create_backup()
        log(f"Created backup {name}")
        db.session.commit()
        flash("Backup created.", "success")
        return redirect(url_for("admin.backups"))
    return render_template("admin/backups.html", items=list_backups())


@bp.route("/backups/<name>")
@owner_required
def backup_download(name):
    if not BACKUP_RE.match(name):
        abort(404)
    path = os.path.join(current_app.config["BACKUP_DIR"], name)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=name)


@bp.post("/backups/<name>/delete")
@owner_required
def backup_delete(name):
    if not BACKUP_RE.match(name):
        abort(404)
    try:
        os.remove(os.path.join(current_app.config["BACKUP_DIR"], name))
    except OSError:
        abort(404)
    log(f"Deleted backup {name}")
    db.session.commit()
    flash("Backup deleted.", "success")
    return redirect(url_for("admin.backups"))


@bp.post("/backups/restore")
@owner_required
def backup_restore():
    if not check_password_hash(g.user.password_hash, request.form.get("password") or ""):
        flash("Wrong password – nothing was restored.", "error")
        return redirect(url_for("admin.backups"))
    name = request.form.get("name") or ""
    upload = request.files.get("file")
    tmp_path = None
    try:
        if upload and upload.filename:
            fd, tmp_path = tempfile.mkstemp(suffix=".zip")
            os.close(fd)
            upload.save(tmp_path)
            path = tmp_path
        elif BACKUP_RE.match(name):
            path = os.path.join(current_app.config["BACKUP_DIR"], name)
        else:
            abort(400)
        user = g.user.username
        restore_backup(path)
        g.user = None
        log(f"Restored backup {upload.filename if upload and upload.filename else name}", user=user)
        db.session.commit()
        flash("Backup restored. A safety copy of the previous state was saved first. Please sign in again.", "success")
    except (ValueError, zipfile.BadZipFile) as e:
        flash(str(e) or "Not a valid backup file.", "error")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
    return redirect(url_for("admin.backups"))


# ====================================================================== dashboard widgets
_ssl_cache = {}


def ssl_days_left(host, port=443):
    hit = _ssl_cache.get(host)
    if hit and hit[0] > time.time():
        return hit[1]
    days = None
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=4) as sock, ctx.wrap_socket(sock, server_hostname=host) as s:
            exp = datetime.strptime(s.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days = (exp - datetime.utcnow()).days
    except (OSError, ssl.SSLError, KeyError, ValueError):
        days = None
    _ssl_cache[host] = (time.time() + 3600, days)
    return days


def dashboard_widgets():
    now = utcnow()
    host = urlparse(current_app.config["SITE_URL"]).hostname or "amxme.info"
    days = []
    start = (now - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.session.query(Visit.created_at).filter(Visit.created_at >= start, Visit.is_bot.is_(False)).all()
    counts = {}
    for (ts,) in rows:
        counts[ts.date()] = counts.get(ts.date(), 0) + 1
    for i in range(14):
        d = (start + timedelta(days=i)).date()
        days.append({"day": d, "n": counts.get(d, 0)})
    peak = max([x["n"] for x in days] + [1])
    monitors = db.session.query(Monitor).filter_by(enabled=True).all()
    usage = shutil.disk_usage(current_app.config["DATA_DIR"])
    backups_ = list_backups()
    return {
        "ssl_days": ssl_days_left(host), "host": host,
        "visits": days, "peak": peak, "visits_total": sum(x["n"] for x in days),
        "msgs_week": db.session.query(Message).filter(Message.created_at >= now - timedelta(days=7)).count(),
        "mon_up": sum(1 for m in monitors if m.status == "up"),
        "mon_down": [m for m in monitors if m.status == "down"], "mon_total": len(monitors),
        "tickets_open": db.session.query(Ticket).filter(Ticket.status == "open").count(),
        "disk_free": usage.free, "disk_pct": round(usage.used / usage.total * 100),
        "last_backup": backups_[0]["time"] if backups_ else None,
        "smtp": smtp_configured(),
    }


# ====================================================================== GDPR data requests
def _person_data(email):
    email = email.strip().lower()
    msgs = db.session.query(Message).filter(db.func.lower(Message.email) == email).all()
    client = db.session.query(Client).filter(db.func.lower(Client.email) == email).first()
    data = {"email": email, "exported_at": utcnow().isoformat(), "contact_messages": [], "client_account": None}
    for m in msgs:
        data["contact_messages"].append({
            "received": m.created_at.isoformat(), "name": m.name, "email": m.email, "service": m.service,
            "message": m.body, "replies": [{"sent": r.created_at.isoformat(), "text": r.body}
                                            for r in message_replies(m.id)]})
    if client:
        tickets = db.session.query(Ticket).filter_by(client_id=client.id).all()
        data["client_account"] = {
            "name": client.name, "company": client.company, "email": client.email, "created": client.created_at.isoformat(),
            "websites": [{"name": m.name, "url": m.url} for m in db.session.query(Monitor).filter_by(client_id=client.id)],
            "invoices": [{"number": i.number, "title": i.title, "amount": i.amount, "status": i.status,
                          "issued": i.issued_at.isoformat()} for i in db.session.query(Invoice).filter_by(client_id=client.id)],
            "tickets": [{"subject": t.subject, "status": t.status, "messages": [
                {"from": x.author, "time": x.created_at.isoformat(), "text": x.body}
                for x in db.session.query(TicketMessage).filter_by(ticket_id=t.id).order_by(TicketMessage.id)]}
                for t in tickets],
        }
    return data, msgs, client


@bp.route("/privacy-tools", methods=["GET", "POST"])
@owner_required
def privacy_tools():
    email = (request.values.get("email") or "").strip()
    found = None
    if email:
        data, msgs, client = _person_data(email)
        found = {"data": data, "msgs": msgs, "client": client}
        action = request.form.get("action")
        if request.method == "POST" and action == "export":
            log(f"GDPR export for {email}")
            db.session.commit()
            buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode())
            return send_file(buf, mimetype="application/json", as_attachment=True,
                             download_name=f"gdpr-export-{re.sub(r'[^a-z0-9]+', '-', email.lower())}.json")
        if request.method == "POST" and action == "delete":
            if request.form.get("confirm") != "DELETE":
                flash("Type DELETE to confirm.", "error")
            else:
                for m in msgs:
                    db.session.query(MessageReply).filter_by(message_id=m.id).delete()
                    db.session.delete(m)
                if client:
                    for inv in db.session.query(Invoice).filter_by(client_id=client.id):
                        if inv.file:
                            try:
                                os.remove(os.path.join(current_app.config["PRIVATE_DIR"], inv.file))
                            except OSError:
                                pass
                    db.session.delete(client)
                log(f"GDPR deletion for {email} ({len(msgs)} messages{', client account' if client else ''})")
                db.session.commit()
                flash("All data of this person was deleted.", "success")
                return redirect(url_for("admin.privacy_tools"))
    return render_template("admin/privacy_tools.html", email=email, found=found)


# ====================================================================== users & roles
@bp.route("/users", methods=["GET", "POST"])
@owner_required
def users():
    new_password = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            username = re.sub(r"[^A-Za-z0-9._-]", "", request.form.get("username") or "")[:40]
            role = "owner" if request.form.get("role") == "owner" else "editor"
            if len(username) < 3:
                flash("Username must have at least 3 characters (letters, numbers, . _ -).", "error")
            elif db.session.query(AdminUser).filter_by(username=username).first():
                flash("This username already exists.", "error")
            else:
                new_password = secrets.token_urlsafe(12)
                db.session.add(AdminUser(username=username, role=role, password_hash=generate_password_hash(new_password)))
                log(f"Added {role} account “{username}”")
                db.session.commit()
                flash(f"Account “{username}” created. Give them the password below – it is shown only once.", "success")
        else:
            u = db.session.get(AdminUser, int(request.form.get("user_id") or 0)) or abort(404)
            owners = db.session.query(AdminUser).filter_by(role="owner").count()
            if action == "role":
                role = "owner" if request.form.get("role") == "owner" else "editor"
                if u.id == g.user.id and role != "owner":
                    flash("You cannot remove your own owner role.", "error")
                elif u.role == "owner" and role != "owner" and owners <= 1:
                    flash("There must always be at least one owner.", "error")
                else:
                    u.role = role
                    log(f"Changed role of “{u.username}” to {role}")
                    db.session.commit()
                    flash("Role updated.", "success")
            elif action == "reset":
                new_password = secrets.token_urlsafe(12)
                u.password_hash = generate_password_hash(new_password)
                u.session_gen = (u.session_gen or 0) + 1
                log(f"Reset password of “{u.username}”")
                db.session.commit()
                flash(f"New password for “{u.username}” – shown only once.", "success")
            elif action == "delete":
                if u.id == g.user.id:
                    flash("You cannot delete your own account.", "error")
                elif u.role == "owner" and owners <= 1:
                    flash("There must always be at least one owner.", "error")
                else:
                    log(f"Deleted account “{u.username}”")
                    db.session.delete(u)
                    db.session.commit()
                    flash("Account deleted.", "success")
    accounts = db.session.query(AdminUser).order_by(AdminUser.id).all()
    return render_template("admin/users.html", accounts=accounts, new_password=new_password)


def cleanup():
    """Called from the periodic privacy cleanup."""
    prune()
