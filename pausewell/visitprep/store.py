"""Owner-scoped SQLite storage. Authorization happens before text retrieval."""

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .fixtures import OWNER, PATIENT_ID, RECORDS, FOREIGN_PATIENT_ID, FOREIGN_RECORD


class AccessDenied(Exception):
    pass


class CapacityExceeded(Exception):
    pass


class AgendaConflict(Exception):
    def __init__(self, message, outcome="revision_conflict"):
        super().__init__(message)
        self.outcome = outcome


class VisitPrepStore:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.lock = threading.RLock()
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY, owner TEXT NOT NULL, patient_id TEXT NOT NULL,
                    title TEXT NOT NULL, date TEXT NOT NULL, kind TEXT NOT NULL,
                    text TEXT NOT NULL, synthetic INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS briefs (
                    id TEXT PRIMARY KEY, owner TEXT NOT NULL, at TEXT NOT NULL,
                    record_ids TEXT NOT NULL, result TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS agendas (
                    brief_id TEXT PRIMARY KEY, owner TEXT NOT NULL,
                    revision INTEGER NOT NULL, result TEXT NOT NULL
                );
            """)
            if not db.execute("SELECT 1 FROM metadata WHERE key='initialized'").fetchone():
                self._seed(db)
                db.execute("INSERT INTO metadata VALUES ('initialized','true')")
        os.chmod(path, 0o600)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA secure_delete=ON")
        return db

    @staticmethod
    def authorize_patient(patient_id):
        if patient_id != PATIENT_ID:
            raise AccessDenied("Record or patient unavailable")

    @staticmethod
    def _insert(db, record, owner=OWNER, patient_id=PATIENT_ID):
        db.execute(
            "INSERT INTO records VALUES (?,?,?,?,?,?,?,?)",
            (
                record["id"],
                owner,
                patient_id,
                record["title"],
                record["date"],
                record["kind"],
                record["text"],
                bool(record.get("synthetic", True)),
            ),
        )

    def _seed(self, db):
        for record in RECORDS:
            self._insert(db, record)
        self._insert(db, FOREIGN_RECORD, "different-owner", FOREIGN_PATIENT_ID)

    @staticmethod
    def _public(row):
        record = dict(row)
        record.pop("owner", None)
        record["synthetic"] = bool(record["synthetic"])
        return record

    def authorized_ids(self, patient_id, record_ids=None):
        self.authorize_patient(patient_id)
        with self.connect() as db:
            if record_ids is None:
                rows = db.execute(
                    "SELECT id,owner,patient_id FROM records WHERE owner=? AND patient_id=? ORDER BY date,id",
                    (OWNER, patient_id),
                ).fetchall()
            else:
                if not record_ids or len(record_ids) != len(set(record_ids)):
                    raise AccessDenied("Record or patient unavailable")
                marks = ",".join("?" for _ in record_ids)
                # Metadata only until every ID has passed ownership checks.
                rows = db.execute(
                    f"SELECT id,owner,patient_id FROM records WHERE id IN ({marks})", record_ids
                ).fetchall()
                if len(rows) != len(record_ids) or any(
                    r["owner"] != OWNER or r["patient_id"] != patient_id for r in rows
                ):
                    raise AccessDenied("Record or patient unavailable")
            if len(rows) > 10:
                raise CapacityExceeded("Select at most 10 records for one brief")
            return [row["id"] for row in rows]

    def retrieve(self, patient_id, record_ids=None):
        with self.lock:
            ids = self.authorized_ids(patient_id, record_ids)
            if not ids:
                return []
            marks = ",".join("?" for _ in ids)
            with self.connect() as db:
                rows = db.execute(
                    f"SELECT * FROM records WHERE id IN ({marks}) AND owner=? AND patient_id=? ORDER BY date,id",
                    [*ids, OWNER, patient_id],
                ).fetchall()
            records = [self._public(row) for row in rows]
            if sum(len(record["text"]) for record in records) > 24000:
                raise CapacityExceeded("Select records totaling at most 24,000 text characters")
            return records

    def list_records(self, patient_id=PATIENT_ID):
        self.authorize_patient(patient_id)
        with self.connect() as db:
            return [
                self._public(row)
                for row in db.execute(
                    "SELECT * FROM records WHERE owner=? AND patient_id=? ORDER BY date,id",
                    (OWNER, patient_id),
                )
            ]

    def add_record(self, value):
        record = {"id": str(uuid4()), **value.model_dump(mode="json"), "patient_id": PATIENT_ID}
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            totals = db.execute(
                "SELECT COUNT(*),COALESCE(SUM(LENGTH(text)),0) FROM records WHERE owner=?", (OWNER,)
            ).fetchone()
            if totals[0] >= 40 or totals[1] + len(record["text"]) > 120000:
                raise CapacityExceeded("The local workspace allows 40 records and 120,000 text characters")
            self._insert(db, record)
        return record

    def delete_record(self, record_id):
        with self.lock:
            self.authorized_ids(PATIENT_ID, [record_id])
            with self.connect() as db:
                db.execute("DELETE FROM records WHERE id=? AND owner=?", (record_id, OWNER))
                # Cited text is also removed from every derived brief, including exports.
                for row in db.execute("SELECT id,record_ids FROM briefs WHERE owner=?", (OWNER,)).fetchall():
                    if record_id in json.loads(row["record_ids"]):
                        db.execute("DELETE FROM agendas WHERE brief_id=? AND owner=?", (row["id"], OWNER))
                        db.execute("DELETE FROM briefs WHERE id=?", (row["id"],))

    def save_brief(self, result, record_ids):
        with self.lock:
            if record_ids:
                # Deletion may occur while inference runs. Recheck before persisting.
                self.authorized_ids(PATIENT_ID, record_ids)
            with self.connect() as db:
                db.execute(
                    "INSERT INTO briefs VALUES (?,?,?,?,?)",
                    (
                        result["id"],
                        OWNER,
                        datetime.now(timezone.utc).isoformat(),
                        json.dumps(record_ids),
                        json.dumps(result),
                    ),
                )
                db.execute(
                    "DELETE FROM briefs WHERE owner=? AND id NOT IN (SELECT id FROM briefs WHERE owner=? ORDER BY at DESC LIMIT 20)",
                    (OWNER, OWNER),
                )
                db.execute(
                    "DELETE FROM agendas WHERE owner=? AND brief_id NOT IN (SELECT id FROM briefs WHERE owner=?)",
                    (OWNER, OWNER),
                )

    def briefs(self):
        with self.connect() as db:
            return [
                json.loads(row[0])
                for row in db.execute(
                    "SELECT result FROM briefs WHERE owner=? ORDER BY at DESC LIMIT 20", (OWNER,)
                )
            ]

    def get_brief(self, brief_id):
        with self.connect() as db:
            row = db.execute("SELECT result FROM briefs WHERE id=? AND owner=?", (brief_id, OWNER)).fetchone()
        if not row:
            raise AccessDenied("Brief unavailable")
        return json.loads(row[0])

    @staticmethod
    def _draft_agenda(brief):
        return {
            "brief_id": brief["id"],
            "revision": 0,
            "priorities": [],
            "questions": [question["text"] for question in brief["questions"][:3]],
            "approved": False,
            "approved_at": None,
            "updated_at": None,
            "approval_notice": "Your words and priorities are saved locally. Approval means you reviewed this agenda, not that its medical content has been verified.",
        }

    def get_agenda(self, brief_id):
        with self.lock:
            # Ownership and existence precede reading editable agenda content.
            brief = self.get_brief(brief_id)
            with self.connect() as db:
                row = db.execute(
                    "SELECT result FROM agendas WHERE brief_id=? AND owner=?", (brief_id, OWNER)
                ).fetchone()
            return json.loads(row[0]) if row else self._draft_agenda(brief)

    def save_agenda(self, brief_id, value):
        with self.lock, self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            # Read only this principal's brief, then recheck all its source IDs.
            brief_row = db.execute(
                "SELECT record_ids,result FROM briefs WHERE id=? AND owner=?", (brief_id, OWNER)
            ).fetchone()
            if not brief_row:
                raise AccessDenied("Brief unavailable")
            record_ids = json.loads(brief_row["record_ids"])
            if record_ids:
                self.authorized_ids(PATIENT_ID, record_ids)
            row = db.execute(
                "SELECT revision FROM agendas WHERE brief_id=? AND owner=?", (brief_id, OWNER)
            ).fetchone()
            revision = row[0] if row else 0
            if value.expected_revision != revision:
                raise AgendaConflict("This agenda changed. Reload it before saving or approving.")
            now = datetime.now(timezone.utc).isoformat()
            agenda = {
                **self._draft_agenda(json.loads(brief_row["result"])),
                "revision": revision + 1,
                "priorities": value.priorities,
                "questions": value.questions,
                "approved": value.approved,
                "approved_at": now if value.approved else None,
                "updated_at": now,
            }
            db.execute(
                "INSERT OR REPLACE INTO agendas VALUES (?,?,?,?)",
                (brief_id, OWNER, agenda["revision"], json.dumps(agenda)),
            )
            return agenda

    def agenda_export(self, brief_id):
        with self.lock:
            brief = self.get_brief(brief_id)
            agenda = self.get_agenda(brief_id)
            if not agenda["approved"]:
                raise AgendaConflict("Approve the current agenda before exporting it.", "not_approved")
            return {
                "brief": brief,
                "agenda": agenda,
                "notice": "Patient-reviewed visit agenda. Record quotations are historical source text, not current treatment instructions. Confirm decisions with your clinician.",
            }

    def erase(self):
        with self.lock, self.connect() as db:
            db.executescript("DELETE FROM records; DELETE FROM briefs; DELETE FROM agendas;")
            # Keep initialized: erased demo records must not reappear on restart.
            db.execute("VACUUM")

    def reset_demo(self):
        with self.lock, self.connect() as db:
            count = db.execute("SELECT COUNT(*) FROM records").fetchone()[0]
            if count:
                raise CapacityExceeded("Delete the current workspace before restoring fictional demo records")
            self._seed(db)
