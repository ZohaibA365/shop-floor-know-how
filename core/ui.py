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
.stButton button {{ font-size: 1rem; border-radius: 8px; }}

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
  border-radius: 10px; padding: 18px 20px; height: 100%; }}
.card h4 {{ margin: 0 0 6px 0; color: {STEEL}; font-size: 1.15rem; }}
.card p {{ margin: 0; color: #2B3138; }}
.card .big {{ font-size: 2rem; font-weight: 800; color: #1F2A36; }}

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


def chips(items):
    st.markdown("".join(f'<span class="chip">{esc(i)}</span>' for i in items), unsafe_allow_html=True)


def nice_date(ts: str | None) -> str:
    return ts[:10] if ts else ""
