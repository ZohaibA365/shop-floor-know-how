"""Claude calls. Every call returns strict JSON, validated with pydantic, with one retry."""
import json
import os

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from core.models import ASK_SCHEMA, INSTRUCTION_SCHEMA, AskResult, InstructionBody

MODEL = "claude-opus-5-5"


class LLMError(Exception):
    """A friendly error the UI can show as-is."""


_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        load_dotenv()
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise LLMError("No API key found. Add the API key to the app's secrets and restart.")
        _client = anthropic.Anthropic(timeout=45.0, max_retries=1)
    return _client


def _send(system: str, messages: list, schema: dict) -> str:
    try:
        response = client().beta.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=system,
            messages=messages,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
            # On a safety decline, the API retries on a fallback model in the same call.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError:
        raise LLMError("The API key was rejected. Check the key in the app's secrets.")
    except anthropic.RateLimitError:
        raise LLMError("Rate limited by the API. Wait a few seconds and try again.")
    except anthropic.APIConnectionError:
        raise LLMError("Could not reach the API. Check the internet connection.")
    except anthropic.APIStatusError as e:
        raise LLMError(f"The API returned an error ({e.status_code}). Try again.")
    if response.stop_reason == "refusal":
        raise LLMError("The model declined this request.")
    return "".join(b.text for b in response.content if b.type == "text")


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return text.strip()


def call_json(system: str, user: str, model_cls: type[BaseModel], schema: dict) -> BaseModel:
    messages = [{"role": "user", "content": user}]
    for attempt in range(2):
        text = _send(system, messages, schema)
        try:
            return model_cls.model_validate_json(_strip_fences(text))
        except ValidationError as e:
            if attempt == 1:
                raise LLMError("The model returned invalid JSON twice. Try again.")
            messages += [
                {"role": "assistant", "content": text or "(empty)"},
                {"role": "user", "content": f"That was not valid JSON for the schema ({e.error_count()} errors). "
                                            "Reply again with only the JSON object."},
            ]


# ---------- drafting ----------

DRAFT_SYSTEM = """You turn a veteran machine operator's spoken walkthrough into a draft work instruction
for a fabrication shop. A supervisor will review your draft before anyone sees it.

Rules:
- Use only what the speaker said. Never add steps, tools, numbers or specs they did not say.
- Keep every safety warning word for word, as the speaker said it, in safety_notes.
- Write steps as short, plain, imperative sentences in the order the speaker gave them.
- Put tips about what goes wrong in common_mistakes, and checks of the finished part in quality_checks.
- If anything is unclear, ambiguous, or a value is missing (for example "set it to the length on the
  sheet" with no number), add a short note to low_confidence saying what the supervisor should confirm.
- Return only the JSON object."""


def draft_instruction(transcript: str, job_name: str, machine: str) -> InstructionBody:
    user = f"Job: {job_name}\nMachine: {machine}\n\nTranscript:\n\"\"\"\n{transcript}\n\"\"\""
    return call_json(DRAFT_SYSTEM, user, InstructionBody, INSTRUCTION_SCHEMA)


# ---------- answering ----------

ASK_SYSTEM = """You answer shop-floor questions from new operators at a fabrication shop.
You may ONLY use the approved work instructions provided. They are the only source of truth.

Rules:
- Answer only if an approved instruction directly covers what was asked. Do not stretch an
  instruction to a machine, material, part or process it does not mention, and never use
  general knowledge. If it is not covered, return answered=false with empty answer, source_id
  and safety_note.
- If answered, set source_id to the id of the one instruction you used.
- Write the answer as a short, plain answer: one direct sentence, then numbered steps if useful,
  each step on its own line. Only include steps the instruction actually says.
  If the question asks whether a safety step can be skipped, start with "No."
- If the source instruction has a safety note relevant to the question, copy that one safety note
  word for word into safety_note. Otherwise leave safety_note empty.
- Return only the JSON object."""


def answer_question(question: str, instructions: list[dict]) -> AskResult:
    context = [
        {"id": i["id"], "job_name": i["job_name"], "machine": i["machine"],
         **{k: v for k, v in i["body"].items() if k != "low_confidence"}}
        for i in instructions
    ]
    user = ("Approved instructions:\n" + json.dumps(context, indent=1)
            + f"\n\nQuestion from a new operator: {question}")
    return call_json(ASK_SYSTEM, user, AskResult, ASK_SCHEMA)
