"""relay - webhook capture, matching, forwarding and the /h/<token> blueprint.

Contents
    inbox.py    create_inbox / get_inbox
    capture.py  capture(inbox, request) -> Event
    forward.py  match / sign / forward rule fan-out
    api.py      the relay blueprint mounted by web/app.py
    models.py   compatibility shim, see below

The SQLAlchemy handle and the Inbox/Event/Rule models are declared once, in the
PROJECT-ROOT models.py, because web/app.py, wsgi.py and cli.py need them too.
db therefore lives in that root module, and the correct import inside this
package is

    from models import db, Event

and NOT 'from . import db', which would look for a non-existent relay/db.py.
The handle is re-exported here only so 'from relay import db' keeps working.
"""

from ..models import Event, Inbox, Rule, db

__all__ = ["Event", "Inbox", "Rule", "db"]
