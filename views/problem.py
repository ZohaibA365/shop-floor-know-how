import streamlit as st

from core.ui import APP_NAME, CLIENT_LABEL, card, eyebrow, stage_strip

st.caption(f"{APP_NAME} · {CLIENT_LABEL}")
st.title("Dave retires in 8 months. What he knows isn't written down anywhere.")
stage_strip()
st.markdown("Grand River Fabrication: 45 people in Cambridge, Ontario. Laser cutting, press brake bending, welding.")

with st.container(key="problem_cards"):
    c1, c2, c3 = st.columns(3)
    c1.markdown(card("Who has the pain",
                     "<b>Supervisors</b> answer the same questions all day. <b>New hires</b> wait or guess. "
                     "The <b>owner</b> pays for scrap and slow onboarding."), unsafe_allow_html=True)
    c2.markdown(card("The problem",
                     "Veteran know-how leaves when people retire. Dave has 31 years on the press brake. "
                     "Jordan, 3 weeks in, keeps asking the same things."), unsafe_allow_html=True)
    c3.markdown(card("The opportunity", "Ontario manufacturing workers retire every year.", big="~20,000"),
                unsafe_allow_html=True)

eyebrow("Value estimate")
st.caption("Example assumptions, replaced with the client's real numbers in week 1")
rows = [
    ("Supervisor time on repeat questions", "3 leads × 5 hrs/week, cut in half, 48 weeks, $45/hr", 16_200),
    ("Faster onboarding", "6 new hires/year, 10 hrs/week of lead time for 8 weeks, cut by 2 weeks, $45/hr", 5_400),
    ("Less scrap", "$60,000/year press brake scrap, cut 10%", 6_000),
]
table = "| Saving | How it's calculated | Per year |\n|---|---|---:|\n"
table += "".join(f"| {name} | {how} | ${value:,} |\n" for name, how, value in rows)
table += f"| **Total** | | **≈ ${sum(v for *_, v in rows):,}** |\n"
table += "| Cost to run | API, hosting, upkeep | ≈ $1,200 |\n"
st.markdown(table)

with st.expander("How I'd confirm this with the client", expanded=False):
    st.markdown("Questions for the owner and supervisors:\n"
                "1. Which questions do you answer most often?\n"
                "2. Which jobs would be hardest to cover if someone left tomorrow?\n"
                "3. How long until a new hire runs a job alone?\n"
                "4. What did the last scrap or rework problem cost?")

st.markdown('<div class="note-line">Release 1 scope: one machine area, one loop (capture, approve, ask). '
            'No integrations.</div>', unsafe_allow_html=True)
