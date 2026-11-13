# Signed: ASDHEM | AMXME Web Solutions
import secrets

import click
from werkzeug.security import generate_password_hash

from .content import SEED_FAQ, SEED_FEATURES, SEED_PROJECTS, SEED_SERVICES
from .extensions import db
from .models import AdminUser, Faq, Feature, Project, Service


def seed():
    if not db.session.query(Service.id).first():
        for i, (title, ic, desc, items) in enumerate(SEED_SERVICES):
            db.session.add(Service(title=title, icon=ic, description=desc, items=items, position=i))
    if not db.session.query(Feature.id).first():
        for group, rows in SEED_FEATURES.items():
            for i, (title, ic, text) in enumerate(rows):
                db.session.add(Feature(group=group, title=title, icon=ic, text=text, position=i))
    if not db.session.query(Project.id).first():
        for i, (title, desc, cat, tech, img) in enumerate(SEED_PROJECTS):
            db.session.add(Project(title=title, description=desc, category=cat, technologies=tech, image=img, position=i))
    if not db.session.query(Faq.id).first():
        for i, (cat, q, a) in enumerate(SEED_FAQ):
            db.session.add(Faq(category=cat, title=q, text=a, position=i))
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
