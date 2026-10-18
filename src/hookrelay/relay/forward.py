import hashlib
import hmac
import json
import urllib.request


def match(rule, event):
    m = {}
    try:
        m = json.loads(rule.match_json or "{}")
    except Exception:
        pass
    if m.get("method") and m["method"] != event.method:
        return False
    if m.get("path") and m["path"] not in event.path:
        return False
    if m.get("body_contains") and m["body_contains"] not in event.body:
        return False
    return True


def sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def forward(rule, event):
    try:
        payload = event.body.encode()
        req = urllib.request.Request(
            rule.forward_url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        if rule.hmac_secret:
            req.add_header("X-Hook-Signature", sign(payload, rule.hmac_secret))
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200, str(r.status)
    except Exception as e:
        return False, str(e)[:80]
