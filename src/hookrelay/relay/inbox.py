import secrets
import string

_ALPHABET = string.ascii_letters + string.digits


def create_inbox(name=""):
    from ..models import Inbox, db

    while True:
        token = "".join(secrets.choice(_ALPHABET) for _ in range(8))
        if not Inbox.query.filter_by(token=token).first():
            break
    inbox = Inbox(token=token, name=name)
    db.session.add(inbox)
    db.session.commit()
    return inbox


def get_inbox(token):
    from ..models import Inbox

    return Inbox.query.filter_by(token=token).first()
