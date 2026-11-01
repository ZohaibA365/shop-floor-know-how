"""Manufacturing Knowledge Capture: interview demo. Run with: streamlit run app.py"""
from pathlib import Path

import streamlit as st

from core import seed, transcribe
from core.ui import APP_NAME, CLIENT_LABEL, ROLES, esc, inject_css

st.set_page_config(page_title=APP_NAME, page_icon=":material/precision_manufacturing:", layout="wide")
inject_css()
seed.ensure_seeded()

# Load speech-to-text once at startup (cached across reruns and sessions).
st.session_state.whisper_error = transcribe.warm_up()

PAGES = [
    st.Page("views/problem.py", title="1. The Problem", default=True),
    st.Page("views/capture.py", title="2. Capture"),
    st.Page("views/review.py", title="3. Review & Approve"),
    st.Page("views/ask.py", title="4. Ask"),
    st.Page("views/pilot.py", title="5. Pilot Plan & Metrics"),
]
nav = st.navigation(PAGES, position="hidden")

current_role = next((k for k, r in ROLES.items() if Path(r["page"]).stem == nav.url_path), None)


def _on_switch_user():
    st.session_state.pending_user = st.session_state.switch_user


with st.sidebar:
    st.markdown(f'<p class="side-title">{esc(APP_NAME)}</p><p class="side-client">{esc(CLIENT_LABEL)}</p>',
                unsafe_allow_html=True)
    st.divider()
    for page in PAGES:
        st.page_link(page)
    st.divider()

    # The control always shows whose page you are on (none on the Problem and Pilot pages).
    st.session_state.switch_user = current_role
    st.segmented_control("Switch user", list(ROLES), format_func=lambda k: ROLES[k]["name"],
                         key="switch_user", on_change=_on_switch_user, width="stretch",
                         help="Dave: veteran · Priya: supervisor · Jordan: new hire")
    pending = st.session_state.pop("pending_user", None)
    if pending and pending != current_role:
        st.switch_page(ROLES[pending]["page"])
    st.divider()

    with st.expander("Demo controls", expanded=False):
        st.toggle("Load backup BR-220", key="use_backup",
                  help="Makes a pre-approved BR-220 instruction visible, in case live drafting fails.")
        if st.button("Reset demo", width="stretch"):
            seed.reset_demo()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.reset_flash = True
            st.switch_page("views/problem.py")

if st.session_state.pop("reset_flash", False):
    st.toast("Demo reset to its clean starting state.")

nav.run()
