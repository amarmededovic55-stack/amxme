# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Client portal (/portal): website status & SSL, invoices (PDF), support tickets."""
import hashlib
import hmac
import os
import time
from datetime import timedelta
from functools import wraps

from flask import (Blueprint, abort, current_app, flash, g, redirect, render_template, request, send_file,
                   session, url_for)
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .i18n import LANGS, t
from .mailer import send_mail
from .models import Activity, Client, Invoice, Monitor, Ticket, TicketMessage, utcnow
from .monitor import uptime

bp = Blueprint("portal", __name__)
IDLE = 4 * 60 * 60
LOCKOUT = timedelta(minutes=15)
MAX_FAILS = 8
_DUMMY = generate_password_hash("portal-dummy-password")


def _fp(client):
    key = current_app.config["SECRET_KEY"].encode()
    return hmac.new(key, f"{client.password_hash}:{client.session_gen}".encode(), hashlib.sha256).hexdigest()[:32]


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="amxme-portal-password")


def password_link(client):
    token = _serializer().dumps({"c": client.id, "g": client.session_gen})
    return current_app.config["SITE_URL"] + url_for("portal.set_password", token=token)


def _log(action, kind="portal"):
    db.session.add(Activity(action=action[:300], kind=kind, ip=request.remote_addr or "", user="portal"))


@bp.before_request
def load_client():
    g.client = None
    cid = session.get("client_id")
    if cid:
        c = db.session.get(Client, cid)
        now = int(time.time())
        if (not c or not c.active or now - int(session.get("client_seen", 0)) > IDLE
                or not hmac.compare_digest(session.get("client_fp", ""), _fp(c))):
            for k in ("client_id", "client_fp", "client_seen"):
                session.pop(k, None)
        else:
            g.client = c
            session["client_seen"] = now
    lang = request.args.get("lang")
    if lang in LANGS:
        session["lang"] = lang
    g.lang = (g.client.lang if g.client and g.client.lang in LANGS else None) or session.get("lang") or "de"


@bp.after_request
def no_store(resp):
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


def client_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.client:
            return redirect(url_for("portal.login"))
        return view(*a, **kw)
    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.client:
        return redirect(url_for("portal.home"))
    if request.method == "POST":
        ip = request.remote_addr or ""
        fails = db.session.query(Activity).filter(Activity.kind == "portal_fail", Activity.ip == ip,
                                                  Activity.created_at > utcnow() - LOCKOUT).count()
        if fails >= MAX_FAILS:
            flash(t("p_locked"), "error")
            return render_template("portal/login.html"), 429
        email = (request.form.get("email") or "").strip().lower()
        c = db.session.query(Client).filter(db.func.lower(Client.email) == email).first()
        ok = check_password_hash(c.password_hash if c and c.password_hash else _DUMMY, request.form.get("password") or "")
        if not (c and c.active and c.password_hash and ok):
            _log(f"Portal login failed for {email[:80]}", "portal_fail")
            db.session.commit()
            flash(t("p_bad_login"), "error")
            return render_template("portal/login.html"), 401
        session.clear()
        session.update(client_id=c.id, client_fp=_fp(c), client_seen=int(time.time()), lang=c.lang)
        c.last_login = utcnow()
        _log(f"Client {c.email} signed in")
        db.session.commit()
        return redirect(url_for("portal.home"))
    return render_template("portal/login.html")


@bp.post("/logout")
def logout():
    for k in ("client_id", "client_fp", "client_seen"):
        session.pop(k, None)
    return redirect(url_for("portal.login"))


@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        ip = request.remote_addr or ""
        recent = db.session.query(Activity).filter(Activity.kind == "portal_reset", Activity.ip == ip,
                                                   Activity.created_at > utcnow() - timedelta(hours=1)).count()
        email = (request.form.get("email") or "").strip().lower()
        c = db.session.query(Client).filter(db.func.lower(Client.email) == email).first()
        if c and c.active and recent < 5:
            send_mail(c.email, t("p_set_pw") + " – AMXME", f"{t('p_hello')} {c.name},\n\n{password_link(c)}\n\n(72 h)\n",
                      from_name="AMXME Web Solutions")
        _log(f"Password link requested for {email[:80]}", "portal_reset")
        db.session.commit()
        flash(t("p_reset_sent"), "success")
        return redirect(url_for("portal.login"))
    return render_template("portal/forgot.html")


@bp.route("/set-password/<token>", methods=["GET", "POST"])
def set_password(token):
    try:
        data = _serializer().loads(token, max_age=72 * 3600)
    except (BadSignature, SignatureExpired):
        data = None
    c = db.session.get(Client, data.get("c")) if isinstance(data, dict) else None
    if not c or c.session_gen != data.get("g") or not c.active:
        flash(t("p_link_invalid"), "error")
        return redirect(url_for("portal.login"))
    g.lang = c.lang if c.lang in LANGS else g.lang
    if request.method == "POST":
        pw = request.form.get("password") or ""
        if len(pw) < 10:
            flash(t("p_pw_short"), "error")
        else:
            c.password_hash = generate_password_hash(pw)
            c.session_gen = (c.session_gen or 0) + 1      # link can be used only once
            _log(f"Client {c.email} set a new password")
            db.session.commit()
            flash(t("p_pw_set"), "success")
            return redirect(url_for("portal.login"))
    return render_template("portal/set_password.html", client=c)


@bp.route("/")
@client_required
def home():
    c = g.client
    sites = db.session.query(Monitor).filter_by(client_id=c.id).order_by(Monitor.position, Monitor.id).all()
    for m in sites:
        m.uptime30 = uptime(m.id, 30)
    invoices = db.session.query(Invoice).filter_by(client_id=c.id).order_by(Invoice.issued_at.desc()).all()
    tickets = db.session.query(Ticket).filter_by(client_id=c.id).order_by(Ticket.updated_at.desc()).all()
    return render_template("portal/home.html", sites=sites, invoices=invoices, tickets=tickets)


@bp.route("/invoice/<int:inv_id>")
@client_required
def invoice(inv_id):
    inv = db.session.get(Invoice, inv_id)
    if not inv or inv.client_id != g.client.id or not inv.file:
        abort(404)
    path = os.path.join(current_app.config["PRIVATE_DIR"], os.path.basename(inv.file))
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="application/pdf", as_attachment=True,
                     download_name=f"{inv.number or 'invoice'}.pdf".replace("/", "-"))


def _notify_admin(subject, body):
    from .templating import get_content
    c = get_content("en")
    to = c.notify_email or c.contact_email
    if to:
        send_mail(to, subject, body, from_name="AMXME Portal")


@bp.post("/tickets")
@client_required
def ticket_new():
    subject = (request.form.get("subject") or "").strip()[:200]
    body = (request.form.get("body") or "").strip()[:5000]
    if len(subject) < 3 or len(body) < 5:
        flash(t("err_message"), "error")
        return redirect(url_for("portal.home") + "#tickets")
    tk = Ticket(client_id=g.client.id, subject=subject)
    db.session.add(tk)
    db.session.flush()
    db.session.add(TicketMessage(ticket_id=tk.id, author="client", body=body))
    db.session.commit()
    _notify_admin(f"New support request: {subject}",
                  f"{g.client.name} ({g.client.email}) wrote:\n\n{body}\n\n{current_app.config['SITE_URL']}/admin/tickets/{tk.id}\n")
    flash(t("p_ticket_sent"), "success")
    return redirect(url_for("portal.ticket", ticket_id=tk.id))


@bp.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@client_required
def ticket(ticket_id):
    tk = db.session.get(Ticket, ticket_id)
    if not tk or tk.client_id != g.client.id:
        abort(404)
    if request.method == "POST":
        body = (request.form.get("body") or "").strip()[:5000]
        if len(body) >= 2:
            db.session.add(TicketMessage(ticket_id=tk.id, author="client", body=body))
            tk.status, tk.updated_at = "open", utcnow()
            db.session.commit()
            _notify_admin(f"Reply on: {tk.subject}", f"{g.client.name} wrote:\n\n{body}\n\n"
                                                      f"{current_app.config['SITE_URL']}/admin/tickets/{tk.id}\n")
        return redirect(url_for("portal.ticket", ticket_id=tk.id))
    msgs = db.session.query(TicketMessage).filter_by(ticket_id=tk.id).order_by(TicketMessage.id).all()
    return render_template("portal/ticket.html", tk=tk, msgs=msgs)


@bp.route("/password", methods=["GET", "POST"])
@client_required
def password():
    if request.method == "POST":
        c = g.client
        if not check_password_hash(c.password_hash, request.form.get("current") or ""):
            flash(t("p_bad_login"), "error")
        elif len(request.form.get("password") or "") < 10:
            flash(t("p_pw_short"), "error")
        else:
            c.password_hash = generate_password_hash(request.form["password"])
            c.session_gen = (c.session_gen or 0) + 1
            session["client_fp"] = _fp(c)
            db.session.commit()
            flash(t("p_pw_set"), "success")
            return redirect(url_for("portal.home"))
    return render_template("portal/password.html")
