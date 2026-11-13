# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Admin side of monitoring and the client portal: clients, websites (monitors), invoices, tickets."""
import os
import re
import uuid
from datetime import date

from flask import abort, current_app, flash, g, redirect, render_template, request, send_file, url_for

from .admin import bp, log, login_required
from .admin_tools import owner_required
from .extensions import db
from .i18n import LANGS
from .mailer import send_mail
from .models import Announcement, Client, Contract, Invoice, Monitor, MonitorCheck, Ticket, TicketFile, TicketMessage, utcnow
from .monitor import check_monitor, daily_bars, uptime
from .portal import files_by_message, password_link, save_ticket_files, send_ticket_file

EMAIL_RE = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$")


# ====================================================================== monitors
@bp.route("/monitors", methods=["GET", "POST"])
@owner_required
def monitors():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()[:120]
        url = (request.form.get("url") or "").strip()[:300]
        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url
        if not name or not re.match(r"^https?://[^\s/$.?#].[^\s]*$", url):
            flash("Please enter a name and a valid URL.", "error")
        else:
            cid = int(request.form.get("client_id") or 0) or None
            m = Monitor(name=name, url=url, client_id=cid, public=bool(request.form.get("public")))
            db.session.add(m)
            db.session.flush()
            check_monitor(m)
            log(f"Added monitor “{name}”")
            db.session.commit()
            flash(f"“{name}” added and checked: {m.status.upper()}.", "success")
        return redirect(url_for("admin.monitors"))
    items = db.session.query(Monitor).order_by(Monitor.position, Monitor.id).all()
    for m in items:
        m.uptime30 = uptime(m.id, 30)
        m.bars = daily_bars(m.id, 30)
    clients = db.session.query(Client).order_by(Client.name).all()
    return render_template("admin/monitors.html", items=items, clients=clients,
                           client_names={c.id: c.name for c in clients})


@bp.post("/monitors/<int:mid>")
@owner_required
def monitor_action(mid):
    m = db.session.get(Monitor, mid) or abort(404)
    action = request.form.get("action")
    if action == "check":
        check_monitor(m)
        flash(f"{m.name}: {m.status.upper()} ({m.last_ms} ms).", "success")
    elif action == "toggle_public":
        m.public = not m.public
    elif action == "toggle":
        m.enabled = not m.enabled
    elif action == "client":
        m.client_id = int(request.form.get("client_id") or 0) or None
    elif action == "delete":
        db.session.query(MonitorCheck).filter_by(monitor_id=m.id).delete()
        log(f"Deleted monitor “{m.name}”")
        db.session.delete(m)
    db.session.commit()
    return redirect(url_for("admin.monitors"))


# ====================================================================== clients
@bp.route("/clients", methods=["GET", "POST"])
@owner_required
def clients():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()[:120]
        email = (request.form.get("email") or "").strip().lower()[:200]
        lang = request.form.get("lang") if request.form.get("lang") in LANGS else "de"
        if len(name) < 2 or not EMAIL_RE.match(email):
            flash("Please enter a name and a valid email.", "error")
        elif db.session.query(Client).filter(db.func.lower(Client.email) == email).first():
            flash("A client with this email already exists.", "error")
        else:
            c = Client(name=name, email=email, company=(request.form.get("company") or "").strip()[:160], lang=lang)
            db.session.add(c)
            db.session.flush()
            log(f"Added client “{name}”")
            db.session.commit()
            flash("Client added. Send the invitation so they can set a password.", "success")
            return redirect(url_for("admin.client", client_id=c.id))
        return redirect(url_for("admin.clients"))
    items = db.session.query(Client).order_by(Client.created_at.desc()).all()
    open_t = dict(db.session.query(Ticket.client_id, db.func.count(Ticket.id)).filter(Ticket.status == "open")
                  .group_by(Ticket.client_id).all())
    return render_template("admin/clients.html", items=items, open_t=open_t, langs=LANGS)


@bp.route("/clients/<int:client_id>", methods=["GET", "POST"])
@owner_required
def client(client_id):
    c = db.session.get(Client, client_id) or abort(404)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "save":
            c.name = (request.form.get("name") or c.name).strip()[:120]
            c.company = (request.form.get("company") or "").strip()[:160]
            c.lang = request.form.get("lang") if request.form.get("lang") in LANGS else c.lang
            c.notes = (request.form.get("notes") or "").strip()[:4000]
            for fld, n in (("street", 160), ("city", 120), ("country", 80), ("phone", 60), ("vat_id", 40)):
                setattr(c, fld, (request.form.get(fld) or "").strip()[:n])
            c.active = bool(request.form.get("active"))
            flash("Client saved.", "success")
        elif action == "invite":
            link = password_link(c)
            texts = {
                "de": ("Ihr Zugang zum AMXME Kundenportal", f"Hallo {c.name},\n\nIhr Zugang zum AMXME Kundenportal ist bereit. "
                       f"Bitte legen Sie hier Ihr Passwort fest (Link 72 Stunden gültig):\n\n{link}\n\nViele Grüße\nAMXME Web Solutions"),
                "hr": ("Vaš pristup AMXME portalu za klijente", f"Pozdrav {c.name},\n\nvaš pristup AMXME portalu je spreman. "
                       f"Ovdje postavite lozinku (poveznica vrijedi 72 sata):\n\n{link}\n\nLijep pozdrav,\nAMXME Web Solutions"),
                "en": ("Your access to the AMXME client portal", f"Hello {c.name},\n\nyour access to the AMXME client portal is ready. "
                       f"Please set your password here (link valid for 72 hours):\n\n{link}\n\nBest regards,\nAMXME Web Solutions"),
            }
            subj, body = texts.get(c.lang, texts["en"])
            ok, err = send_mail(c.email, subj, body, from_name="AMXME Web Solutions")
            log(f"Sent portal invitation to {c.email}" + ("" if ok else " (FAILED)"))
            flash("Invitation sent." if ok else f"Email failed ({err}). Copy this link manually: {link}",
                  "success" if ok else "error")
        elif action == "invoice":
            up = request.files.get("file")
            head = up.stream.read(5) if up and up.filename else b""
            if head != b"%PDF-":
                flash("Please choose a PDF file.", "error")
            else:
                up.stream.seek(0)
                name = f"{uuid.uuid4().hex}.pdf"
                path = os.path.join(current_app.config["PRIVATE_DIR"], name)
                up.save(path)
                os.chmod(path, 0o600)
                db.session.add(Invoice(client_id=c.id, file=name, number=(request.form.get("number") or "").strip()[:60],
                                       title=(request.form.get("title") or "").strip()[:200],
                                       amount=(request.form.get("amount") or "").strip()[:40]))
                log(f"Uploaded invoice for {c.name}")
                flash("Invoice uploaded – the client can download it in the portal.", "success")
        elif action in ("inv_paid", "inv_delete"):
            inv = db.session.get(Invoice, int(request.form.get("invoice_id") or 0))
            if inv and inv.client_id == c.id:
                if action == "inv_paid":
                    inv.status = "open" if inv.status == "paid" else "paid"
                else:
                    try:
                        os.remove(os.path.join(current_app.config["PRIVATE_DIR"], inv.file))
                    except OSError:
                        pass
                    db.session.delete(inv)
        elif action == "contract_add":
            def d(v):
                try:
                    return date.fromisoformat(v) if v else None
                except ValueError:
                    return None
            title = (request.form.get("title") or "").strip()[:200]
            if title:
                db.session.add(Contract(client_id=c.id, title=title, kind=request.form.get("kind") or "hosting",
                                        domain=(request.form.get("domain") or "").strip()[:200],
                                        start_date=d(request.form.get("start")), renewal_date=d(request.form.get("renewal")),
                                        note=(request.form.get("note") or "").strip()[:300]))
                log(f"Added service “{title}” for {c.name}")
                flash("Service added – the client sees it in the portal.", "success")
        elif action in ("contract_end", "contract_delete"):
            ct = db.session.get(Contract, int(request.form.get("contract_id") or 0))
            if ct and ct.client_id == c.id:
                if action == "contract_end":
                    ct.status = "active" if ct.status == "ended" else "ended"
                else:
                    db.session.delete(ct)
        elif action == "delete":
            for inv in db.session.query(Invoice).filter_by(client_id=c.id):
                try:
                    os.remove(os.path.join(current_app.config["PRIVATE_DIR"], inv.file))
                except OSError:
                    pass
            log(f"Deleted client “{c.name}”")
            db.session.delete(c)
            db.session.commit()
            flash("Client deleted.", "success")
            return redirect(url_for("admin.clients"))
        db.session.commit()
        return redirect(url_for("admin.client", client_id=c.id))
    sites = db.session.query(Monitor).filter_by(client_id=c.id).all()
    invoices = db.session.query(Invoice).filter_by(client_id=c.id).order_by(Invoice.issued_at.desc()).all()
    contracts = db.session.query(Contract).filter_by(client_id=c.id).order_by(Contract.status, Contract.renewal_date).all()
    tickets = db.session.query(Ticket).filter_by(client_id=c.id).order_by(Ticket.updated_at.desc()).all()
    return render_template("admin/client.html", c=c, sites=sites, invoices=invoices, tickets=tickets, langs=LANGS,
                           contracts=contracts)


@bp.route("/invoices/<int:inv_id>")
@owner_required
def invoice_file(inv_id):
    inv = db.session.get(Invoice, inv_id) or abort(404)
    path = os.path.join(current_app.config["PRIVATE_DIR"], os.path.basename(inv.file))
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="application/pdf", download_name=f"{inv.number or 'invoice'}.pdf")


# ====================================================================== tickets
@bp.route("/tickets")
@login_required
def tickets():
    status = request.args.get("status", "open")
    q = db.session.query(Ticket)
    if status in ("open", "answered", "closed"):
        q = q.filter(Ticket.status == status)
    items = q.order_by(Ticket.updated_at.desc()).limit(300).all()
    names = {c.id: c.name for c in db.session.query(Client)}
    return render_template("admin/tickets.html", items=items, names=names, status=status)


@bp.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def ticket_admin(ticket_id):
    tk = db.session.get(Ticket, ticket_id) or abort(404)
    c = db.session.get(Client, tk.client_id)
    if request.method == "POST":
        body = (request.form.get("body") or "").strip()[:5000]
        if request.form.get("action") == "close":
            tk.status = "closed"
        elif len(body) >= 2:
            msg = TicketMessage(ticket_id=tk.id, author="admin", body=body)
            db.session.add(msg)
            db.session.flush()
            save_ticket_files(tk, msg)
            tk.status, tk.updated_at = "answered", utcnow()
            if c and c.notify:
                portal = current_app.config["SITE_URL"] + url_for("portal.ticket", ticket_id=tk.id)
                send_mail(c.email, f"Re: {tk.subject}", f"{body}\n\n—\n{portal}\n", from_name="AMXME Web Solutions")
            log(f"Answered ticket “{tk.subject}”")
        db.session.commit()
        return redirect(url_for("admin.ticket_admin", ticket_id=tk.id))
    msgs = db.session.query(TicketMessage).filter_by(ticket_id=tk.id).order_by(TicketMessage.id).all()
    return render_template("admin/ticket.html", tk=tk, c=c, msgs=msgs, files=files_by_message(tk.id))


@bp.route("/ticket-file/<int:file_id>")
@login_required
def ticket_file_admin(file_id):
    f = db.session.get(TicketFile, file_id) or abort(404)
    return send_ticket_file(f)


# ====================================================================== announcements for the client portal
@bp.route("/announcements", methods=["GET", "POST"])
@owner_required
def announcements():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            title = (request.form.get("title") or "").strip()[:200]
            if title:
                level = request.form.get("level") if request.form.get("level") in ("info", "maintenance", "important") else "info"
                a = Announcement(title=title, body=(request.form.get("body") or "").strip()[:4000], level=level)
                db.session.add(a)
                log(f"Posted announcement “{title}”")
                if request.form.get("email"):
                    sent = 0
                    for cl in db.session.query(Client).filter_by(active=True, notify=True):
                        ok, _ = send_mail(cl.email, title, f"{a.body}\n\n—\n{current_app.config['SITE_URL']}/portal/",
                                          from_name="AMXME Web Solutions")
                        sent += 1 if ok else 0
                    flash(f"Announcement posted and emailed to {sent} client(s).", "success")
                else:
                    flash("Announcement posted in the client portal.", "success")
        else:
            a = db.session.get(Announcement, int(request.form.get("id") or 0)) or abort(404)
            if action == "toggle":
                a.active = not a.active
            elif action == "delete":
                db.session.delete(a)
        db.session.commit()
        return redirect(url_for("admin.announcements"))
    items = db.session.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return render_template("admin/announcements.html", items=items)
