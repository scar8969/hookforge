== curl ==
# curl -X POST http://127.0.0.1:5000/h/8f3k2a -H "Content-Type: application/json" -d '{"type":"stripe.succeeded"}'
# GET  /api/inboxes
# POST /api/inboxes  {"name":"stripe"}
# GET  /api/events?inbox=8f3k2a&q=stripe
# POST /api/events/3/replay
# POST /api/rules  {"inbox_id":1,"match":{"body_contains":"stripe.succeeded"},"forward_url":"https://…","hmac_secret":"whsec_…"}

== session plan ==
# Session 1: inbox + capture (headers/body/1MB cap) → tests
# Session 2: events API + search + replay → tests
# Session 3: rules + HMAC forward → tests
# Session 4: web templates + screenshots → README → CI/Docker/Pages → tag
