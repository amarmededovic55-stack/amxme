# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Invoice generator: fill in the key details, get a German-law compliant PDF (§ 14 UStG),
edit it any time and send it to the client by email + client portal with one click."""
import json
import os
import re
import uuid
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from flask import abort, current_app, flash, g, redirect, render_template, request, send_file, url_for

from .admin import bp, log
from .admin_tools import owner_required
from .extensions import db
from .mailer import send_mail
from .models import Client, Invoice, utcnow
from .pdf import PDF
from .templating import get_content

L = {
    "de": dict(invoice="Rechnung", number="Rechnungsnummer", date="Rechnungsdatum", period="Leistungszeitraum",
               due="Zahlbar bis", customer="Kundennummer", pos="Pos.", desc="Beschreibung", qty="Menge",
               unit="Einzelpreis", total="Gesamt", net="Nettobetrag", vat="zzgl. USt. {r} %", gross="Rechnungsbetrag",
               small="Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleinunternehmerregelung).",
               pay="Bitte überweisen Sie den Rechnungsbetrag bis zum {due} unter Angabe der Rechnungsnummer auf folgendes Konto:",
               thanks="Vielen Dank für Ihren Auftrag!", tax="Steuernummer", vatid="USt-IdNr.", page="Seite",
               subject="Ihre Rechnung {n} – {c}",
               mail="Hallo {name},\n\nanbei erhalten Sie Ihre Rechnung {n} über {amount}.\nBitte überweisen Sie den Betrag bis zum {due}.\n\nSie finden die Rechnung auch jederzeit in Ihrem Kundenportal:\n{portal}\n\nVielen Dank und viele Grüße\n{c}"),
    "en": dict(invoice="Invoice", number="Invoice number", date="Invoice date", period="Service period",
               due="Due date", customer="Customer no.", pos="No.", desc="Description", qty="Qty",
               unit="Unit price", total="Total", net="Net amount", vat="plus VAT {r} %", gross="Total amount",
               small="No VAT is charged according to § 19 UStG (German small business regulation).",
               pay="Please transfer the amount by {due}, quoting the invoice number, to the following account:",
               thanks="Thank you for your business!", tax="Tax number", vatid="VAT ID", page="Page",
               subject="Your invoice {n} – {c}",
               mail="Hello {name},\n\nplease find attached your invoice {n} for {amount}.\nPlease transfer the amount by {due}.\n\nYou can also find the invoice in your client portal at any time:\n{portal}\n\nThank you and best regards,\n{c}"),
    "hr": dict(invoice="Račun", number="Broj računa", date="Datum računa", period="Razdoblje usluge",
               due="Rok plaćanja", customer="Broj kupca", pos="Br.", desc="Opis", qty="Kol.",
               unit="Cijena", total="Ukupno", net="Neto iznos", vat="PDV {r} %", gross="Ukupan iznos",
               small="PDV se ne obračunava prema § 19 njemačkog Zakona o PDV-u (mali poduzetnik).",
               pay="Molimo uplatite iznos do {due} uz navođenje broja računa na sljedeći račun:",
               thanks="Hvala na povjerenju!", tax="Porezni broj", vatid="PDV broj", page="Stranica",
               subject="Vaš račun {n} – {c}",
               mail="Pozdrav {name},\n\nu privitku je vaš račun {n} na iznos od {amount}.\nMolimo uplatite iznos do {due}.\n\nRačun uvijek možete pronaći i u portalu za klijente:\n{portal}\n\nHvala i lijep pozdrav,\n{c}"),
}
PURPLE, INK, MUTED, LINE = (91, 33, 182), (43, 39, 80), (107, 104, 144), (221, 214, 254)


def money(v, lang):
    q = Decimal(v).quantize(Decimal("0.01"), ROUND_HALF_UP)
    s = f"{q:,.2f}"
    if lang == "en":
        return f"€{s}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def fdate(d, lang):
    return d.strftime("%d/%m/%Y" if lang == "en" else "%d.%m.%Y") if d else ""


def dec(s, default="0"):
    try:
        return Decimal(str(s or default).replace(" ", "").replace("€", "").replace(",", "."))
    except InvalidOperation:
        return Decimal(default)


def totals(items, vat_rate, small_business):
    net = sum((dec(i["qty"], "1") * dec(i["price"])).quantize(Decimal("0.01"), ROUND_HALF_UP) for i in items)
    vat = Decimal(0) if small_business else (net * dec(vat_rate) / 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
    return net, vat, net + vat


def render_pdf(inv, client):
    """Build the invoice PDF from the stored data."""
    c = get_content("en")
    d = json.loads(inv.data or "{}")
    lang = d.get("lang") if d.get("lang") in L else "de"
    t = L[lang]
    items = d.get("items", [])
    small = bool(d.get("small_business"))
    net, vat, gross = totals(items, d.get("vat_rate", "19"), small)
    issued = date.fromisoformat(d["date"]) if d.get("date") else inv.issued_at.date()
    due = date.fromisoformat(d["due"]) if d.get("due") else issued + timedelta(days=14)
    seller = c.legal_company or c.company_name
    seller_lines = [x for x in (c.legal_name if c.legal_company else "", c.legal_street, c.legal_city, c.legal_country) if x]
    pdf = PDF(title=f"{t['invoice']} {inv.number}", author=seller)
    W, X0, X1 = 595.28, 56, 539

    def footer():
        y = 46
        pdf.line(X0, y + 22, X1, y + 22, 0.5, LINE)
        cols = [
            [seller] + seller_lines,
            [x for x in (c.legal_email or c.contact_email, c.legal_phone, c.contact_email and "amxme.info") if x][:3],
            [x for x in (f"{t['tax']}: {d.get('tax_number')}" if d.get("tax_number") else "",
                         f"{t['vatid']}: {c.legal_vat}" if c.legal_vat else "") if x],
            [x for x in (d.get("bank"), f"IBAN {d.get('iban')}" if d.get("iban") else "", f"BIC {d.get('bic')}" if d.get("bic") else "") if x],
        ]
        for i, col in enumerate(cols):
            for j, line in enumerate(col[:4]):
                pdf.text(X0 + (0, 118, 228, 350)[i], y + 8 - j * 9, line, 6.8, color=MUTED)

    # ---- header
    pdf.rect(0, 822, W, 20, PURPLE)
    pdf.text(X0, 778, (c.brand_name or "AMXME"), 22, "B", PURPLE)
    pdf.text(X0, 764, (c.brand_sub or "Web Solutions").upper(), 7.5, color=MUTED)
    for i, line in enumerate([seller] + seller_lines + [c.legal_email or c.contact_email]):
        pdf.text(X1, 782 - i * 11, line, 8.5, "B" if i == 0 else "R", INK if i == 0 else MUTED, "right")
    # ---- recipient
    pdf.text(X0, 706, " · ".join([seller] + [x for x in (c.legal_street, c.legal_city) if x]), 6.8, color=MUTED)
    pdf.line(X0, 702, X0 + 230, 702, 0.4, LINE)
    rec = [x for x in (client.company, client.name, client.street, client.city, client.country) if x]
    for i, line in enumerate(rec):
        pdf.text(X0, 686 - i * 13, line, 10, "B" if i == 0 else "R")
    # ---- meta box
    meta = [(t["number"], inv.number), (t["date"], fdate(issued, lang)), (t["customer"], f"K-{client.id:04d}")]
    if d.get("period"):
        meta.append((t["period"], d["period"]))
    meta.append((t["due"], fdate(due, lang)))
    pdf.rect(318, 700 - len(meta) * 15, X1 - 318, len(meta) * 15 + 12, (245, 243, 255))
    for i, (k, v) in enumerate(meta):
        y = 696 - i * 15
        pdf.text(328, y, k, 8.5, color=MUTED)
        pdf.text(X1 - 10, y, v, 9, "B", align="right")
    # ---- title
    y = 580
    pdf.text(X0, y, f"{t['invoice']} {inv.number}", 20, "B", INK)
    if d.get("intro"):
        for line in pdf.wrap(d["intro"], X1 - X0, 9.5):
            y -= 14
            pdf.text(X0, y, line, 9.5)
    # ---- items table
    y -= 30
    cols = (X0 + 8, X0 + 40, 400, 470, X1 - 8)

    def head(yy):
        pdf.rect(X0, yy - 7, X1 - X0, 22, PURPLE)
        pdf.text(cols[0], yy, t["pos"], 8.5, "B", (255, 255, 255))
        pdf.text(cols[1], yy, t["desc"], 8.5, "B", (255, 255, 255))
        pdf.text(cols[2], yy, t["qty"], 8.5, "B", (255, 255, 255), "right")
        pdf.text(cols[3], yy, t["unit"], 8.5, "B", (255, 255, 255), "right")
        pdf.text(cols[4], yy, t["total"], 8.5, "B", (255, 255, 255), "right")
    head(y)
    y -= 24
    for n, it in enumerate(items, 1):
        lines = pdf.wrap(it.get("desc", ""), cols[2] - cols[1] - 50, 9.5)
        need = 14 * len(lines) + 10
        if y - need < 170:
            footer()
            pdf.text(X1, 30, f"{t['page']} {len(pdf.pages)}", 7, color=MUTED, align="right")
            pdf.new_page()
            y = 780
            head(y)
            y -= 24
        q, p = dec(it.get("qty"), "1"), dec(it.get("price"))
        qty = (f"{q:f}".rstrip("0").rstrip(".") if "." in f"{q:f}" else f"{q:f}")
        if lang != "en":
            qty = qty.replace(".", ",")
        pdf.text(cols[0], y, str(n), 9.5, color=MUTED)
        for j, line in enumerate(lines):
            pdf.text(cols[1], y - j * 13, line, 9.5, "B" if j == 0 else "R")
        pdf.text(cols[2], y, qty + (f" {it['unit']}" if it.get("unit") else ""), 9.5, align="right")
        pdf.text(cols[3], y, money(p, lang), 9.5, align="right")
        pdf.text(cols[4], y, money(q * p, lang), 9.5, "B", align="right")
        y -= 13 * len(lines) + 9
        pdf.line(X0, y + 11, X1, y + 11, 0.4, LINE)
    # ---- totals
    y -= 12
    rows = [(t["net"], money(net, lang))]
    if not small:
        rows.append((t["vat"].format(r=str(d.get("vat_rate", "19")).replace(".", "," if lang != "en" else ".")), money(vat, lang)))
    for k, v in rows:
        pdf.text(350, y, k, 9.5, color=MUTED)
        pdf.text(cols[4], y, v, 9.5, align="right")
        y -= 16
    y -= 6
    pdf.rect(340, y - 9, X1 - 340, 24, (237, 233, 254))
    pdf.text(350, y, t["gross"], 11, "B", PURPLE)
    pdf.text(cols[4], y, money(gross, lang), 11.5, "B", PURPLE, "right")
    y -= 34
    if small:
        pdf.text(X0, y, t["small"], 8.5, color=MUTED)
        y -= 20
    # ---- payment
    for line in pdf.wrap(t["pay"].format(due=fdate(due, lang)), X1 - X0, 9.5):
        pdf.text(X0, y, line, 9.5)
        y -= 13
    bank = [x for x in (d.get("account_holder") or seller,
                        f"IBAN: {d.get('iban')}" if d.get("iban") else "",
                        f"BIC: {d.get('bic')}" if d.get("bic") else "", d.get("bank")) if x]
    for line in bank:
        pdf.text(X0 + 10, y, line, 9.5, "B" if line.startswith("IBAN") else "R")
        y -= 13
    if d.get("notes"):
        y -= 6
        for line in pdf.wrap(d["notes"], X1 - X0, 9):
            pdf.text(X0, y, line, 9, color=MUTED)
            y -= 12
    y -= 10
    pdf.text(X0, y, t["thanks"], 10, "B", PURPLE)
    footer()
    if len(pdf.pages) > 1:
        pdf.text(X1, 30, f"{t['page']} {len(pdf.pages)}", 7, color=MUTED, align="right")
    return pdf.output(), gross


def _save_pdf(inv, client):
    data, gross = render_pdf(inv, client)
    if inv.file:
        try:
            os.remove(os.path.join(current_app.config["PRIVATE_DIR"], os.path.basename(inv.file)))
        except OSError:
            pass
    name = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join(current_app.config["PRIVATE_DIR"], name)
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o600)
    inv.file = name
    d = json.loads(inv.data or "{}")
    inv.amount = money(gross, d.get("lang", "de"))
    return data


def next_number(prefix):
    year = date.today().year
    base = f"{prefix}{year}-"
    nums = [int(m.group(1)) for (n,) in db.session.query(Invoice.number).filter(Invoice.number.like(f"{base}%"))
            for m in [re.match(re.escape(base) + r"(\d+)$", n or "")] if m]
    return f"{base}{(max(nums) + 1) if nums else 1:03d}"


def _form_data(client):
    c = get_content("en")
    f = request.form
    items = []
    for desc, qty, unit, price in zip(f.getlist("desc"), f.getlist("qty"), f.getlist("unit"), f.getlist("price")):
        if desc.strip() or price.strip():
            items.append({"desc": desc.strip()[:500], "qty": (qty or "1").strip()[:12], "unit": unit.strip()[:20],
                          "price": str(dec(price))})
    return {
        "lang": f.get("lang") if f.get("lang") in L else (client.lang if client.lang in L else "de"),
        "date": f.get("date") or date.today().isoformat(),
        "due": f.get("due") or (date.today() + timedelta(days=int(c.inv_payment_days or 14))).isoformat(),
        "period": (f.get("period") or "").strip()[:80],
        "intro": (f.get("intro") or "").strip()[:600],
        "notes": (f.get("notes") or "").strip()[:1000],
        "items": items,
        "vat_rate": str(dec(f.get("vat_rate") or c.inv_vat_rate or "19")),
        "small_business": bool(f.get("small_business")),
        "tax_number": c.inv_tax_number, "iban": c.inv_iban, "bic": c.inv_bic, "bank": c.inv_bank,
        "account_holder": c.inv_account_holder,
    }


def _send(inv, client, data):
    c = get_content("en")
    d = json.loads(inv.data or "{}")
    lang = d.get("lang", "de")
    t = L[lang]
    due = date.fromisoformat(d["due"]) if d.get("due") else inv.issued_at.date()
    company = c.legal_company or c.company_name
    portal = current_app.config["SITE_URL"] + url_for("portal.home")
    body = t["mail"].format(name=client.name, n=inv.number, amount=inv.amount, due=fdate(due, lang), portal=portal, c=company)
    return send_mail(client.email, t["subject"].format(n=inv.number, c=company), body,
                     reply_to=c.contact_email or None, from_name=company,
                     attachments=[(f"{inv.number}.pdf".replace("/", "-"), data, "application/pdf")])


@bp.route("/clients/<int:client_id>/invoices/new", methods=["GET", "POST"])
@bp.route("/invoices/<int:inv_id>/edit", methods=["GET", "POST"])
@owner_required
def invoice_edit(client_id=None, inv_id=None):
    c = get_content("en")
    inv = db.session.get(Invoice, inv_id) if inv_id else None
    if inv_id and (not inv or inv.kind != "generated"):
        abort(404)
    client = db.session.get(Client, inv.client_id if inv else client_id) or abort(404)
    if request.method == "POST":
        data = _form_data(client)
        if not data["items"]:
            flash("Add at least one line item.", "error")
        else:
            is_new = inv is None
            if is_new:
                inv = Invoice(client_id=client.id, kind="generated")
                db.session.add(inv)
            number = (request.form.get("number") or "").strip()[:60] or next_number(c.inv_prefix or "RE-")
            clash = db.session.query(Invoice).filter(Invoice.number == number, Invoice.id != (inv.id or 0)).first()
            if clash:
                flash(f"Invoice number {number} already exists.", "error")
                db.session.rollback()
                return redirect(request.url)
            inv.number, inv.data = number, json.dumps(data, ensure_ascii=False)
            inv.title = (data["items"][0]["desc"].split("\n")[0])[:200]
            inv.issued_at = datetime.fromisoformat(data["date"])
            db.session.flush()
            pdf_bytes = _save_pdf(inv, client)
            action = request.form.get("action")
            if action == "send":
                ok, err = _send(inv, client, pdf_bytes)
                if ok:
                    inv.sent_at = utcnow()
                    flash(f"Invoice {inv.number} saved and emailed to {client.email}. It is also in the client portal.", "success")
                else:
                    flash(f"Invoice saved, but the email failed: {err}", "error")
            else:
                flash(f"Invoice {inv.number} saved{' – it is visible in the client portal' if True else ''}.", "success")
            log(f"{'Created' if is_new else 'Edited'} invoice {inv.number} for {client.name}" + (" and sent it" if inv.sent_at and action == "send" else ""))
            db.session.commit()
            return redirect(url_for("admin.invoice_edit", inv_id=inv.id))
    d = json.loads(inv.data) if inv and inv.data else {
        "lang": client.lang if client.lang in L else "de", "date": date.today().isoformat(),
        "due": (date.today() + timedelta(days=int(c.inv_payment_days or 14))).isoformat(),
        "items": [{"desc": "", "qty": "1", "unit": "", "price": ""}],
        "vat_rate": c.inv_vat_rate or "19", "small_business": c.inv_small_business == "1",
    }
    net = vat = gross = None
    if d.get("items"):
        net, vat, gross = totals(d["items"], d.get("vat_rate", "19"), d.get("small_business"))
    return render_template("admin/invoice_form.html", inv=inv, client=client, d=d,
                           suggested=inv.number if inv else next_number(c.inv_prefix or "RE-"),
                           net=net, vat=vat, gross=gross, money=money, settings_ok=bool(c.inv_iban and (c.inv_tax_number or c.legal_vat)))


@bp.route("/invoices/<int:inv_id>/pdf")
@owner_required
def invoice_pdf(inv_id):
    inv = db.session.get(Invoice, inv_id) or abort(404)
    path = os.path.join(current_app.config["PRIVATE_DIR"], os.path.basename(inv.file or ""))
    if not inv.file or not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="application/pdf", download_name=f"{inv.number or 'invoice'}.pdf")


@bp.post("/invoices/<int:inv_id>/send")
@owner_required
def invoice_send(inv_id):
    inv = db.session.get(Invoice, inv_id) or abort(404)
    client = db.session.get(Client, inv.client_id) or abort(404)
    with open(os.path.join(current_app.config["PRIVATE_DIR"], os.path.basename(inv.file)), "rb") as f:
        data = f.read()
    ok, err = _send(inv, client, data) if inv.kind == "generated" else send_mail(
        client.email, f"Invoice {inv.number}", f"Hello {client.name},\n\nplease find attached invoice {inv.number}.\n",
        attachments=[(f"{inv.number or 'invoice'}.pdf", data, "application/pdf")])
    if ok:
        inv.sent_at = utcnow()
        log(f"Emailed invoice {inv.number} to {client.email}")
    db.session.commit()
    flash(f"Invoice {inv.number} sent to {client.email}." if ok else f"Email failed: {err}", "success" if ok else "error")
    return redirect(request.referrer or url_for("admin.invoices"))


@bp.route("/invoices")
@owner_required
def invoices():
    status = request.args.get("status", "all")
    q = db.session.query(Invoice)
    if status in ("open", "paid"):
        q = q.filter(Invoice.status == status)
    items = q.order_by(Invoice.issued_at.desc()).limit(500).all()
    names = {c.id: c.name for c in db.session.query(Client)}
    open_sum = sum((dec(json.loads(i.data or "{}") and totals(json.loads(i.data)["items"], json.loads(i.data).get("vat_rate", "19"),
                                                             json.loads(i.data).get("small_business"))[2])
                    for i in items if i.status == "open" and i.kind == "generated"), Decimal(0))
    return render_template("admin/invoices.html", items=items, names=names, status=status, open_sum=money(open_sum, "de"))
