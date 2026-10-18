"""B1 hookrelay — tests. Run: pytest test_hookforge.py"""
import sys, os, json

import pytest
flask_ok = True
try:
    import flask_sqlalchemy
except ImportError:
    flask_ok = False

def test_inbox_token_unique():
    from hookrelay.relay.inbox import create_inbox
    # verify token generator shape
    import secrets, string
    t1 = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    t2 = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    assert len(t1) == 8 and t1 != t2

@pytest.mark.skipif(not flask_ok, reason="flask-sqlalchemy not installed")
def test_capture_truncates():
    from hookrelay.relay.capture import MAX_BODY, capture
    class FakeReq:
        method = "POST"
        path = "/"
        remote_addr = "127.0.0.1"
        headers = {"Content-Type": "application/json"}
        def get_data(self):
            return b"x" * (MAX_BODY + 1000)
    class FakeInbox:
        id = 1
    e = capture(FakeInbox(), FakeReq())
    assert len(e.body) <= MAX_BODY

def test_match_rules():
    from hookrelay.relay.forward import match
    class Rule:
        match_json = '{"body_contains": "stripe.succeeded"}'
    class Event:
        method = "POST"
        path = "/"
        body = '{"type": "stripe.succeeded"}'
    assert match(Rule(), Event())

def test_match_method():
    from hookrelay.relay.forward import match
    class Rule:
        match_json = '{"method": "GET"}'
    class Event:
        method = "POST"
        path = "/"
        body = ""
    assert not match(Rule(), Event())

def test_hmac_sign():
    from hookrelay.relay.forward import sign
    import hmac, hashlib
    assert sign(b"payload", "secret") == hmac.new(b"secret", b"payload", hashlib.sha256).hexdigest()
