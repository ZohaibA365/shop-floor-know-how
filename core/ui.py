"""Shared look and feel: app name, colours, CSS and small HTML helpers."""
import html

import streamlit as st

from core.db import local_time

APP_NAME = "Manufacturing Knowledge Capture"
CLIENT_NAME = "Grand River Fabrication"
CLIENT_LABEL = f"Demo client: {CLIENT_NAME} (fictional)"

# Who is "logged in" on each page.
ROLES = {
    "veteran": {"name": "Dave", "title": "Press brake lead · Veteran", "page": "views/capture.py"},
    "supervisor": {"name": "Priya", "title": "Production supervisor", "page": "views/review.py"},
    "new_hire": {"name": "Jordan", "title": "New press brake operator · 3 weeks in", "page": "views/ask.py"},
}

# Fonts are loaded by the theme in .streamlit/config.toml; colours live in :root below.
CSS = """
<style>
:root {
  --bg: #F7F6F3; --surface: #FFFFFF; --border: #E4E2DD;
  --text: #1F2328; --muted: #6B6F76; --primary: #1F3A5F;
  --review-text: #8A5A00; --review-bg: #FFF6E5; --review-border: #EBCB8B;
  --safety-text: #B42318; --safety-bg: #FEF3F2; --safety-border: #F2B8B5;
  --ok-text: #1E6B47; --ok-bg: #ECF6F0;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
}

/* ---------- page frame ---------- */
.block-container { max-width: 1008px; padding: 48px 24px 64px 24px; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"], footer, #MainMenu { display: none !important; }

/* ---------- type ---------- */
.stApp { color: var(--text); }
.stApp p, .stApp li, .stApp label, .stApp td { font-size: 16px; line-height: 1.5; }
.stApp h1 { font-size: 32px !important; font-weight: 600 !important; letter-spacing: -0.015em;
  line-height: 1.2 !important; padding: 0 0 8px 0 !important; }
.stApp h2, .stApp h3 { font-size: 20px !important; font-weight: 600 !important; letter-spacing: -0.005em;
  padding: 24px 0 8px 0 !important; }
.stApp h4 { font-size: 17px !important; font-weight: 600 !important; }
[data-testid="stCaptionContainer"] p { color: var(--muted); font-size: 14px; }
.eyebrow { font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted);
  font-weight: 500; margin: 0 0 8px 0; }
/* A section eyebrow sits 24px below the previous block and tight above its heading. */
.section-eyebrow { padding-top: 24px; margin: 0; }
[data-testid="stElementContainer"]:has(.section-eyebrow) + [data-testid="stElementContainer"] h3 {
  padding-top: 0 !important; }
.viewing-as { color: var(--muted); font-size: 14px; margin-bottom: 8px; }
.mono, .stApp code { font-family: var(--mono) !important; font-size: 0.94em; }
.stApp code { background: none !important; color: inherit !important; padding: 0 !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * { font-family: var(--mono) !important;
  font-weight: 500; font-size: 28px !important; }
[data-testid="stMetricLabel"] p { color: var(--muted); font-size: 14px !important; }

/* ---------- buttons ---------- */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
  border-radius: 6px; font-weight: 500; min-height: 40px; height: auto; box-shadow: none; }
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {
  background: var(--surface) !important; border: 1px solid var(--border) !important; color: var(--text) !important; }
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--primary) !important; color: var(--primary) !important; }
/* Wrap long button labels instead of cutting them off with "…" on narrow screens. */
.stButton button *, .stFormSubmitButton button * { white-space: normal !important; overflow: visible !important;
  text-overflow: clip !important; word-break: normal !important; overflow-wrap: normal !important; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
.stApp .side-title { font-weight: 600; font-size: 16px; line-height: 1.3; margin: 0; }
.stApp .side-client { color: var(--muted); font-size: 13px; line-height: 1.4; margin: 4px 0 0 0; }
[data-testid="stSidebar"] hr { margin: 16px 0; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] { padding: 4px 8px; border-radius: 6px; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p { font-size: 15px; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] { background: #EEF1F5; }
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] p {
  color: var(--primary); font-weight: 600; }

/* ---------- cards ---------- */
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 24px; height: 100%; box-sizing: border-box; }
.card h4 { margin: 0 0 8px 0; font-size: 17px; font-weight: 600; color: var(--text); padding: 0; }
.card p { margin: 0; }
.card .big { font-family: var(--mono); font-size: clamp(24px, 2.6vw, 32px); font-weight: 500;
  white-space: nowrap; margin: 0 0 8px 0; color: var(--text); }
.note-line { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px 24px; margin-top: 16px; }
.goal-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 32px; margin-top: 32px; }
.goal-card h4 { margin: 0 0 16px 0; font-size: 12px !important; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); font-weight: 500 !important; padding: 0; }
.goal-card p { margin: 0; font-size: 24px !important; line-height: 1.4 !important; color: var(--primary);
  font-weight: 500; letter-spacing: -0.01em; }

/* Never break words mid-word inside cards and strips. */
.card, .card *, .stage, .stage *, .goal-card, .goal-card *, .note-line, .safety-box, .review-box {
  word-break: normal !important; overflow-wrap: normal !important; hyphens: none !important; }

/* Card rows reflow when the main area is narrow (e.g. a ~1000px window with the sidebar open). */
.st-key-week_cards, .st-key-problem_cards, .st-key-review_cols { container-type: inline-size; }
/* Cards in a row share one height: stretch every wrapper between the column and the card.
   Streamlit also pulls markdown up by 1rem, which would make cards hang into the row gap. */
:is(.st-key-week_cards, .st-key-problem_cards) [data-testid="stColumn"] :is(
  [data-testid="stVerticalBlock"], [data-testid="stElementContainer"], [data-testid="stMarkdown"],
  [data-testid="stMarkdown"] > div, [data-testid="stMarkdownContainer"]) { height: 100%; margin-bottom: 0 !important; }
.st-key-week_cards [data-testid="stHorizontalBlock"],
.st-key-problem_cards [data-testid="stHorizontalBlock"],
.st-key-review_cols [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; row-gap: 16px !important; }
@container (max-width: 860px) {
  .st-key-week_cards [data-testid="stColumn"] {
    flex: 1 1 calc(50% - 1rem) !important; min-width: calc(50% - 1rem) !important; }
}
@container (max-width: 700px) {
  .st-key-problem_cards [data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 100% !important; }
}
@container (max-width: 760px) {
  .st-key-review_cols [data-testid="stColumn"] { flex: 1 1 100% !important; min-width: 100% !important; }
  /* Only the two outer columns stack; button pairs inside them stay side by side. */
  .st-key-review_cols [data-testid="stColumn"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
  .st-key-review_cols [data-testid="stColumn"] [data-testid="stColumn"] {
    flex: 1 1 0 !important; min-width: 0 !important; }
}

/* ---------- stage strip ---------- */
.stage-wrap { container-type: inline-size; margin: 8px 0 24px 0; }
.stage-strip { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 16px; row-gap: 16px; }
@container (max-width: 640px) { .stage-strip { grid-template-columns: repeat(2, 1fr); } }
.stage-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.stage-num { font-family: var(--mono); font-size: 12px; color: var(--primary); font-weight: 500; }
.stage-line { flex: 1; height: 1px; background: var(--border); }
.stage-name { font-weight: 600; font-size: 15px; display: block; }
.stage-desc { color: var(--muted); font-size: 14px; line-height: 1.4; display: block; margin-top: 2px; }

/* ---------- tables ---------- */
.stMarkdown table { border-collapse: collapse; width: 100%; border: none; margin: 8px 0 16px 0;
  background: transparent; }
.stMarkdown th { font-size: 12px !important; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--muted); font-weight: 500; background: transparent !important; border: none !important;
  border-bottom: 1px solid var(--border) !important; padding: 8px 12px 8px 0 !important; }
.stMarkdown td { border: none !important; border-bottom: 1px solid var(--border) !important;
  padding: 12px 12px 12px 0 !important; vertical-align: top; background: transparent !important; }
.stMarkdown tr { background: transparent !important; }
.stMarkdown td[style*="right"], .stMarkdown th[style*="right"] { text-align: right; }
.stMarkdown td[style*="right"] { font-family: var(--mono); white-space: nowrap; }

/* ---------- status ---------- */
.badge { display: inline-block; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase; vertical-align: middle; }
.badge-draft { color: var(--review-text); background: var(--review-bg); }
.badge-approved { color: var(--ok-text); background: var(--ok-bg); }
.badge-sent_back { color: var(--muted); background: #EFEEEA; }
.safety-box { background: var(--safety-bg); border: 1px solid var(--safety-border); border-radius: 8px;
  padding: 16px; margin: 16px 0; color: var(--text); }
.safety-box .eyebrow, [class*="st-key-safety_edit"] .eyebrow { color: var(--safety-text); font-weight: 600; }
.review-box { background: var(--review-bg); border: 1px solid var(--review-border); border-radius: 8px;
  padding: 16px; margin: 8px 0; }
.review-box .eyebrow, [class*="st-key-lowconf_edit"] .eyebrow { color: var(--review-text); font-weight: 600; }
[class*="st-key-safety_edit"] { background: var(--safety-bg); border: 1px solid var(--safety-border);
  border-radius: 8px; padding: 16px; }
[class*="st-key-lowconf_edit"] { background: var(--review-bg); border: 1px solid var(--review-border);
  border-radius: 8px; padding: 16px; }
.box-sub { color: var(--muted); font-size: 14px; margin: -4px 0 8px 0; }

/* ---------- review editor ---------- */
/* Text areas grow with their text as you type. */
[class*="st-key-edit_"] textarea { field-sizing: content; min-height: 0 !important; resize: none; }
[class*="st-key-edit_"] [data-baseweb="textarea"] { min-height: 0 !important; }
.field-label { font-weight: 600; font-size: 15px; margin: 16px 0 8px 0; }

/* ---------- answer ---------- */
.st-key-answer_card, .st-key-noanswer_card { border-radius: 8px; padding: 24px; }
.st-key-answer_card { background: var(--surface); border: 1px solid var(--border); }
.st-key-noanswer_card { background: var(--review-bg); border: 1px solid var(--review-border); }
.st-key-noanswer_card h3 { padding-top: 0 !important; }
.source-line { color: var(--muted); font-size: 14px; margin-top: 16px; border-top: 1px solid var(--border);
  padding-top: 16px; }

/* ---------- misc ---------- */
.transcript { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 16px; line-height: 1.6; white-space: pre-wrap; max-height: 560px; overflow-y: auto; }
.chip { display: inline-block; background: var(--surface); border: 1px solid var(--border); border-radius: 6px;
  padding: 4px 12px; margin: 0 8px 8px 0; font-size: 14px; }
[data-testid="stExpander"] details { border-radius: 8px; background: var(--surface); }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(text) -> str:
    return html.escape(str(text))


def mono(text) -> str:
    return f'<span class="mono">{esc(text)}</span>'


def eyebrow(text: str):
    st.markdown(f'<div class="eyebrow section-eyebrow">{esc(text)}</div>', unsafe_allow_html=True)


def role_badge(role_key: str):
    role = ROLES[role_key]
    st.markdown(f'<div class="viewing-as">Viewing as {esc(role["name"])} · {esc(role["title"])}</div>',
                unsafe_allow_html=True)


def status_badge(status: str) -> str:
    labels = {"draft": "Draft", "approved": "Approved", "sent_back": "Sent back to Dave"}
    return f'<span class="badge badge-{status}">{labels.get(status, status)}</span>'


def safety_box(text: str) -> str:
    return f'<div class="safety-box"><div class="eyebrow">Safety</div>{esc(text)}</div>'


def lowconf_box(text: str) -> str:
    return f'<div class="review-box"><div class="eyebrow">Needs review</div>{esc(text)}</div>'


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
    steps = "".join(
        f'<div class="stage"><div class="stage-top"><span class="stage-num">{n:02d}</span>'
        f'<span class="stage-line"></span></div><span class="stage-name">{esc(name)}</span>'
        f'<span class="stage-desc">{esc(line)}</span></div>'
        for n, (name, line) in enumerate(STAGES, 1))
    st.markdown(f'<div class="stage-wrap"><div class="stage-strip">{steps}</div></div>', unsafe_allow_html=True)


def goal_card(title: str, text: str):
    st.markdown(f'<div class="goal-card"><h4>{esc(title)}</h4><p>{esc(text)}</p></div>',
                unsafe_allow_html=True)


def chips(items):
    st.markdown("".join(f'<span class="chip">{esc(i)}</span>' for i in items), unsafe_allow_html=True)


def nice_date(ts: str | None) -> str:
    """Date in Toronto time, e.g. 2026-10-31."""
    return local_time(ts).strftime("%Y-%m-%d") if ts else ""


def nice_datetime(ts: str | None) -> str:
    """Date and time in Toronto time, e.g. 2026-10-31 14:05."""
    return local_time(ts).strftime("%Y-%m-%d %H:%M") if ts else ""
