import argparse
import json
import sys


def _app():
    """Import the Flask app lazily so --help works before the web deps load."""
    from ._app import app

    return app


def cmd_inbox_create(args):
    from .relay.inbox import create_inbox

    app = _app()
    with app.app_context():
        inbox = create_inbox(args.name or "")
        print(inbox.token)
    return 0


def cmd_inboxes(args):
    from .models import Event, Inbox, Rule

    app = _app()
    with app.app_context():
        rows = [
            {
                "id": i.id,
                "name": i.name,
                "token": i.token,
                "events": Event.query.filter_by(inbox_id=i.id).count(),
                "rules": Rule.query.filter_by(inbox_id=i.id).count(),
            }
            for i in Inbox.query.order_by(Inbox.id.desc()).all()
        ]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(
                "#%-4s %-20s %-10s events=%-5s rules=%s"
                % (r["id"], r["name"] or "(unnamed)", r["token"], r["events"], r["rules"])
            )
    return 0


def cmd_events(args):
    from .models import Event, Inbox

    app = _app()
    with app.app_context():
        inbox = Inbox.query.filter_by(token=args.inbox).first()
        if inbox is None:
            print("no inbox with token %s" % args.inbox, file=sys.stderr)
            return 2
        q = Event.query.filter_by(inbox_id=inbox.id).order_by(Event.id.desc())
        if args.q:
            rows = [
                e
                for e in q.limit(200).all()
                if args.q in (e.body or "") or args.q in (e.path or "")
            ]
        else:
            rows = q.limit(args.limit).all()
        rows = rows[: args.limit]
        out = [
            {
                "id": e.id,
                "method": e.method,
                "path": e.path,
                "status": e.status,
                "ms": e.ms,
                "ip": e.ip,
                "at": e.at.isoformat() if e.at else "",
                "body": e.body,
            }
            for e in rows
        ]
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for e in out:
            print(
                "#%-4s %-6s %-30s %s %sms %s"
                % (e["id"], e["method"], e["path"], e["status"], e["ms"], e["at"])
            )
    return 0


def cmd_replay(args):
    from .models import Event, Rule
    from .relay.forward import forward, match

    app = _app()
    with app.app_context():
        event = Event.query.filter_by(id=args.event_id).first()
        if event is None:
            print("no event with id %d" % args.event_id, file=sys.stderr)
            return 2
        rules = Rule.query.filter_by(inbox_id=event.inbox_id, enabled=1).all()
        matched = [r for r in rules if match(r, event)]
        if not matched:
            print("no enabled rule matches event #%d" % event.id, file=sys.stderr)
            return 3
        ok = True
        for rule in matched:
            good, detail = forward(rule, event)
            ok = ok and good
            print(
                "rule #%d -> %s : %s (%s)"
                % (rule.id, rule.forward_url, "ok" if good else "failed", detail)
            )
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(prog="hookrelay", description="webhook relay + debugger")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("inbox-create", help="create an inbox and print its token")
    c.add_argument("--name", default="")
    l = sub.add_parser("inboxes", help="list inboxes")
    l.add_argument("--json", action="store_true")
    e = sub.add_parser("events", help="list captured events for one inbox")
    e.add_argument("inbox")
    e.add_argument("--limit", type=int, default=20)
    e.add_argument("--q", default="")
    e.add_argument("--json", action="store_true")
    r = sub.add_parser("replay", help="re-deliver an event to its matching rules")
    r.add_argument("event_id", type=int)
    args = p.parse_args()
    if args.cmd == "inbox-create":
        return cmd_inbox_create(args)
    if args.cmd == "inboxes":
        return cmd_inboxes(args)
    if args.cmd == "events":
        return cmd_events(args)
    if args.cmd == "replay":
        return cmd_replay(args)
    p.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
