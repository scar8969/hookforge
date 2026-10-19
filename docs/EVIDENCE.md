# Evidence

Every line below was produced by a command run against this exact checkout, on this machine, at the time recorded. Nothing here is copied from the README.

| | |
| --- | --- |
| Generated | 2026-10-19 11:55 |
| Python | 3.14.7 |
| Platform | Windows 11 |

## Test suite

```sh
python -m pytest -q
```

- exit code **0**
- 25 passed in 1.20s

## Static gates

| Gate | Exit | Last line |
| --- | --- | --- |
| `ruff check` | 0 | All checks passed! |
| `ruff format --check` | 0 | 21 files already formatted |
| `mypy src` | 0 | Success: no issues found in 17 source files |
| `bandit -c pyproject.toml -r src` | 0 | — |

## Live route walk

The application was imported through `wsgi.py` and each GET path declared in `openapi/` was requested once through the Werkzeug test client.

| Status | Path | Bytes | Content-Type |
| --- | --- | --- | --- |
| 200 | `/api/health` | 49 | application/json |
| 200 | `/api/inboxes` | 15 | application/json |
| 200 | `/api/events` | 27 | application/json |
| 404 | `/h/{token}` | 22 | application/json |
| 200 | `/inboxes` | 5097 | text/html |

5 paths walked, 0 of them raised or answered 5xx.

## CLI

```
usage: hookrelay [-h] {inbox-create,inboxes,events,replay} ...

webhook relay + debugger

positional arguments:
  {inbox-create,inboxes,events,replay}
    inbox-create        create an inbox and print its token
    inboxes             list inboxes
    events              list captured events for one inbox
    replay              re-deliver an event to its matching rules

options:
  -h, --help            show this help message and exit
```

## Screenshots

Captured from the running service with headless Chromium at 1440x900 and committed with the repository:

| File | Bytes |
| --- | --- |
| `docs/assets/screens/healthz.png` | 8,504 |
| `docs/assets/screens/inboxes.png` | 37,515 |
| `docs/assets/screens/livez.png` | 7,468 |
| `docs/assets/screens/metrics.png` | 15,166 |
| `docs/assets/screens/readyz.png` | 7,880 |
| `docs/assets/screens/root.png` | 44,636 |
| `docs/assets/screens/version.png` | 26,979 |

## What this file does not prove

- It is not a load test: every request is a single uncached call from one process.
- A green suite is not a coverage claim; `pytest --cov` reports the number the README quotes.
- The route walk exercises GET paths only; mutating routes are covered by the suite.
