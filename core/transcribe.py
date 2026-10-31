"""Local speech-to-text with faster-whisper. The model loads once at app startup."""
import tempfile
from pathlib import Path

import streamlit as st

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


@st.cache_resource(show_spinner="Loading the speech-to-text model (first launch downloads it)…")
def get_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel("base.en", device="cpu", compute_type="int8", download_root=str(MODEL_DIR))


def warm_up() -> str | None:
    """Load the model now. Returns an error message, or None if it loaded."""
    try:
        get_whisper()
        return None
    except Exception as e:  # no network on first run, disk issues, etc.
        return f"Speech-to-text is unavailable ({type(e).__name__}). Use the sample transcript."


def transcribe(data: bytes, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix) as f:
        f.write(data)
        f.flush()
        segments, _ = get_whisper().transcribe(f.name, beam_size=1, vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()
