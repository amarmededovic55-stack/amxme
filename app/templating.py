# Signed: ASDHEM | AMXME Web Solutions
import os
from datetime import datetime

from flask import url_for, g
from markupsafe import Markup, escape

from .content import DEFAULTS
from .extensions import db
from .icons import icon
from .models import Setting


class Content(dict):
    def __getattr__(self, k):
        return self.get(k, "")


def get_content():
    if "content" not in g:
        data = dict(DEFAULTS)
        for s in db.session.execute(db.select(Setting)).scalars():
            if s.key in data:
                data[s.key] = s.value or ""
        g.content = Content(data)
    return g.content


def lines(text):
    return [l.strip() for l in (text or "").splitlines() if l.strip()]


def paragraphs(text):
    parts = [p.strip() for p in (text or "").replace("\r\n", "\n").split("\n\n")]
    return [p for p in parts if p]


SAFE_SCHEMES = ("http://", "https://", "mailto:", "tel:")


def safe_url(url, fallback="#"):
    """Allow only http(s)/mailto/tel or same-site links (blocks javascript:, data: ...)."""
    u = (url or "").strip()
    if not u:
        return fallback
    if u.startswith(("#", "/")) and not u.startswith(("//", "/\\")):
        return u
    if u.lower().startswith(SAFE_SCHEMES):
        return u
    return fallback


def highlight(text, word):
    """Escape text and wrap the first occurrence of `word` in a gradient span."""
    text = text or ""
    if word and word in text:
        before, _, after = text.partition(word)
        return Markup(f'{escape(before)}<span class="grad-text">{escape(word)}</span>{escape(after)}')
    return escape(text)


def ua_short(ua):
    """Very small user-agent summary, e.g. 'Chrome · Windows'."""
    if not ua:
        return "—"
    u = ua.lower()
    for key, name in (("bot", None), ("spider", None), ("crawl", None)):
        if key in u:
            return ua[:60]
    browser = next((n for k, n in (("edg/", "Edge"), ("opr/", "Opera"), ("samsungbrowser", "Samsung Internet"),
                                   ("firefox", "Firefox"), ("chrome", "Chrome"), ("safari", "Safari")) if k in u), None)
    os_ = next((n for k, n in (("iphone", "iPhone"), ("ipad", "iPad"), ("android", "Android"), ("windows", "Windows"),
                               ("mac os", "macOS"), ("cros", "ChromeOS"), ("linux", "Linux")) if k in u), None)
    parts = [p for p in (browser, os_) if p]
    return " · ".join(parts) if parts else ua[:60]


def init_app(app):
    app.jinja_env.filters["ua_short"] = ua_short
    app.jinja_env.globals.update(icon=icon)
    app.jinja_env.filters.update(lines=lines, paragraphs=paragraphs, highlight=highlight, safe_url=safe_url)

    @app.template_filter("dt")
    def fmt_dt(value, fmt="%d %b %Y, %H:%M"):
        return value.strftime(fmt) + " UTC" if value else ""

    # ASDHEM | cache busting: ?v=<file mtime> changes automatically whenever a static file is edited
    def asset(filename):
        path = os.path.join(app.static_folder, filename)
        try:
            v = int(os.path.getmtime(path))
        except OSError:
            v = 0
        return url_for("static", filename=filename) + f"?v={v}"

    app.jinja_env.globals["asset"] = asset

    @app.context_processor
    def inject():
        return {"c": get_content(), "year": datetime.now().year}
