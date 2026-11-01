"""Shared look and feel: app name, colours, CSS and small HTML helpers."""
import html

import streamlit as st

APP_NAME = "Manufacturing Knowledge Capture"
CLIENT_NAME = "Grand River Fabrication"
CLIENT_LABEL = f"Demo client: {CLIENT_NAME} (fictional)"

# Who is "logged in" on each page.
ROLES = {
    "veteran": {"name": "Dave", "title": "Press brake lead · Veteran", "page": "views/capture.py"},
    "supervisor": {"name": "Priya", "title": "Production supervisor", "page": "views/review.py"},
    "new_hire": {"name": "Jordan", "title": "New press brake operator · 3 weeks in", "page": "views/ask.py"},
}

STEEL = "#3A6EA5"
RED = "#C0392B"
YELLOW = "#F4D03F"
GREEN = "#2E8B57"

CSS = f"""
<style>
html, body, [class*="css"] {{ font-size: 18px; }}
.block-container {{ padding-top: 2.2rem; max-width: 1400px; }}
h1 {{ font-size: 2.3rem !important; }}
h2 {{ font-size: 1.7rem !important; }}
h3 {{ font-size: 1.35rem !important; }}
p, li, label, .stMarkdown {{ font-size: 1.05rem; }}
.stButton button {{ font-size: 1rem; border-radius: 8px; height: auto; }}
/* Wrap long button labels instead of cutting them off with "…" on narrow screens. */
.stButton button *, .stFormSubmitButton button * {{ white-space: normal !important; overflow: visible !important;
  text-overflow: clip !important; word-break: normal !important; overflow-wrap: normal !important; }}
/* Short rating buttons sit in narrow columns: keep them on one line. */
[class*="st-key-up_"] button *, [class*="st-key-down_"] button * {{ white-space: nowrap !important; }}

.role-pill {{
  display: inline-block; background: #EAF1F8; color: {STEEL};
  border: 1px solid #C9DAEB; border-radius: 999px;
  padding: 6px 16px; font-weight: 600; margin-bottom: 0.6rem;
}}
.badge {{ display: inline-block; border-radius: 6px; padding: 3px 12px;
  font-weight: 700; font-size: 0.9rem; letter-spacing: 0.02em; color: white; }}
.badge-draft {{ background: #8A94A0; }}
.badge-approved {{ background: {GREEN}; }}
.badge-sent_back {{ background: #B9770E; }}

.card {{ background: #FFFFFF; border: 1px solid #E1E5EA; border-left: 6px solid {STEEL};
  border-radius: 10px; padding: 18px 20px; height: 100%; box-sizing: border-box; }}
.card h4 {{ margin: 0 0 6px 0; color: {STEEL}; font-size: 1.15rem; }}
.card p {{ margin: 0; color: #2B3138; }}
.card .big {{ font-size: clamp(1.4rem, 2.4vw, 2rem); font-weight: 800; color: #1F2A36;
  white-space: nowrap; }}

/* Never break words mid-word inside cards and strips. */
.card, .card *, .stage, .stage *, .goal-card, .goal-card *, .scope-line {{
  word-break: normal !important; overflow-wrap: normal !important; hyphens: none !important; }}

/* Card rows reflow when the main area is narrow (e.g. a ~1000px window with the sidebar open). */
.st-key-week_cards, .st-key-problem_cards {{ container-type: inline-size; }}
/* Streamlit pulls markdown up by 1rem; without this the cards hang into the row gap. */
.st-key-week_cards .card, .st-key-problem_cards .card {{ margin-bottom: 1rem; }}
.st-key-week_cards [data-testid="stHorizontalBlock"],
.st-key-problem_cards [data-testid="stHorizontalBlock"] {{ flex-wrap: wrap !important; row-gap: 1rem !important; }}
@container (max-width: 860px) {{
  .st-key-week_cards [data-testid="stColumn"] {{
    flex: 1 1 calc(50% - 1rem) !important; min-width: calc(50% - 1rem) !important; }}
}}
@container (max-width: 620px) {{
  .st-key-problem_cards [data-testid="stColumn"] {{ flex: 1 1 100% !important; min-width: 100% !important; }}
}}

.safety-box {{ background: #FDEDEC; border: 2px solid {RED}; border-radius: 10px;
  padding: 12px 16px; margin: 8px 0; color: #78281F; }}
.safety-box b {{ color: {RED}; }}
.lowconf-box {{ background: #FEF9E7; border: 2px solid {YELLOW}; border-radius: 10px;
  padding: 10px 14px; margin: 6px 0; color: #6E5A00; }}
.source-line {{ color: #4A5562; font-size: 0.98rem; margin-top: 10px;
  border-top: 1px solid #E1E5EA; padding-top: 8px; }}
.transcript {{ background: #F5F7FA; border: 1px solid #E1E5EA; border-radius: 10px;
  padding: 16px; line-height: 1.6; white-space: pre-wrap; }}
.chip {{ display: inline-block; background: #EAF1F8; color: #24476B; border-radius: 999px;
  padding: 5px 14px; margin: 0 6px 6px 0; font-size: 0.95rem; }}
.scope-line {{ background: #EAF1F8; border-radius: 10px; padding: 14px 18px;
  font-weight: 600; color: #24476B; margin-top: 1rem; }}

.stage-wrap {{ container-type: inline-size; margin: 0.2rem 0 1.2rem 0; }}
.stage-strip {{ display: flex; flex-wrap: wrap; gap: 6px; }}
@container (max-width: 700px) {{ .stage {{ flex: 1 1 calc(50% - 6px) !important; }} }}
.stage {{ flex: 1 1 0; min-width: 0; background: #EAF1F8; border-top: 4px solid {STEEL}; border-radius: 6px;
  padding: 8px 12px; }}
.stage b {{ color: {STEEL}; font-size: 1rem; }}
.stage span {{ display: block; color: #4A5562; font-size: 0.88rem; line-height: 1.35; }}
.goal-card {{ border-left: 8px solid {STEEL}; background: #EAF1F8; border-radius: 10px;
  padding: 26px 30px; margin-top: 1.5rem; }}
.goal-card h4 {{ margin: 0 0 10px 0; color: {STEEL}; font-size: 1.3rem; }}
.goal-card p {{ margin: 0; font-size: 1.55rem; line-height: 1.45; color: #1F2A36; font-weight: 600; }}

/* Section containers created with st.container(key=...) */
.st-key-answer_card, .st-key-noanswer_card {{
  border-radius: 12px; padding: 18px 22px; background: #FFFFFF;
}}
.st-key-answer_card {{ border: 2px solid {GREEN}; }}
.st-key-noanswer_card {{ border: 2px solid #B9770E; background: #FEF5E7; }}
[class*="st-key-safety_edit"] {{ background: #FDEDEC; border: 2px solid {RED};
  border-radius: 10px; padding: 10px 14px; }}
[class*="st-key-lowconf_edit"] {{ background: #FEF9E7; border: 2px solid {YELLOW};
  border-radius: 10px; padding: 10px 14px; }}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(text) -> str:
    return html.escape(str(text))


def role_badge(role_key: str):
    role = ROLES[role_key]
    st.markdown(
        f'<span class="role-pill">👤 Logged in as {esc(role["name"])} · {esc(role["title"])}</span>',
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    labels = {"draft": "DRAFT", "approved": "APPROVED", "sent_back": "SENT BACK TO DAVE"}
    return f'<span class="badge badge-{status}">{labels.get(status, status.upper())}</span>'


def safety_box(text: str) -> str:
    return f'<div class="safety-box"><b>⚠ SAFETY</b><br>{esc(text)}</div>'


def lowconf_box(text: str) -> str:
    return f'<div class="lowconf-box">❓ {esc(text)}</div>'


def card(title: str, body: str, big: str = "") -> str:
    big_html = f'<div class="big">{esc(big)}</div>' if big else ""
    return f'<div class="card"><h4>{esc(title)}</h4>{big_html}<p>{body}</p></div>'


STAGES = [
    ("Match", "One clear problem, scoped with the owner and supervisor"),
    ("Build", "Capture, Review, Ask"),
    ("Deploy", "4-week pilot on one machine area"),
    ("Measure", "KPIs agreed in Week 0"),
]


def stage_strip():
    steps = "".join(f'<div class="stage"><b>{esc(name)}</b><span>{esc(line)}</span></div>'
                    for name, line in STAGES)
    st.markdown(f'<div class="stage-wrap"><div class="stage-strip">{steps}</div></div>', unsafe_allow_html=True)


def goal_card(title: str, text: str):
    st.markdown(f'<div class="goal-card"><h4>{esc(title)}</h4><p>{esc(text)}</p></div>',
                unsafe_allow_html=True)


def chips(items):
    st.markdown("".join(f'<span class="chip">{esc(i)}</span>' for i in items), unsafe_allow_html=True)


def nice_date(ts: str | None) -> str:
    return ts[:10] if ts else ""
