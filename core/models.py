"""Pydantic models for every JSON shape Claude returns."""
from pydantic import BaseModel, Field


class InstructionBody(BaseModel):
    purpose: str
    tools: list[str] = Field(default_factory=list)
    steps: list[str]
    quality_checks: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    low_confidence: list[str] = Field(default_factory=list)


class AskResult(BaseModel):
    answered: bool
    answer: str = ""
    source_id: str = ""
    safety_note: str = ""


def _list_of_strings():
    return {"type": "array", "items": {"type": "string"}}


# JSON schemas sent to the API as structured outputs (kept explicit and simple).
INSTRUCTION_SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {"type": "string"},
        "tools": _list_of_strings(),
        "steps": _list_of_strings(),
        "quality_checks": _list_of_strings(),
        "safety_notes": _list_of_strings(),
        "common_mistakes": _list_of_strings(),
        "low_confidence": _list_of_strings(),
    },
    "required": ["purpose", "tools", "steps", "quality_checks",
                 "safety_notes", "common_mistakes", "low_confidence"],
    "additionalProperties": False,
}

ASK_SCHEMA = {
    "type": "object",
    "properties": {
        "answered": {"type": "boolean"},
        "answer": {"type": "string"},
        "source_id": {"type": "string"},
        "safety_note": {"type": "string"},
    },
    "required": ["answered", "answer", "source_id", "safety_note"],
    "additionalProperties": False,
}
