# Signed: ASDHEM | AMXME Web Solutions
#
#      █████╗ ███████╗██████╗ ██╗  ██╗███████╗███╗   ███╗
#     ██╔══██╗██╔════╝██╔══██╗██║  ██║██╔════╝████╗ ████║
#     ███████║███████╗██║  ██║███████║█████╗  ██╔████╔██║
#     ██╔══██║╚════██║██║  ██║██╔══██║██╔══╝  ██║╚██╔╝██║
#     ██║  ██║███████║██████╔╝██║  ██║███████╗██║ ╚═╝ ██║
#     ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝
#
#     Designed & built by ASDHEM  ·  AMXME Web Solutions
#
import os
from datetime import timedelta

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_wtf.csrf import CSRFError
from sqlalchemy import event
from werkzeug.middleware.proxy_fix import ProxyFix

from .extensions import db, csrf


def create_app():
    app = Flask(__name__)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.environ.get("DATA_DIR", os.path.join(base, "data"))
    upload_dir = os.environ.get("UPLOAD_DIR", os.path.join(data_dir, "uploads"))
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(os.environ.get("PRIVATE_DIR", os.path.join(data_dir, "private")), mode=0o700, exist_ok=True)

    secret = os.environ.get("SECRET_KEY") or ""
    if len(secret) < 32:
        if os.environ.get("FLASK_DEBUG") != "1":
            raise RuntimeError("SECRET_KEY must be set in .env (at least 32 characters)")
        secret = "dev-only-insecure-key"

    secure_cookie = os.environ.get("COOKIE_SECURE", "1") == "1"
    app.config.update(
        SECRET_KEY=secret,
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(data_dir, "amxme.db"),
        SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"timeout": 15}},
        UPLOAD_DIR=upload_dir,
        DATA_DIR=data_dir,
        PRIVATE_DIR=os.environ.get("PRIVATE_DIR", os.path.join(data_dir, "private")),   # ASDHEM | invoices, never public
        BACKUP_DIR=os.environ.get("BACKUP_DIR", os.path.join(base, "backups")),
        MAX_CONTENT_LENGTH=12 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=secure_cookie,
        # __Host- prefix: browser only accepts it over HTTPS, for this exact host, path=/ (no subdomain tricks)
        SESSION_COOKIE_NAME="__Host-amxme_session" if secure_cookie else "amxme_session",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        WTF_CSRF_TIME_LIMIT=None,
        SITE_URL=os.environ.get("SITE_URL", "https://amxme.info").rstrip("/"),
    )
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def _sqlite_pragmas(conn, _):
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()

    from . import templating
    templating.init_app(app)

    from . import history  # noqa: F401  ASDHEM | version-history hooks
    from .public import bp as public_bp
    from .admin import bp as admin_bp
    from .portal import bp as portal_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(portal_bp, url_prefix="/portal")

    from . import cli
    cli.init_app(app)

    @app.route("/uploads/<path:name>")
    def uploads(name):  # nginx serves this in production
        return send_from_directory(app.config["UPLOAD_DIR"], name, max_age=86400 * 30)

    from .i18n import lang_from_path, t

    def _err(code, key):
        from flask import g
        g.lang = getattr(g, "lang", None) or lang_from_path()
        return render_template("error.html", code=code, message=t(key)), code

    @app.errorhandler(CSRFError)
    def csrf_error(e):
        if request.headers.get("X-Requested-With") == "fetch":
            from flask import g
            g.lang = request.form.get("lang") or lang_from_path()
            return jsonify(ok=False, errors={"_": t("err_session")}), 400
        return _err(400, "e400")

    @app.errorhandler(404)
    def not_found(e):
        return _err(404, "e404")

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return _err(500, "e500")

    @app.errorhandler(405)
    def not_allowed(e):
        return _err(405, "e405")

    @app.errorhandler(413)
    def too_large(e):
        return render_template("error.html", code=413, message="The uploaded file is too large (max 12 MB)."), 413

    csp = "; ".join([
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "font-src 'self'",
        "img-src 'self' data: blob:",
        "connect-src 'self'",
        "form-action 'self'",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "upgrade-insecure-requests",
    ])

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
                                "accelerometer=(), gyroscope=(), magnetometer=(), browsing-topics=()")
        resp.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        resp.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")   # ASDHEM | other sites may not embed our responses
        resp.headers.setdefault("X-Permitted-Cross-Domain-Policies", "none")
        if request.is_secure:
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        if request.path.startswith("/admin"):
            resp.headers["Cache-Control"] = "no-store"
            resp.headers["X-Robots-Tag"] = "noindex, nofollow"
        return resp

    return app
