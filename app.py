"""Manufacturing Knowledge Capture: interview demo. Run with: streamlit run app.py"""
import streamlit as st

from core import seed, transcribe
from core.ui import APP_NAME, CLIENT_LABEL, ROLES, inject_css

st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
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

with st.sidebar:
    st.markdown(f"## 🛠️ {APP_NAME}")
    st.caption(CLIENT_LABEL)
    st.divider()
    for page in PAGES:
        st.page_link(page)
    st.divider()

    st.markdown("**Switch user**")
    for key, label in [("veteran", "Veteran"), ("supervisor", "Supervisor"), ("new_hire", "New hire")]:
        role = ROLES[key]
        if st.button(f"{label} · {role['name']}", key=f"role_{key}", width="stretch"):
            st.switch_page(role["page"])
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
