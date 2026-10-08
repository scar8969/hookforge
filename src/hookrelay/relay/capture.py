import json, time

MAX_BODY = 1024 * 1024  # 1MB

def capture(inbox, request):
    from ..models import Event
    body = request.get_data() if hasattr(request, "get_data") else b""
    body = body[:MAX_BODY].decode("utf-8", "ignore")
    headers = {k: v for k, v in (request.headers.items() if hasattr(request, "headers") else [])}
    return Event(inbox_id=inbox.id, method=request.method, path=request.path,
                 headers_json=json.dumps(headers), body=body,
                 ip=request.remote_addr or "", ms=0)
