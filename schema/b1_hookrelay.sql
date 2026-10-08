-- 📡 hookrelay schema
CREATE TABLE inboxes(id INTEGER PRIMARY KEY, token TEXT UNIQUE, name TEXT, created_at DATETIME);
CREATE TABLE events(id INTEGER PRIMARY KEY, inbox_id INTEGER REFERENCES inboxes(id), method TEXT, path TEXT, headers_json TEXT DEFAULT '{}', body TEXT, status INTEGER DEFAULT 200, ms INTEGER DEFAULT 0, ip TEXT, at DATETIME);
CREATE TABLE rules(id INTEGER PRIMARY KEY, inbox_id INTEGER REFERENCES inboxes(id), match_json TEXT DEFAULT '{}', forward_url TEXT, hmac_secret TEXT, enabled INTEGER DEFAULT 1);
