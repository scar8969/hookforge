"""Compatibility shim: relay/models.py is NOT a second model module.

The real models (and the SQLAlchemy handle) live in the PROJECT-ROOT models.py,
one directory up, because web/app.py, wsgi.py and cli.py all import them from
there. This module exists only so that the sibling form

    from .models import Event        # inside relay/*.py

resolves instead of raising ModuleNotFoundError: No module named 'relay.models'.
New code in this package should import from the root module directly:

    from models import Event, db
"""
from ..models import Event, Inbox, Rule, db  # noqa: F401

__all__ = ["db", "Inbox", "Event", "Rule"]
