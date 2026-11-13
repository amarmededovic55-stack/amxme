# Signed: ASDHEM | AMXME Web Solutions
import os
from datetime import datetime

from flask import url_for, g
from markupsafe import Markup, escape

from .content import DEFAULTS, DEFAULTS_I18N, TRANSLATABLE
from .i18n import DEFAULT_LANG, LANG_ORDER, LANG_SHORT, LANGS, LOCALES, current_lang, js_strings, t
from .extensions import db
from .icons import icon
from .models import Setting


class Content(dict):
    def __getattr__(self, k):
        return self.get(k, "")


def _settings():
    if "settings_raw" not in g:
        g.settings_raw = {s.key: s.value or "" for s in db.session.execute(db.select(Setting)).scalars()}
    return g.settings_raw


def translated_value(key, lang, raw=None):
    """ASDHEM | value of one text in `lang`: typed translation > translated default > English."""
    raw = _settings() if raw is None else raw
    base = raw.get(key, DEFAULTS.get(key, ""))
    if lang == DEFAULT_LANG or key not in TRANSLATABLE:
        return base
    explicit = raw.get(f"{key}__{lang}", "")
    if explicit.strip():
        return explicit
    if base == DEFAULTS.get(key) and key in DEFAULTS_I18N.get(lang, {}):
        return DEFAULTS_I18N[lang][key]
    return base


def explicit_translation(key, lang):
    """What the admin form shows for a translation: typed value, or the built-in translated default."""
    raw = _settings()
    explicit = raw.get(f"{key}__{lang}", "")
    if explicit.strip():
        return explicit
    base = raw.get(key, DEFAULTS.get(key, ""))
    if base == DEFAULTS.get(key):
        return DEFAULTS_I18N.get(lang, {}).get(key, "")
    return ""


def get_content(lang=None):
    lang = lang or current_lang()
    cache = g.setdefault("content_cache", {})
    if lang not in cache:
        raw = _settings()
        cache[lang] = Content({k: translated_value(k, lang, raw) for k in DEFAULTS})
    return cache[lang]


class Tr:
    """ASDHEM | read-only view of a collection item in the current language."""

    def __init__(self, obj, lang):
        self._o, self._lang = obj, lang

    def __getattr__(self, name):
        o = self._o
        if name in getattr(o, "I18N_FIELDS", ()):
            return o.tr(name, self._lang)
        if name == "item_list":
            return [l.strip() for l in (o.tr("items", self._lang) or "").splitlines() if l.strip()]
        return getattr(o, name)


def localize(items, lang=None):
    lang = lang or current_lang()
    return [Tr(i, lang) for i in items]


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
    """Escape text and wrap the first occurrence of `word` (any letter case) in a gradient span."""
    text = text or ""
    word = (word or "").strip()
    i = text.lower().find(word.lower()) if word else -1
    if i >= 0:
        before, mid, after = text[:i], text[i:i + len(word)], text[i + len(word):]
        return Markup(f'{escape(before)}<span class="grad-text">{escape(mid)}</span>{escape(after)}')
    return escape(text)


def steps(text):
    """'Title | Text' lines -> [(title, text)]."""
    out = []
    for line in lines(text):
        title, _, body = line.partition("|")
        out.append((title.strip(), body.strip()))
    return out


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
    app.jinja_env.filters.update(lines=lines, paragraphs=paragraphs, highlight=highlight, safe_url=safe_url, steps=steps)
    app.jinja_env.globals.update(t=t, LANGS=LANGS, LOCALES=LOCALES, LANG_SHORT=LANG_SHORT, LANG_ORDER=LANG_ORDER)

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

    def lang_url(code):
        """Same page in another language (language switcher / hreflang)."""
        from flask import request
        ep = request.endpoint
        args = dict(request.view_args or {})
        if ep and app.url_map.is_endpoint_expecting(ep, "lang"):
            args["lang"] = code
            return url_for(ep, **args)
        return url_for("public.index", lang=code)

    @app.context_processor
    def inject():
        return {"c": get_content(), "year": datetime.now().year, "lang": current_lang(),
                "lang_url": lang_url, "i18n_js": js_strings}
