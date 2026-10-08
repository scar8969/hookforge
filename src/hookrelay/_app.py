from .models import Event, Inbox, Rule, db
from .relay.api import bp
from .relay.forward import forward, match
from .relay.inbox import create_inbox

import ast, json, os
from . import paths

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)

# Templates live next to the project root, not under web/. Without an explicit
# template_folder Flask searches web/templates and every render raises
# TemplateNotFound (HTTP 500).
paths.ensure_runtime_dirs()

def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR),
                instance_path=str(paths.INSTANCE_DIR))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "hookrelay.db")
    app.secret_key = os.environ.get("SECRET_KEY", "hookrelay-dev")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    @app.context_processor
    def _inject_app_name():
        return {"app_name": "hookrelay"}

    def _pretty_headers(raw):
        """headers_json is written as JSON by capture() but accept a Python repr too."""
        text = (raw or "").strip()
        if not text:
            return {}
        try:
            v = json.loads(text)
        except (TypeError, ValueError):
            try:
                v = ast.literal_eval(text)
            except (TypeError, ValueError, SyntaxError):
                return {}
        if not isinstance(v, dict):
            return {}
        return {str(k): str(x) for k, x in sorted(v.items())}

    def _inbox_rows():
        rows = []
        for i in Inbox.query.order_by(Inbox.id.desc()).all():
            rows.append({"id": i.id, "token": i.token, "name": i.name or "(unnamed)",
                         "created_at": i.created_at,
                         "events": Event.query.filter_by(inbox_id=i.id).count(),
                         "rules": Rule.query.filter_by(inbox_id=i.id).count()})
        return rows

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "inboxes": Inbox.query.count(),
                        "events": Event.query.count(),
                        "rules": Rule.query.count()})

    @app.get("/")
    def index():
        inboxes = _inbox_rows()
        token = request.args.get("inbox") or ""
        q = request.args.get("q") or ""
        current = None
        if token:
            current = Inbox.query.filter_by(token=token).first()
        elif inboxes:
            current = Inbox.query.filter_by(id=inboxes[0]["id"]).first()

        query = Event.query
        if current is not None:
            query = query.filter_by(inbox_id=current.id)
        rows = []
        for e in query.order_by(Event.id.desc()).limit(50).all():
            if q and q not in (e.body or "") and q not in (e.path or ""):
                continue
            rows.append({"id": e.id, "method": e.method, "path": e.path, "status": e.status,
                         "ms": e.ms, "ip": e.ip, "at": e.at,
                         "headers": _pretty_headers(e.headers_json),
                         "body": (e.body or "")[:400],
                         "truncated": len(e.body or "") > 400})

        counts = {"inboxes": Inbox.query.count(),
                  "events": Event.query.count() if current is None
                  else Event.query.filter_by(inbox_id=current.id).count(),
                  "rules": Rule.query.count() if current is None
                  else Rule.query.filter_by(inbox_id=current.id).count()}
        return render_template("index.html", inboxes=inboxes, events=rows,
                               current=current, counts=counts, q=q)

    @app.get("/inboxes")
    def inboxes_page():
        return render_template("inboxes.html", inboxes=_inbox_rows(),
                               counts={"inboxes": Inbox.query.count(),
                                       "events": Event.query.count(),
                                       "rules": Rule.query.count()})

    @app.post("/inboxes/new")
    def new_inbox():
        inbox = create_inbox((request.form.get("name") or "").strip())
        flash("inbox %s created" % inbox.token, "success")
        return redirect(url_for("index", inbox=inbox.token))

    @app.post("/events/<int:eid>/delete")
    def delete_event(eid):
        event = Event.query.get_or_404(eid)
        token = (Inbox.query.filter_by(id=event.inbox_id).first() or Inbox()).token or ""
        db.session.delete(event)
        db.session.commit()
        flash("event #%d deleted" % eid, "success")
        return redirect(url_for("index", inbox=token))

    @app.post("/inboxes/<int:iid>/delete")
    def delete_inbox(iid):
        Inbox.query.get_or_404(iid)
        ids = [e.id for e in Event.query.filter_by(inbox_id=iid).all()]
        Event.query.filter_by(inbox_id=iid).delete()
        Rule.query.filter_by(inbox_id=iid).delete()
        Inbox.query.filter_by(id=iid).delete()
        db.session.commit()
        flash("inbox #%d deleted with %d event(s)" % (iid, len(ids)), "success")
        return redirect(url_for("inboxes_page"))

    return app

app = build_app()
