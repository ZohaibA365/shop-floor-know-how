"""Offline eval of the Ask pipeline. Usage: python eval.py

Loads the start-of-shift and backup BR-220 instructions straight from demo_data/seed.json,
so results don't depend on the live demo database.
"""
import json
from pathlib import Path

from core.ask import ask
from core.seed import seed_instructions

QUESTIONS = json.loads((Path(__file__).parent / "eval" / "questions.json").read_text())


def check(case: dict, result: dict) -> tuple[bool, str]:
    if case["expect"] == "no_answer":
        return (not result["answered"], "" if not result["answered"] else "answered but should not have")
    if not result["answered"]:
        return False, "said 'Ask your lead'"
    if result["source"]["id"] not in case["sources"]:
        return False, f"wrong source {result['source']['id']}"
    answer = result["answer"].lower()
    if case.get("must_say_no") and not answer.startswith("no"):
        return False, "did not say no"
    if not any(k in answer for k in case["keywords"]):
        return False, f"missing keyword {case['keywords']}"
    if case.get("safety") and not has_safety_note(case, result):
        return False, "safety note missing or not word for word"
    return True, ""


def has_safety_note(case: dict, result: dict) -> bool:
    """The right safety note is shown, exactly as written in the approved source."""
    if not result["answered"]:
        return False
    note = result["safety_note"]
    return case["safety_contains"] in note.lower() and note in result["source"]["body"]["safety_notes"]


def main():
    instructions = seed_instructions()  # start-of-shift + backup BR-220, both approved
    answer_ok = no_answer_ok = 0
    safety_cases, safety_ok = 0, 0
    for case in QUESTIONS:
        result = ask(case["q"], instructions)
        ok, why = check(case, result)
        if case["expect"] == "answer":
            answer_ok += ok
        else:
            no_answer_ok += ok
        if case.get("safety"):
            safety_cases += 1
            safety_ok += has_safety_note(case, result)
        print(f"{'PASS' if ok else 'FAIL'}  {case['q']}" + (f"   ({why})" if why else ""))

    n_answer = sum(c["expect"] == "answer" for c in QUESTIONS)
    print()
    print(f"Answered correctly:           {answer_ok}/{n_answer}")
    print(f"'Ask your lead' correctly:    {no_answer_ok}/{len(QUESTIONS) - n_answer}")
    print(f"Every safety question included its safety note: {'YES' if safety_ok == safety_cases else 'NO'}"
          f" ({safety_ok}/{safety_cases})")


if __name__ == "__main__":
    main()
