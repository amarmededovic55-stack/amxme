# Signed: ASDHEM | AMXME Web Solutions
import secrets

import click
from werkzeug.security import generate_password_hash

from .content import FAQ_CATEGORY_I18N, SEED_FAQ, SEED_FEATURES, SEED_PROJECTS, SEED_SERVICES
from .extensions import db
from .models import AdminUser, Faq, Feature, Project, Service


def seed():
    import json as _json

    def j(tr):
        return _json.dumps(tr, ensure_ascii=False) if tr else ""
    if not db.session.query(Service.id).first():
        for i, (title, ic, desc, items, tr) in enumerate(SEED_SERVICES):
            db.session.add(Service(title=title, icon=ic, description=desc, items=items, position=i, i18n=j(tr)))
    if not db.session.query(Feature.id).first():
        for group, rows in SEED_FEATURES.items():
            for i, (title, ic, text, tr) in enumerate(rows):
                db.session.add(Feature(group=group, title=title, icon=ic, text=text, position=i, i18n=j(tr)))
    if not db.session.query(Project.id).first():
        for i, (title, desc, cat, tech, img) in enumerate(SEED_PROJECTS):
            db.session.add(Project(title=title, description=desc, category=cat, technologies=tech, image=img, position=i))
    if not db.session.query(Faq.id).first():
        for i, (cat, q, a, tr) in enumerate(SEED_FAQ):
            tr_json = {lang: {"title": tq, "text": ta, "category": FAQ_CATEGORY_I18N[cat][lang]} for lang, (tq, ta) in tr.items()}
            db.session.add(Faq(category=cat, title=q, text=a, position=i, i18n=j(tr_json)))
    db.session.commit()


def init_app(app):
    @app.cli.command("init-db")
    def init_db():
        """Create tables and seed default content (safe to run repeatedly)."""
        db.create_all()
        seed()
        click.echo("Database ready.")

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.option("--password", default=None, help="Leave empty to generate one.")
    def create_admin(username, password):
        """Create an admin user, or reset the password of an existing one."""
        db.create_all()
        password = password or secrets.token_urlsafe(12)
        user = db.session.execute(db.select(AdminUser).filter_by(username=username)).scalar()
        if user:
            user.password_hash = generate_password_hash(password)
            action = "Password reset for"
        else:
            db.session.add(AdminUser(username=username, password_hash=generate_password_hash(password)))
            action = "Created admin"
        db.session.commit()
        click.echo(f"{action} '{username}'. Password: {password}")
