import streamlit as st

from core import db
from core.ask import ask
from core.llm import LLMError
from core.ui import APP_NAME, esc, nice_date, role_badge, safety_box

EXAMPLES = [
    "My bend is coming out at 92 degrees, what do I do?",
    "Can I skip lockout if I'm just swapping the punch quickly?",
    "How do I set up the laser cutter?",
]

role_badge("new_hire")
st.title("Ask")
st.caption(f"{APP_NAME} · answers come only from instructions Priya has approved.")


def run_question(question: str):
    question = question.strip()
    if not question:
        return
    approved = db.approved_for_ask(st.session_state.get("use_backup", False))
    try:
        with st.spinner("Checking approved instructions…"):
            result = ask(question, approved)
    except LLMError as e:
        st.session_state.ask_error = str(e)
        return
    source_id = result["source"]["id"] if result["answered"] else None
    qid = db.log_question(question, "Jordan", result["answered"], source_id)
    st.session_state.ask_error = None
    st.session_state.last_answer = {"qid": qid, "question": question, "rated": None, **result}


with st.form("ask_form", clear_on_submit=True, border=False):
    col_q, col_btn = st.columns([6, 1], vertical_alignment="bottom")
    typed = col_q.text_input("Ask about any job", placeholder="e.g. What die do I use for BR-220?")
    if col_btn.form_submit_button("Ask", type="primary", width="stretch"):
        run_question(typed)

st.write("Try one:")
for col, example in zip(st.columns(len(EXAMPLES)), EXAMPLES):
    if col.button(example, width="stretch"):
        run_question(example)

if st.session_state.get("ask_error"):
    st.error(st.session_state.ask_error)

last = st.session_state.get("last_answer")
if last:
    st.markdown(f"#### “{esc(last['question'])}”")
    if last["answered"]:
        src = last["source"]
        with st.container(key="answer_card"):
            st.markdown(last["answer"])
            if last["safety_note"]:
                st.markdown(safety_box(last["safety_note"]), unsafe_allow_html=True)
            st.markdown(
                f'<div class="source-line">📄 From: <b>{esc(src["job_name"])}</b> ({esc(src["id"])}) · '
                f'by {esc(src["author"])} · approved by {esc(src["approver"])}, '
                f'{nice_date(src["approved_at"])} · v{src["version"]}</div>',
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns([1, 1, 6])
            if last["rated"] is None:
                if c1.button("👍 Helpful", key=f"up_{last['qid']}"):
                    db.set_helpful(last["qid"], True)
                    last["rated"] = True
                    st.rerun()
                if c2.button("👎 Not helpful", key=f"down_{last['qid']}"):
                    db.set_helpful(last["qid"], False)
                    last["rated"] = False
                    st.rerun()
            else:
                c1.caption("Thanks, feedback logged.")
    else:
        with st.container(key="noanswer_card"):
            st.markdown("### 🙋 I don't have an approved instruction for this. Ask your lead.")
            st.markdown("Sent to Priya's gaps list, so this job can be captured next.")
