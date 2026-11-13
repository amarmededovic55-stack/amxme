# Signed: ASDHEM | AMXME Web Solutions
import json
from datetime import datetime, timezone

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Translatable:
    """ASDHEM | per-language overrides stored as JSON: {"de": {"title": ...}, "hr": {...}}."""
    I18N_FIELDS = ()

    @property
    def translations(self):
        try:
            data = json.loads(self.i18n or "{}")
        except ValueError:
            data = {}
        return data if isinstance(data, dict) else {}

    def tr(self, field, lang):
        if lang and lang != "en":
            v = (self.translations.get(lang) or {}).get(field)
            if v and str(v).strip():
                return v
        return getattr(self, field) or ""

    def set_tr(self, lang, field, value):
        data = self.translations
        bucket = data.setdefault(lang, {})
        if value and value.strip():
            bucket[field] = value.strip()
        else:
            bucket.pop(field, None)
        if not bucket:
            data.pop(lang, None)
        self.i18n = json.dumps(data, ensure_ascii=False) if data else ""


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login = db.Column(db.DateTime)
    # two-factor authentication (TOTP)
    totp_secret = db.Column(db.String(64), default="")
    totp_enabled = db.Column(db.Boolean, default=False)
    totp_last = db.Column(db.Integer, default=0)       # last used time-step, blocks code reuse
    backup_codes = db.Column(db.Text, default="")       # hashed one-time recovery codes, one per line
    session_gen = db.Column(db.Integer, default=0, nullable=False, server_default="0")  # ASDHEM | +1 on logout = all sessions revoked
    role = db.Column(db.String(20), default="owner", nullable=False, server_default="owner")  # ASDHEM | owner | editor

    @property
    def is_owner(self):
        return self.role == "owner"


class Setting(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class Service(Translatable, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    I18N_FIELDS = ("title", "description", "items", "body")
    slug = db.Column(db.String(80), default="")      # ASDHEM | own page at /services/<slug> when body is filled
    body = db.Column(db.Text, default="")
    i18n = db.Column(db.Text, default="")  # ASDHEM | translations (JSON)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    items = db.Column(db.Text, default="")  # one per line
    icon = db.Column(db.String(40), default="code")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)

    @property
    def item_list(self):
        return [l.strip() for l in (self.items or "").splitlines() if l.strip()]


class Feature(Translatable, db.Model):
    """Small icon + title + text blocks. group: why | hosting | badge"""
    id = db.Column(db.Integer, primary_key=True)
    I18N_FIELDS = ("title", "text")
    i18n = db.Column(db.Text, default="")  # ASDHEM | translations (JSON)
    group = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    text = db.Column(db.Text, default="")
    icon = db.Column(db.String(40), default="check")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)


class Project(Translatable, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    I18N_FIELDS = ("title", "description", "category")
    i18n = db.Column(db.Text, default="")  # ASDHEM | translations (JSON)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(80), default="")
    technologies = db.Column(db.String(255), default="")  # comma separated
    url = db.Column(db.String(500), default="")
    image = db.Column(db.String(500), default="")  # URL path (/uploads/.. or /static/..)
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    @property
    def tech_list(self):
        return [t.strip() for t in (self.technologies or "").split(",") if t.strip()]


class Faq(Translatable, db.Model):
    """ASDHEM | FAQ section: question (title) + answer (text), grouped by category."""
    id = db.Column(db.Integer, primary_key=True)
    I18N_FIELDS = ("title", "text", "category")
    i18n = db.Column(db.Text, default="")  # ASDHEM | translations (JSON)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, default="")
    category = db.Column(db.String(60), default="General")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    service = db.Column(db.String(150), default="")
    body = db.Column(db.Text, nullable=False)
    ip = db.Column(db.String(64), default="")
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)
    emailed = db.Column(db.Boolean, default=False)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    user = db.Column(db.String(80), default="")
    action = db.Column(db.String(300), nullable=False)
    ip = db.Column(db.String(64), default="")
    kind = db.Column(db.String(20), default="change")  # change | auth | auth_fail


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), nullable=False, index=True)
    path = db.Column(db.String(200), default="")
    user_agent = db.Column(db.String(300), default="")
    referrer = db.Column(db.String(300), default="")
    is_bot = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)


# ====================================================================== ASDHEM | admin tools
class Revision(db.Model):
    """Snapshot of content BEFORE a change -> one-click restore (version history)."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    user = db.Column(db.String(80), default="")
    table = db.Column(db.String(40), nullable=False)
    row_key = db.Column(db.String(120), nullable=False, index=True)
    action = db.Column(db.String(10), nullable=False)   # update | create | delete
    label = db.Column(db.String(200), default="")
    data = db.Column(db.Text, default="")              # JSON of the previous row state


class MessageReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("message.id", ondelete="CASCADE"), index=True, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(80), default="")
    sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)


class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(300), nullable=False, unique=True)
    name = db.Column(db.String(200), default="")
    alt = db.Column(db.String(300), default="")
    width = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)
    size = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)


# ====================================================================== ASDHEM | blog & testimonials
class Post(Translatable, db.Model):
    I18N_FIELDS = ("title", "excerpt", "body")
    id = db.Column(db.Integer, primary_key=True)
    i18n = db.Column(db.Text, default="")
    slug = db.Column(db.String(120), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    excerpt = db.Column(db.Text, default="")
    body = db.Column(db.Text, default="")
    image = db.Column(db.String(500), default="")
    enabled = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class Testimonial(Translatable, db.Model):
    I18N_FIELDS = ("role", "text")
    id = db.Column(db.Integer, primary_key=True)
    i18n = db.Column(db.Text, default="")
    title = db.Column(db.String(120), nullable=False)        # person's name
    role = db.Column(db.String(160), default="")             # company / position
    text = db.Column(db.Text, default="")
    rating = db.Column(db.String(1), default="5")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=False)           # hidden until you have real reviews


# ====================================================================== ASDHEM | monitoring & client portal
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(160), default="")
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), default="")
    lang = db.Column(db.String(5), default="de")
    active = db.Column(db.Boolean, default=True)
    session_gen = db.Column(db.Integer, default=0, nullable=False, server_default="0")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login = db.Column(db.DateTime)
    # ASDHEM | profile & security (client portal)
    phone = db.Column(db.String(60), default="")
    street = db.Column(db.String(160), default="")
    city = db.Column(db.String(120), default="")
    country = db.Column(db.String(80), default="")
    vat_id = db.Column(db.String(40), default="")
    notify = db.Column(db.Boolean, default=True)              # email on ticket answers & announcements
    totp_secret = db.Column(db.String(64), default="")
    totp_enabled = db.Column(db.Boolean, default=False)
    totp_last = db.Column(db.Integer, default=0)


class Monitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id", ondelete="SET NULL"), index=True)
    public = db.Column(db.Boolean, default=False)            # shown on the public status page
    enabled = db.Column(db.Boolean, default=True)
    position = db.Column(db.Integer, default=0)
    status = db.Column(db.String(10), default="unknown")     # up | down | unknown
    last_code = db.Column(db.Integer, default=0)
    last_ms = db.Column(db.Integer, default=0)
    last_error = db.Column(db.String(200), default="")
    last_checked = db.Column(db.DateTime)
    ssl_expires = db.Column(db.DateTime)
    down_since = db.Column(db.DateTime)


class MonitorCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monitor_id = db.Column(db.Integer, db.ForeignKey("monitor.id", ondelete="CASCADE"), index=True, nullable=False)
    ok = db.Column(db.Boolean, default=True)
    ms = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), index=True, nullable=False)
    number = db.Column(db.String(60), default="")
    title = db.Column(db.String(200), default="")
    amount = db.Column(db.String(40), default="")
    status = db.Column(db.String(10), default="open")        # open | paid
    file = db.Column(db.String(120), default="")             # stored in DATA_DIR/private, never public
    issued_at = db.Column(db.DateTime, default=utcnow)
    kind = db.Column(db.String(12), default="upload")        # ASDHEM | upload | generated
    data = db.Column(db.Text, default="")                   # generated invoices: items, dates, VAT … (JSON)
    sent_at = db.Column(db.DateTime)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), index=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(12), default="open")        # open | answered | closed
    category = db.Column(db.String(20), default="question")  # question | change | problem | billing
    priority = db.Column(db.String(10), default="normal")    # normal | urgent
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, index=True)


class TicketMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id", ondelete="CASCADE"), index=True, nullable=False)
    author = db.Column(db.String(10), default="client")      # client | admin
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)


class SiteCheck(db.Model):
    """Free website check: only a salted hash of the shortened IP, for rate limiting (deleted after 1 day)."""
    id = db.Column(db.Integer, primary_key=True)
    who = db.Column(db.String(64), index=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)


class Contract(db.Model):
    """ASDHEM | a booked service of a client (hosting, maintenance, domain …) with renewal date."""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), index=True, nullable=False)
    kind = db.Column(db.String(20), default="hosting")       # hosting | maintenance | domain | design | other
    title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(200), default="")
    start_date = db.Column(db.Date)
    renewal_date = db.Column(db.Date)
    status = db.Column(db.String(12), default="active")      # active | ended
    note = db.Column(db.String(300), default="")


class Announcement(db.Model):
    """ASDHEM | news / maintenance notices shown in the client portal."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, default="")
    level = db.Column(db.String(12), default="info")         # info | maintenance | important
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)


class TicketFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("ticket_message.id", ondelete="CASCADE"), index=True, nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id", ondelete="CASCADE"), index=True, nullable=False)
    name = db.Column(db.String(160), default="")
    file = db.Column(db.String(80), nullable=False)          # stored in DATA_DIR/private
    size = db.Column(db.Integer, default=0)
