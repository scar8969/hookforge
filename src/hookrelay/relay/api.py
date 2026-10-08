from ..models import Event, Inbox, Rule, db
from .capture import capture
from .forward import forward, match
from .inbox import create_inbox, get_inbox

from flask import Blueprint, jsonify, request, Response
import json, time

bp = Blueprint("relay", __name__)

@bp.route("/h/<token>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def hook(token):
    inbox = get_inbox(token)
    if not inbox:
        return jsonify({"error": "not_found"}), 404
    event = capture(inbox, request)
    db.session.add(event)
    db.session.commit()
    # fire rules
    for rule in Rule.query.filter_by(inbox_id=inbox.id, enabled=1).all():
        if match(rule, event):
            import threading
            threading.Thread(target=forward, args=(rule, event), daemon=True).start()
    return jsonify({"received": True, "event_id": event.id})

@bp.get("/api/inboxes")
def inboxes():
    return jsonify({"inboxes": [{"id": i.id, "name": i.name, "token": i.token,
                                 "events": Event.query.filter_by(inbox_id=i.id).count()}
                                for i in Inbox.query.all()]})

@bp.post("/api/inboxes")
def new_inbox():
    d = request.get_json(force=True, silent=True) or {}
    inbox = create_inbox(d.get("name", ""))
    return jsonify({"id": inbox.id, "token": inbox.token, "url": f"/h/{inbox.token}"})

@bp.get("/api/events")
def events():
    """Captured events; ?inbox=<token> narrows to one inbox, ?q= filters text.

    With no ?inbox the whole capture log is returned. An ?inbox= token that does
    not exist is a client error, so it answers 404 instead of an empty list.
    """
    token = request.args.get("inbox", "")
    inbox = get_inbox(token) if token else None
    if token and not inbox:
        return jsonify({"error": "inbox not found"}), 404
    q = request.args.get("q", "")
    query = Event.query
    if inbox is not None:
        query = query.filter_by(inbox_id=inbox.id)
    if q:
        query = query.filter(Event.body.contains(q) | Event.path.contains(q))
    rows = [{"id": e.id, "inbox_id": e.inbox_id, "method": e.method, "path": e.path,
             "status": e.status, "ms": e.ms, "at": e.at.isoformat() if e.at else ""}
            for e in query.order_by(Event.id.desc()).limit(50).all()]
    return jsonify({"events": rows, "inbox": inbox.token if inbox else None})

@bp.post("/api/events/<int:eid>/replay")
def replay(eid):
    e = Event.query.get_or_404(eid)
    inbox = Inbox.query.get(e.inbox_id)
    # re-send to inbox capture
    class _FakeReq:
        method = e.method
        path = e.path
        headers = {}
        data = e.body.encode()
    ne = capture(inbox, _FakeReq())
    db.session.add(ne)
    db.session.commit()
    return jsonify({"status": "replayed", "event_id": ne.id})

@bp.post("/api/rules")
def add_rule():
    d = request.get_json(force=True, silent=True) or {}
    r = Rule(inbox_id=d.get("inbox_id", 0), match_json=str(d.get("match", {})),
             forward_url=d.get("forward_url", ""), hmac_secret=d.get("hmac_secret", ""))
    db.session.add(r)
    db.session.commit()
    return jsonify({"id": r.id})
