# Signed: ASDHEM | AMXME Web Solutions
from datetime import datetime, timezone

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


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


class Setting(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default="")
    items = db.Column(db.Text, default="")  # one per line
    icon = db.Column(db.String(40), default="code")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)

    @property
    def item_list(self):
        return [l.strip() for l in (self.items or "").splitlines() if l.strip()]


class Feature(db.Model):
    """Small icon + title + text blocks. group: why | hosting | badge"""
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    text = db.Column(db.Text, default="")
    icon = db.Column(db.String(40), default="check")
    position = db.Column(db.Integer, default=0)
    enabled = db.Column(db.Boolean, default=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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


class Faq(db.Model):
    """ASDHEM | FAQ section: question (title) + answer (text), grouped by category."""
    id = db.Column(db.Integer, primary_key=True)
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
