# Signed: ASDHEM | AMXME Web Solutions
# ASDHEM | migration v4: client portal extras (profile, 2FA, services, announcements, attachments) + invoice generator
from sqlalchemy import text
from wsgi import app
from app.extensions import db
from app.models import Activity

COLUMNS = {
    "client": [("phone", "VARCHAR(60) DEFAULT ''"), ("street", "VARCHAR(160) DEFAULT ''"), ("city", "VARCHAR(120) DEFAULT ''"),
               ("country", "VARCHAR(80) DEFAULT ''"), ("vat_id", "VARCHAR(40) DEFAULT ''"), ("notify", "BOOLEAN DEFAULT 1"),
               ("totp_secret", "VARCHAR(64) DEFAULT ''"), ("totp_enabled", "BOOLEAN DEFAULT 0"), ("totp_last", "INTEGER DEFAULT 0")],
    "ticket": [("category", "VARCHAR(20) DEFAULT 'question'"), ("priority", "VARCHAR(10) DEFAULT 'normal'")],
    "invoice": [("kind", "VARCHAR(12) DEFAULT 'upload'"), ("data", "TEXT DEFAULT ''"), ("sent_at", "DATETIME")],
}

with app.app_context():
    db.create_all()
    con = db.session.connection()
    for table, cols in COLUMNS.items():
        have = [r[1] for r in con.execute(text(f"PRAGMA table_info({table})"))]
        for name, ddl in cols:
            if name not in have:
                con.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
                print("added", table, name)
    db.session.add(Activity(user="system", action="Client portal extras + invoice generator installed", kind="change"))
    db.session.commit()
    print("done")
