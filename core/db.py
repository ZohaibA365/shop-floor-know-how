"""SQLite storage for instructions and the question log."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
TZ = ZoneInfo("America/Toronto")

SCHEMA = """
CREATE TABLE IF NOT EXISTS instructions (
    id          TEXT PRIMARY KEY,
    job_name    TEXT NOT NULL,
    machine     TEXT NOT NULL,
    transcript  TEXT NOT NULL DEFAULT '',
    body_json   TEXT NOT NULL,
    status      TEXT NOT NULL,          -- draft | approved | sent_back
    author      TEXT NOT NULL,
    approver    TEXT,
    approved_at TEXT,
    version     INTEGER NOT NULL DEFAULT 0,
    is_backup   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS questions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    question  TEXT NOT NULL,
    asked_by  TEXT NOT NULL,
    answered  INTEGER NOT NULL,
    source_id TEXT,
    helpful   INTEGER,                 -- 1 up, 0 down, NULL not rated
    covered   INTEGER NOT NULL DEFAULT 0,
    asked_at  TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def local_time(ts: str) -> datetime:
    """Parse a stored timestamp as Toronto time. Old rows without an offset are in the server's local time."""
    return datetime.fromisoformat(ts).astimezone(TZ)


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _to_dict(row) -> dict:
    d = dict(row)
    if "body_json" in d:
        d["body"] = json.loads(d.pop("body_json"))
    return d


# ---------- instructions ----------

def insert_instruction(rec: dict):
    with connect() as conn:
        conn.execute(
            """INSERT INTO instructions (id, job_name, machine, transcript, body_json, status,
               author, approver, approved_at, version, is_backup, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rec["id"], rec["job_name"], rec["machine"], rec.get("transcript", ""),
             json.dumps(rec["body"]), rec["status"], rec["author"], rec.get("approver"),
             rec.get("approved_at"), rec.get("version", 0), int(rec.get("is_backup", 0)),
             rec.get("created_at") or now()),
        )


def next_instruction_id() -> str:
    with connect() as conn:
        rows = conn.execute("SELECT id FROM instructions WHERE id GLOB 'INS-[0-9][0-9][0-9]'").fetchall()
    n = max([int(r["id"][4:]) for r in rows] or [0]) + 1
    return f"INS-{n:03d}"


def get_instruction(inst_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM instructions WHERE id = ?", (inst_id,)).fetchone()
    return _to_dict(row) if row else None


def list_instructions(status: str, include_backup: bool = False) -> list[dict]:
    sql = "SELECT * FROM instructions WHERE status = ?"
    if not include_backup:
        sql += " AND is_backup = 0"
    with connect() as conn:
        rows = conn.execute(sql + " ORDER BY created_at DESC", (status,)).fetchall()
    return [_to_dict(r) for r in rows]


def approved_for_ask(include_backup: bool) -> list[dict]:
    """The ONLY instructions new hires can get answers from.

    A backup is skipped when a live instruction for the same job is already approved."""
    rows = list_instructions("approved", include_backup)
    live_jobs = {r["job_name"].strip().lower() for r in rows if not r["is_backup"]}
    return [r for r in rows if not (r["is_backup"] and r["job_name"].strip().lower() in live_jobs)]


def update_instruction(inst_id: str, job_name: str, body: dict):
    with connect() as conn:
        conn.execute("UPDATE instructions SET job_name = ?, body_json = ? WHERE id = ?",
                     (job_name, json.dumps(body), inst_id))


def approve(inst_id: str, approver: str):
    with connect() as conn:
        conn.execute(
            """UPDATE instructions SET status = 'approved', approver = ?, approved_at = ?,
               version = version + 1 WHERE id = ?""",
            (approver, now(), inst_id),
        )


def send_back(inst_id: str):
    with connect() as conn:
        conn.execute("UPDATE instructions SET status = 'sent_back' WHERE id = ?", (inst_id,))


# ---------- question log ----------

def log_question(question: str, asked_by: str, answered: bool, source_id: str | None) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO questions (question, asked_by, answered, source_id, asked_at) VALUES (?,?,?,?,?)",
            (question, asked_by, int(answered), source_id, now()),
        )
        return cur.lastrowid


def insert_question(q: dict):
    with connect() as conn:
        conn.execute(
            """INSERT INTO questions (question, asked_by, answered, source_id, helpful, covered, asked_at)
               VALUES (?,?,?,?,?,?,?)""",
            (q["question"], q["asked_by"], int(q["answered"]), q.get("source_id"),
             q.get("helpful"), int(q.get("covered", 0)), q["asked_at"]),
        )


def set_helpful(question_id: int, helpful: bool):
    with connect() as conn:
        conn.execute("UPDATE questions SET helpful = ? WHERE id = ?", (int(helpful), question_id))


def open_gaps() -> list[dict]:
    """Unanswered questions, one row per distinct question, newest first."""
    with connect() as conn:
        rows = conn.execute(
            """SELECT MAX(id) AS id, question, GROUP_CONCAT(DISTINCT asked_by) AS asked_by,
                      COUNT(*) AS times, MAX(asked_at) AS asked_at
               FROM questions WHERE answered = 0 AND covered = 0
               GROUP BY LOWER(TRIM(question)) ORDER BY asked_at DESC"""
        ).fetchall()
    return [dict(r) for r in rows]


def mark_covered(question: str):
    with connect() as conn:
        conn.execute("UPDATE questions SET covered = 1 WHERE answered = 0 AND LOWER(TRIM(question)) = LOWER(TRIM(?))",
                     (question,))


def all_questions() -> list[dict]:
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM questions").fetchall()]


def is_empty() -> bool:
    with connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM instructions").fetchone()[0] == 0
