"""Single-owner local persistence: no raw samples or journal text are stored."""

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo
from .models import Preferences


class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, at TEXT, source TEXT, result TEXT);
            CREATE TABLE IF NOT EXISTS checkins(id TEXT PRIMARY KEY, at TEXT, source TEXT, status TEXT, result TEXT, feedback TEXT);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
            """)
        os.chmod(path, 0o600)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def prefs(self):
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key='prefs'").fetchone()
        return Preferences.model_validate_json(row[0]) if row else Preferences()

    def save_prefs(self, prefs):
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO settings VALUES('prefs',?)", (prefs.model_dump_json(),))

    def ingest(self, window, assessment, now):
        p = self.prefs()
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            # Source partitions keep demo retries and real device events independent.
            event_id = window.source + ":" + window.event_id
            previous = db.execute("SELECT result FROM events WHERE id=?", (event_id,)).fetchone()
            if previous:
                return {**json.loads(previous[0]), "duplicate": True}
            cutoff = (now - timedelta(days=7)).isoformat()
            db.execute("DELETE FROM events WHERE at < ?", (cutoff,))
            db.execute("DELETE FROM checkins WHERE at < ?", (cutoff,))
            result = dict(assessment)
            if not result["candidate"]:
                # A changed context invalidates an unanswered prompt from an earlier window.
                closed = {
                    "status": "context_changed",
                    "message": "The context changed. This earlier check-in is closed; no action is needed.",
                    "cards": [],
                    "resources": [],
                }
                db.execute(
                    "UPDATE checkins SET status='context_changed',result=? WHERE source=? AND status='pending'",
                    (json.dumps(closed), window.source),
                )
            local = now.astimezone(ZoneInfo(p.timezone))
            h = local.hour
            quiet = (
                (
                    (p.quiet_start <= h < p.quiet_end)
                    if p.quiet_start < p.quiet_end
                    else (h >= p.quiet_start or h < p.quiet_end)
                )
                if p.quiet_start != p.quiet_end
                else False
            )
            recent = db.execute(
                "SELECT at FROM checkins WHERE source=? ORDER BY at DESC", (window.source,)
            ).fetchall()
            today = sum(
                datetime.fromisoformat(row[0]).astimezone(ZoneInfo(p.timezone)).date() == local.date()
                for row in recent
            )
            snooze = db.execute(
                "SELECT value FROM settings WHERE key=?", ("snooze:" + window.source,)
            ).fetchone()
            if result["candidate"]:
                reason = None
                if not p.enabled:
                    reason = "paused"
                elif quiet:
                    reason = "quiet_hours"
                elif snooze and datetime.fromisoformat(snooze[0]) > now:
                    reason = "snoozed"
                elif today >= p.daily_limit:
                    reason = "daily_limit"
                elif recent and now - datetime.fromisoformat(recent[0][0]) < timedelta(
                    minutes=p.cooldown_minutes
                ):
                    reason = "cooldown"
                if reason:
                    result.update(candidate=False, reason=reason)
                else:
                    checkin_id = str(uuid4())
                    result.update(
                        checkin_id=checkin_id, message="A small check-in? What's happening for you right now?"
                    )
                    db.execute(
                        "INSERT INTO checkins VALUES(?,?,?,'pending',?,NULL)",
                        (checkin_id, now.isoformat(), window.source, json.dumps(result)),
                    )
            db.execute(
                "INSERT INTO events VALUES(?,?,?,?)",
                (event_id, now.isoformat(), window.source, json.dumps(result)),
            )
            return result

    def get(self, checkin_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM checkins WHERE id=?", (checkin_id,)).fetchone()
        return dict(row) if row else None

    def complete(self, checkin_id, result, now):
        with self.connect() as db:
            row = db.execute("SELECT source FROM checkins WHERE id=?", (checkin_id,)).fetchone()
            db.execute(
                "UPDATE checkins SET status=?,result=? WHERE id=?",
                (result["status"], json.dumps(result), checkin_id),
            )
            if result["status"] in {"snooze", "exercise"}:
                db.execute(
                    "INSERT OR REPLACE INTO settings VALUES(?,?)",
                    ("snooze:" + row[0], (now + timedelta(hours=2)).isoformat()),
                )

    def feedback(self, checkin_id, feedback):
        with self.connect() as db:
            db.execute("UPDATE checkins SET feedback=? WHERE id=?", (feedback.model_dump_json(), checkin_id))

    def export(self, now):
        cutoff = (now - timedelta(days=7)).isoformat()
        with self.connect() as db:
            db.execute("DELETE FROM events WHERE at < ?", (cutoff,))
            db.execute("DELETE FROM checkins WHERE at < ?", (cutoff,))
            return {
                "checkins": [
                    {
                        **dict(r),
                        "result": json.loads(r["result"]),
                        "feedback": json.loads(r["feedback"]) if r["feedback"] else None,
                    }
                    for r in db.execute("SELECT * FROM checkins ORDER BY at DESC")
                ],
                "events": [
                    {"at": r["at"], "source": r["source"], **json.loads(r["result"])}
                    for r in db.execute("SELECT * FROM events ORDER BY at DESC LIMIT 100")
                ],
            }

    def erase(self):
        with self.lock, self.connect() as db:
            db.execute("PRAGMA secure_delete=ON")
            db.executescript("DELETE FROM events; DELETE FROM checkins; DELETE FROM settings;")
            db.execute("VACUUM")
