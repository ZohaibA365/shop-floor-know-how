"""Seed data and the demo reset."""
import json
from datetime import datetime, timedelta
from pathlib import Path

from core import db

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo_data"


def load_seed() -> dict:
    return json.loads((DEMO_DIR / "seed.json").read_text())


def _days_ago(n: int) -> str:
    return (datetime.now() - timedelta(days=n)).replace(microsecond=0).isoformat()


def seed_instructions() -> list[dict]:
    """Start-of-shift and backup BR-220 as full records (also used by eval.py)."""
    seed = load_seed()
    records = []
    for key in ("start_of_shift", "backup_br220"):
        rec = dict(seed[key])
        when = _days_ago(rec.pop("days_ago"))
        rec["created_at"] = rec["approved_at"] = when
        if "transcript_file" in rec:
            rec["transcript"] = (DEMO_DIR / rec.pop("transcript_file")).read_text().strip()
        records.append(rec)
    return records


def reset_demo():
    """Restore the clean demo state: start-of-shift approved, no live BR-220, seeded question log."""
    db.DB_PATH.unlink(missing_ok=True)
    for rec in seed_instructions():
        db.insert_instruction(rec)
    for q in load_seed()["questions"]:
        db.insert_question({**q, "asked_at": _days_ago(q["days_ago"])})


def ensure_seeded():
    if not db.DB_PATH.exists() or db.is_empty():
        reset_demo()
