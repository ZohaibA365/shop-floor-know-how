"""The Ask pipeline shared by the Ask page and eval.py, including the code-side safety checks."""
from core.llm import answer_question


STOPWORDS = {"a", "an", "the", "and", "or", "you", "your", "it", "if", "to", "of", "in", "on", "for",
             "is", "are", "be", "do", "not", "any", "every", "time", "before", "after", "with", "out"}


def _words(text: str) -> set[str]:
    words = text.lower().replace(",", " ").replace(".", " ").split()
    return {w for w in words if w not in STOPWORDS}


def _verbatim_safety(note: str, source: dict) -> str:
    """Return a safety note exactly as written in the source, or '' if none is relevant."""
    notes = source["body"].get("safety_notes", [])
    if not note.strip() or not notes:
        return ""
    for n in notes:
        if note.strip().lower() in n.lower() or n.lower() in note.lower():
            return n
    # The model paraphrased: show the closest real note instead, word for word.
    # Only swap in a note that shares at least half of the model's meaningful words.
    best = max(notes, key=lambda n: len(_words(n) & _words(note)))
    shared = len(_words(best) & _words(note))
    return best if shared >= 2 and shared >= len(_words(note)) / 2 else ""


def ask(question: str, approved: list[dict]) -> dict:
    """Returns {answered, answer, source, safety_note}. source is None when not answered."""
    if not approved:
        return {"answered": False, "answer": "", "source": None, "safety_note": ""}
    result = answer_question(question, approved)
    by_id = {i["id"]: i for i in approved}
    source = by_id.get(result.source_id.strip())
    # Never trust a citation we can't verify: it must be an approved instruction we sent.
    if not result.answered or source is None or source["status"] != "approved" or not result.answer.strip():
        return {"answered": False, "answer": "", "source": None, "safety_note": ""}
    return {
        "answered": True,
        "answer": result.answer.strip(),
        "source": source,
        "safety_note": _verbatim_safety(result.safety_note, source),
    }
