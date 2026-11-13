# Signed: ASDHEM | AMXME Web Solutions
"""Public website: homepage (EN / DE / HR), legal pages, contact form, preview links, sitemap."""
import hashlib
import ipaddress
import json
import random
import re
import secrets
import time
from datetime import timedelta

from flask import (Blueprint, Response, abort, current_app, flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from itsdangerous import BadSignature, URLSafeSerializer

from .extensions import db
from .i18n import DEFAULT_LANG, LANGS, UI, best_browser_lang, current_lang, t
from .mailer import send_mail
from .models import Activity, Faq, Feature, Message, Monitor, Post, Project, Service, Setting, SiteCheck, Testimonial, Visit, utcnow
from .templating import get_content, localize

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


MESSAGE_IP_DAYS = 7              # ASDHEM | GDPR: sender IP of contact messages kept only for spam/rate-limit checks
ACTIVITY_RETENTION_DAYS = 365    # admin activity / login log


def anonymize_ip(ip):
    """ASDHEM | GDPR: drop the host part – IPv4 keeps /24 (1.2.3.0), IPv6 keeps /48."""
    try:
        addr = ipaddress.ip_address((ip or "").strip())
    except ValueError:
        return ""
    if addr.version == 6 and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{addr}/{prefix}", strict=False).network_address)


def privacy_cleanup():
    """ASDHEM | GDPR storage limitation: delete / minimise personal data that is no longer needed."""
    now = utcnow()
    db.session.query(Visit).filter(Visit.created_at < now - timedelta(days=VISIT_RETENTION_DAYS)).delete()
    over = db.session.query(Visit).count() - VISIT_MAX_ROWS
    if over > 0:
        oldest = db.session.query(Visit.id).order_by(Visit.id).limit(over).subquery()
        db.session.query(Visit).filter(Visit.id.in_(db.select(oldest.c.id))).delete(synchronize_session=False)
    db.session.query(Message).filter(
        Message.ip != "", Message.created_at < now - timedelta(days=MESSAGE_IP_DAYS)
    ).update({Message.ip: ""}, synchronize_session=False)
    try:
        months = int((get_content().message_retention_months or "12").strip())
    except ValueError:
        months = 12
    if months > 0:
        db.session.query(Message).filter(
            Message.created_at < now - timedelta(days=months * 31)).delete(synchronize_session=False)
    db.session.query(Activity).filter(
        Activity.created_at < now - timedelta(days=ACTIVITY_RETENTION_DAYS)).delete(synchronize_session=False)
    db.session.query(SiteCheck).filter(SiteCheck.created_at < now - timedelta(days=1)).delete(synchronize_session=False)
    from .history import prune
    prune()


def record_visit():
    """Log a page view (skipped for the logged-in admin). Never breaks the page."""
    if session.get("admin_id"):
        return
    try:
        ua = (request.headers.get("User-Agent") or "")[:300]
        db.session.add(Visit(
            ip=anonymize_ip(request.remote_addr)[:64],  # ASDHEM | GDPR: never store the full IP
            path=request.full_path.rstrip("?")[:200],
            user_agent=ua,
            referrer=(request.referrer or "")[:300],
            is_bot=not ua or bool(BOT_RE.search(ua)),
        ))
        if random.random() < 0.02:  # occasional cleanup of old data
            privacy_cleanup()
        db.session.commit()
    except Exception:  # noqa: BLE001
        db.session.rollback()

bp = Blueprint("public", __name__)
LANG_RULE = "<any(de, hr):lang>"


@bp.url_value_preprocessor
def _pull_lang(endpoint, values):
    """ASDHEM | /de/... and /hr/... set the page language; everything else is English."""
    g.lang = (values or {}).pop("lang", DEFAULT_LANG) if values else DEFAULT_LANG
    if g.lang not in LANGS:
        g.lang = DEFAULT_LANG


@bp.url_defaults
def _push_lang(endpoint, values):
    if "lang" not in values and current_app.url_map.is_endpoint_expecting(endpoint, "lang"):
        values["lang"] = current_lang()

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


def structured_data(faqs=None, services=None):
    """ASDHEM | schema.org JSON-LD (Organization + WebSite, + FAQPage on the FAQ page) for Google / AI search."""
    c = get_content()
    site = current_app.config["SITE_URL"]
    lang = current_lang()
    page_url = site + url_for("public.faq")
    org = {
        "@type": "Organization", "@id": f"{site}/#organization",
        "name": c.company_name or "AMXME Web Solutions", "url": f"{site}/",
        "logo": f"{site}/static/img/favicon.svg",
        "description": c.meta_description,
    }
    if c.contact_email:
        org["email"] = c.contact_email
        org["contactPoint"] = {"@type": "ContactPoint", "contactType": "customer support",
                               "email": c.contact_email, "availableLanguage": ["English", "German", "Croatian"]}
    if services is None:
        services = localize(enabled(Service))
    if services:
        org["makesOffer"] = [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s.title,
                                                                 "description": s.description}} for s in services]
    graph = [org, {"@type": "WebSite", "@id": f"{site}/#website", "url": f"{site}/",
                   "name": c.company_name or "AMXME Web Solutions", "publisher": {"@id": f"{site}/#organization"},
                   "inLanguage": ["en", "de", "hr"],
                   "creator": {"@type": "Organization", "name": "ASDHEM"}}]  # ASDHEM | signature, visible in schema validators
    if faqs:
        graph.append({"@type": "FAQPage", "@id": f"{page_url}#faq", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": f.title,
             "acceptedAnswer": {"@type": "Answer", "text": f.text}} for f in faqs]})
    return {"@context": "https://schema.org", "@graph": graph}


@bp.route("/", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/")
def index():
    lang = current_lang()
    # ASDHEM | language: ?hl=xx remembers a choice; first visit to "/" follows the browser language
    hl = request.args.get("hl")
    if hl in LANGS:
        session["lang"] = hl
        return redirect(url_for("public.index", lang=hl))
    if lang == DEFAULT_LANG and "lang" not in session and not BOT_RE.search(request.headers.get("User-Agent") or ""):
        best = best_browser_lang()
        if best and best != DEFAULT_LANG:
            session["lang"] = best
            resp = redirect(url_for("public.index", lang=best))
            resp.headers["Vary"] = "Accept-Language"
            return resp
    if session.get("lang") != lang:
        session["lang"] = lang
    record_visit()
    c = get_content()
    preview_left = 0
    if c.maintenance_enabled == "1" and not session.get("admin_id"):
        preview_left = preview_seconds_left()
        if not preview_left:
            return render_template("maintenance.html", ld=structured_data(), canonical_path=url_for("public.index"))
    ctx = home_context()
    ctx["preview_left"] = preview_left
    return render_template("index.html", **ctx)


def faq_data():
    """ASDHEM | enabled FAQs (localized) + their categories with counts."""
    lang = current_lang()
    faqs = localize(enabled(Faq))
    faq_cats = {}
    for f in faqs:
        f.cat = (f.category or "").strip() or ("General" if lang == "en" else {"de": "Allgemein", "hr": "Općenito"}[lang])
        faq_cats[f.cat] = faq_cats.get(f.cat, 0) + 1
    return faqs, list(faq_cats.items())


def home_context():
    """Everything the homepage template needs (also used by the admin live preview)."""
    services = localize(enabled(Service))
    projects = localize(enabled(Project))
    has_faq = db.session.execute(db.select(Faq.id).filter_by(enabled=True).limit(1)).first() is not None
    return dict(
        services=services,
        why=localize(enabled(Feature, group="why")),
        hosting=localize(enabled(Feature, group="hosting")),
        badges=localize(enabled(Feature, group="badge")),
        testimonials=localize(enabled(Testimonial)),
        posts=localize(latest_posts(3)),
        projects=projects,
        categories=sorted({p.category for p in projects if p.category}),
        preview_left=0,
        has_faq=has_faq,
        ld=structured_data(None, services),
        canonical_path=url_for("public.index"),
    )


def latest_posts(limit=None):
    q = db.select(Post).filter_by(enabled=True).order_by(Post.created_at.desc())
    if limit:
        q = q.limit(limit)
    return db.session.execute(q).scalars().all()


def _site_open():
    """False while 'under construction' is on (unless admin / preview link)."""
    c = get_content()
    return c.maintenance_enabled != "1" or session.get("admin_id") or preview_seconds_left()


# ====================================================================== ASDHEM | service pages
@bp.route("/services/<slug>", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/services/<slug>")
def service_page(slug):
    if not _site_open():
        return redirect(url_for("public.index"))
    s = db.session.execute(db.select(Service).filter_by(slug=slug, enabled=True)).scalar()
    if not s or not s.tr("body", current_lang()).strip():
        abort(404)
    record_visit()
    others = [x for x in localize(enabled(Service)) if x.id != s.id]
    return render_template("service.html", s=localize([s])[0], others=others,
                           canonical_path=url_for("public.service_page", slug=slug))


# ====================================================================== ASDHEM | blog
@bp.route("/blog", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/blog")
def blog():
    if not _site_open():
        return redirect(url_for("public.index"))
    record_visit()
    return render_template("blog.html", posts=localize(latest_posts()), canonical_path=url_for("public.blog"))


@bp.route("/blog/<slug>", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/blog/<slug>")
def blog_post(slug):
    if not _site_open():
        return redirect(url_for("public.index"))
    p = db.session.execute(db.select(Post).filter_by(slug=slug)).scalar()
    if not p or not (p.enabled or session.get("admin_id")):
        abort(404)
    record_visit()
    more = [x for x in localize(latest_posts(4)) if x.id != p.id][:3]
    site = current_app.config["SITE_URL"]
    lp = localize([p])[0]
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": lp.title,
          "description": lp.excerpt, "inLanguage": current_lang(),
          "datePublished": p.created_at.date().isoformat(), "dateModified": (p.updated_at or p.created_at).date().isoformat(),
          "author": {"@type": "Organization", "name": get_content().company_name},
          "publisher": {"@id": f"{site}/#organization"},
          "mainEntityOfPage": site + url_for("public.blog_post", slug=slug)}
    if p.image:
        ld["image"] = site + p.image
    return render_template("post.html", p=lp, more=more, ld=ld, canonical_path=url_for("public.blog_post", slug=slug))


# ====================================================================== ASDHEM | "How we work" page
@bp.route("/process", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/process")
def process():
    """Old address: "How we work" now lives at the top of the homepage."""
    return redirect(url_for("public.index", lang=current_lang()) + "#process", code=301)


# ====================================================================== ASDHEM | FAQ page
@bp.route("/faq", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/faq")
def faq():
    if not _site_open():
        return redirect(url_for("public.index"))
    faqs, faq_cats = faq_data()
    if not faqs:
        abort(404)
    record_visit()
    return render_template("faq.html", faqs=faqs, faq_cats=faq_cats, ld=structured_data(faqs),
                           canonical_path=url_for("public.faq"))


# ====================================================================== ASDHEM | public status page
@bp.route("/status", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/status")
def status():
    from .monitor import daily_bars, uptime
    items = db.session.query(Monitor).filter_by(public=True, enabled=True).order_by(Monitor.position, Monitor.id).all()
    for m in items:
        m.uptime30 = uptime(m.id, 30)
        m.bars = daily_bars(m.id, 30)
    all_ok = all(m.status != "down" for m in items)
    resp = current_app.make_response(render_template("status.html", items=items, all_ok=all_ok,
                                                     canonical_path=url_for("public.status")))
    resp.headers["Cache-Control"] = "public, max-age=60"
    return resp


# ====================================================================== ASDHEM | free website check
CHECK_PER_HOUR = 6
CHECK_GLOBAL_PER_HOUR = 120


def _who():
    key = current_app.config["SECRET_KEY"]
    return hashlib.sha256(f"{key}|{anonymize_ip(request.remote_addr)}|{request.remote_addr}".encode()).hexdigest()


@bp.route("/check", defaults={"lang": DEFAULT_LANG}, methods=["GET", "POST"])
@bp.route(f"/{LANG_RULE}/check", methods=["GET", "POST"])
def website_check():
    from .checker import CheckError, run   # ASDHEM | available even in "under construction" mode
    result = error = None
    url = (request.values.get("url") or "").strip()[:300]
    if request.method == "POST" and url:
        hour = utcnow() - timedelta(hours=1)
        who = _who()
        mine = db.session.query(SiteCheck).filter(SiteCheck.who == who, SiteCheck.created_at > hour).count()
        total = db.session.query(SiteCheck).filter(SiteCheck.created_at > hour).count()
        if mine >= CHECK_PER_HOUR or total >= CHECK_GLOBAL_PER_HOUR:
            error = t("chk_err_rate")
        else:
            db.session.add(SiteCheck(who=who))
            db.session.commit()
            try:
                result = run(url)
            except CheckError as e:
                error = t(f"chk_err_{e}") if f"chk_err_{e}" in UI else t("chk_err_connect")
    else:
        record_visit()
    return render_template("check.html", url=url, result=result, error=error, canonical_path=url_for("public.website_check"))


@bp.route("/preview/<token>")
def preview(token):
    """Open a preview link: gives this browser access for as long as the link is active."""
    try:
        link_id = _preview_serializer().loads(token)
    except BadSignature:
        return render_template("error.html", code=404, message=t("e404")), 404
    if not any(l.get("i") == link_id for l in preview_links()):
        return render_template("error.html", code=410, message=t("e410")), 410
    session["preview_id"] = link_id
    session.pop("preview_until", None)
    resp = redirect(url_for("public.index"))
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


@bp.post("/contact")
def contact():
    f = request.form
    is_fetch = request.headers.get("X-Requested-With") == "fetch"
    g.lang = f.get("lang") if f.get("lang") in LANGS else DEFAULT_LANG  # ASDHEM | reply in the visitor's language
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
        errors["name"] = t("err_name")
    elif len(name) > 120:
        errors["name"] = t("err_name_long")
    if not EMAIL_RE.match(email) or len(email) > 200:
        errors["email"] = t("err_email")
    if not service:
        errors["service"] = t("err_service")
    if len(body) < 10:
        errors["message"] = t("err_message")
    elif len(body) > 5000:
        errors["message"] = t("err_message_long")
    if errors:
        return respond(False, errors, 422)

    ip = request.remote_addr or ""
    recent = db.session.query(Message).filter(
        Message.ip == ip, Message.created_at > utcnow() - timedelta(hours=1)
    ).count()
    hour_ago = utcnow() - timedelta(hours=1)
    total_recent = db.session.query(Message).filter(Message.created_at > hour_ago).count()
    if recent >= RATE_LIMIT_PER_HOUR or total_recent >= GLOBAL_LIMIT_PER_HOUR:
        return respond(False, {"_": t("err_rate")}, 429)

    msg = Message(name=name, email=email, service=service, body=body, ip=ip)
    db.session.add(msg)
    db.session.commit()

    to = c.notify_email or c.contact_email
    if to:
        ok, _ = send_mail(
            to,
            f"New inquiry: {service} – {name}",
            f"New message from the AMXME website contact form\n\n"
            f"Name:    {name}\nEmail:   {email}\nService: {service}\nLanguage: {LANGS[current_lang()]}\n\n{body}\n\n"
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


# ASDHEM | GDPR / German law: Imprint + Privacy Policy, always reachable (also in "under construction" mode)
@bp.route("/imprint", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/imprint")
def imprint():
    record_visit()
    return render_template("legal.html", page="imprint", canonical_path=url_for("public.imprint"))


@bp.route("/privacy", defaults={"lang": DEFAULT_LANG})
@bp.route(f"/{LANG_RULE}/privacy")
def privacy():
    record_visit()
    return render_template("legal.html", page="privacy", canonical_path=url_for("public.privacy"), visit_days=VISIT_RETENTION_DAYS,
                           message_ip_days=MESSAGE_IP_DAYS)


@bp.route("/impressum")
def impressum_alias():
    return redirect(url_for("public.imprint", lang="de"), 301)


@bp.route("/datenschutz")
def datenschutz_alias():
    return redirect(url_for("public.privacy", lang="de"), 301)


@bp.route("/robots.txt")
def robots():
    site = current_app.config["SITE_URL"]
    return Response(f"User-agent: *\nDisallow: /admin\nSitemap: {site}/sitemap.xml\n", mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    site = current_app.config["SITE_URL"]
    pages = [("public.index", {}), ("public.imprint", {}), ("public.privacy", {}), ("public.status", {}),
             ("public.website_check", {})]
    if latest_posts(1):
        pages.append(("public.blog", {}))
    if enabled(Faq):
        pages.append(("public.faq", {}))
    pages += [("public.blog_post", {"slug": p.slug}) for p in latest_posts()]
    pages += [("public.service_page", {"slug": x.slug}) for x in enabled(Service) if x.slug and (x.body or "").strip()]
    urls = []
    for ep, args in pages:
        alts = {code: site + url_for(ep, lang=code, **args) for code in LANGS}
        links = "".join(f'<xhtml:link rel="alternate" hreflang="{code}" href="{u}"/>' for code, u in alts.items())
        links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts[DEFAULT_LANG]}"/>'
        urls += [f"<url><loc>{u}</loc>{links}</url>" for u in alts.values()]
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
           + "".join(urls) + "</urlset>\n")
    return Response(xml, mimetype="application/xml")
