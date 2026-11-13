# Signed: ASDHEM | AMXME Web Solutions
"""ASDHEM | Version history: every change to texts and collection items is snapshotted
automatically (SQLAlchemy flush hooks) and can be restored with one click."""
import json
from datetime import date, datetime

from flask import g, has_request_context
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from .extensions import db
from .models import Faq, Feature, Post, Project, Revision, Service, Setting, Testimonial

TRACKED = {m.__tablename__: m for m in (Setting, Service, Feature, Faq, Project, Post, Testimonial)}
SKIP_SETTINGS = {"preview_links"}
KEEP = 3000


def _val(v):
    return v.isoformat() if isinstance(v, (datetime, date)) else v


def _row_key(obj):
    return obj.key if isinstance(obj, Setting) else str(obj.id)


def _label(obj):
    if isinstance(obj, Setting):
        from .content import FIELD_SECTION, SECTION_MAP
        base, _, lang = obj.key.partition("__")
        sec = SECTION_MAP.get(FIELD_SECTION.get(base, ""))
        field = next((f["label"] for f in (sec or {}).get("fields", []) if f["key"] == base), base)
        return f"{sec['title'] if sec else 'Setting'} › {field}" + (f" ({lang.upper()})" if lang else "")
    return f"{obj.__tablename__.title()} › {getattr(obj, 'title', '') or obj.id}"


def _tracked(obj):
    if obj.__tablename__ not in TRACKED:
        return False
    return not (isinstance(obj, Setting) and obj.key in SKIP_SETTINGS)


def _user():
    if has_request_context():
        u = getattr(g, "user", None)
        if u:
            return u.username
    return "system"


def _snapshot(obj, previous=False):
    state = inspect(obj)
    data = {}
    for attr in state.mapper.column_attrs:
        hist = state.attrs[attr.key].history
        if previous and hist.deleted:
            data[attr.key] = _val(hist.deleted[0])
        else:
            data[attr.key] = _val(getattr(obj, attr.key))
    return data


def _add(session, obj, action, data):
    session.add(Revision(user=_user(), table=obj.__tablename__, row_key=_row_key(obj), action=action,
                         label=_label(obj)[:200], data=json.dumps(data, ensure_ascii=False)))


@event.listens_for(Session, "before_flush")
def _before_flush(session, ctx, instances):
    if session.info.get("no_history"):
        return
    for obj in list(session.dirty):
        if _tracked(obj) and session.is_modified(obj, include_collections=False):
            _add(session, obj, "update", _snapshot(obj, previous=True))
    for obj in list(session.deleted):
        if _tracked(obj):
            _add(session, obj, "delete", _snapshot(obj))
    session.info["new_tracked"] = [o for o in session.new if _tracked(o)]


@event.listens_for(Session, "after_flush")
def _after_flush(session, ctx):
    new = session.info.pop("new_tracked", [])
    for obj in new:
        _add(session, obj, "create", {})


def restore(rev):
    """Bring a row back to the state stored in `rev`. The restore itself is recorded too (undo-able)."""
    model = TRACKED.get(rev.table)
    if not model:
        raise ValueError("Unknown table")
    pk = rev.row_key if model is Setting else int(rev.row_key)
    current = db.session.get(model, pk)
    if rev.action == "create":
        if current is not None:
            db.session.delete(current)
        return
    data = json.loads(rev.data or "{}")
    if current is None:
        current = model()
        db.session.add(current)
    for col in model.__table__.columns:
        if col.name in data:
            v = data[col.name]
            if isinstance(col.type, db.DateTime) and isinstance(v, str):
                v = datetime.fromisoformat(v)
            setattr(current, col.name, v)


def prune():
    over = db.session.query(Revision).count() - KEEP
    if over > 0:
        old = db.session.query(Revision.id).order_by(Revision.id).limit(over).subquery()
        db.session.query(Revision).filter(Revision.id.in_(db.select(old.c.id))).delete(synchronize_session=False)
