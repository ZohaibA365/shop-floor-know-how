from pathlib import Path

import streamlit as st

from core import db
from core.llm import LLMError, draft_instruction
from core.transcribe import transcribe
from core.ui import APP_NAME, chips, esc, role_badge

SAMPLE = Path(__file__).resolve().parent.parent / "demo_data" / "dave_br220.txt"
PROMPTS = ["What do you check first?", "What usually goes wrong?",
           "What's the trick most people miss?", "What safety step do you never skip?"]

role_badge("veteran")
st.title("Capture")
st.caption(f"{APP_NAME} · talk through a job. The AI writes the draft. Priya approves it.")

c1, c2 = st.columns(2)
job_name = c1.text_input("Job name", value="Press brake setup: bracket BR-220")
machine = c2.text_input("Machine", value="Press brake, 10-gauge mild steel")

st.markdown("**While you record, try answering:**")
chips(PROMPTS)

up_col, or_col, sample_col = st.columns([4, 0.5, 2], vertical_alignment="center")
audio = up_col.file_uploader("Upload a recording", type=["mp3", "m4a", "wav"])
or_col.markdown("<div style='text-align:center'>or</div>", unsafe_allow_html=True)
if sample_col.button("📄 Use sample transcript", width="stretch"):
    st.session_state.capture_transcript = SAMPLE.read_text().strip()
    st.session_state.capture_source = "sample"
    st.session_state.capture_done = None

sample_msg = st.empty()  # filled after the draft button, so it disappears once a draft exists

if st.session_state.get("whisper_error"):
    st.warning(st.session_state.whisper_error)

if st.button("✨ Create draft", type="primary"):
    try:
        transcript = st.session_state.get("capture_transcript", "")
        if audio is not None and st.session_state.get("capture_source") != "sample":
            with st.spinner("Transcribing the recording…"):
                transcript = transcribe(audio.getvalue(), Path(audio.name).suffix)
        if not transcript:
            st.warning("Upload a recording or use the sample transcript first.")
        else:
            with st.spinner("Writing the draft instruction…"):
                body = draft_instruction(transcript, job_name, machine)
            inst_id = db.next_instruction_id()
            db.insert_instruction({"id": inst_id, "job_name": job_name, "machine": machine,
                                   "transcript": transcript, "body": body.model_dump(),
                                   "status": "draft", "author": "Dave", "version": 0})
            st.session_state.review_flash = None
            st.session_state.capture_done = {"id": inst_id, "transcript": transcript, "body": body.model_dump()}
            st.session_state.capture_source = None
            st.session_state.capture_transcript = ""
    except LLMError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Could not transcribe that file ({type(e).__name__}). Try the sample transcript.")

if st.session_state.get("capture_source") == "sample":
    sample_msg.success("Sample transcript loaded: Dave talking through BR-220.")

done = st.session_state.get("capture_done")
if done:
    b = done["body"]
    st.success(f"Draft {done['id']} saved with Dave as author. It is waiting for Priya's review "
               "and is not visible to new hires yet.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Steps", len(b["steps"]))
    m2.metric("Safety notes", len(b["safety_notes"]))
    m3.metric("Quality checks", len(b["quality_checks"]))
    m4.metric("Items to confirm", len(b["low_confidence"]))
    st.markdown("**Transcript**")
    st.markdown(f'<div class="transcript">{esc(done["transcript"])}</div>', unsafe_allow_html=True)
    if st.button("Go to Review & Approve as Priya →", type="primary"):
        st.switch_page("views/review.py")
