from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Inbox(db.Model):
    __tablename__ = "inboxes"
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    inbox_id = db.Column(db.Integer, db.ForeignKey("inboxes.id"), index=True)
    method = db.Column(db.String(8), default="")
    path = db.Column(db.String(256), default="")
    headers_json = db.Column(db.Text, default="{}")
    body = db.Column(db.Text, default="")
    status = db.Column(db.Integer, default=200)
    ms = db.Column(db.Integer, default=0)
    ip = db.Column(db.String(64), default="")
    at = db.Column(db.DateTime, default=datetime.utcnow)


class Rule(db.Model):
    __tablename__ = "rules"
    id = db.Column(db.Integer, primary_key=True)
    inbox_id = db.Column(db.Integer, db.ForeignKey("inboxes.id"))
    match_json = db.Column(db.Text, default="{}")
    forward_url = db.Column(db.String(512), default="")
    hmac_secret = db.Column(db.String(128), default="")
    enabled = db.Column(db.Integer, default=1)
