from datetime import datetime

import streamlit as st

from core import db
from core.ui import APP_NAME, card, goal_card, stage_strip

st.caption(APP_NAME)
st.title("Pilot Plan & Metrics")
stage_strip()

# ---------- timeline ----------
st.subheader("4-week pilot")
weeks = [
    ("Week 0", "Baseline", "Log supervisor time on repeat questions, scrap and onboarding hours."),
    ("Week 1", "Capture", "Veterans record their top 3 jobs. Supervisor approves."),
    ("Weeks 2–3", "Use", "New hires use Ask. Gaps captured twice a week."),
    ("Week 4", "Decide", "Compare against baseline. Expand, adjust or stop."),
]
with st.container(key="week_cards"):
    for col, (when, title, text) in zip(st.columns(4), weeks):
        col.markdown(card(f"{when} · {title}", text), unsafe_allow_html=True)
st.markdown('<div class="scope-line">Every week: 30-minute progress check-in with the supervisor to review KPIs, '
            'new gaps and which jobs to capture next.</div>', unsafe_allow_html=True)

# ---------- success metrics ----------
include_backup = st.session_state.get("use_backup", False)
approved = db.approved_for_ask(include_backup)
questions = db.all_questions()
rated = [q for q in questions if q["helpful"] is not None]
helpful_pct = round(100 * sum(q["helpful"] for q in rated) / len(rated)) if rated else None
if questions:
    first = min(datetime.fromisoformat(q["asked_at"]) for q in questions)
    weeks_running = max(1.0, (datetime.now() - first).days / 7)
    people = len({q["asked_by"] for q in questions})
    per_hire_week = len(questions) / people / weeks_running
else:
    per_hire_week = None

st.subheader("Success metrics, agreed with the owner in Week 0")
st.caption("Current is pulled live from the app's database.")
kpis = [
    ("Supervisor hours on repeat questions (per lead, per week)", "5", "Down 30% (3.5)", "Measured in week 4"),
    ("Instructions approved", "0", "10+", str(len(approved))),
    ("Answers marked helpful", "–", "70%+", f"{helpful_pct}% of {len(rated)} rated" if rated else "–"),
    ("Questions asked per new hire per week", "Not tracked", "Tracked weekly",
     f"{per_hire_week:.1f}" if per_hire_week is not None else "–"),
    ("Unsafe or made-up answers in spot checks", "–", "0", "Weekly spot check + 15‑question test set"),
]
table = "| KPI | Baseline | Target | Current |\n|---|---|---|---|\n"
table += "".join(f"| {k} | {b} | {t} | **{c}** |\n" for k, b, t, c in kpis)
st.markdown(table)

# ---------- roadmap ----------
st.subheader("Roadmap")
st.markdown("- **Release 1 (now):** capture, approve, ask\n"
            "- **Release 2:** ranked gap list and search once instructions outgrow the prompt "
            "(starts only if pilot targets are hit)\n"
            "- **Release 3:** photos and clips, review dates, onboarding checklists")

# ---------- where AI fits ----------
st.markdown(card("Where AI fits, and what stays human",
                 "<b>AI</b> drafts instructions and answers only from approved text. <b>People</b> approve, "
                 "own safety and decide what gets captured.<br><br>Release 1 uses a language model with no "
                 "custom ML. Release 2's search is where I'd bring in an ML specialist, to decide when to move "
                 "beyond sending every instruction in the prompt and how to measure answer quality."),
            unsafe_allow_html=True)
st.write("")

# ---------- training and guardrails ----------
c1, c2 = st.columns(2)
with c1.expander("Training", expanded=False):
    st.markdown("- **Veterans:** 15 min\n- **Supervisors:** 20 min\n"
                "- **New hires:** 10 min + a one-page card\n\nThe supervisor is the **floor champion**.")
with c2.expander("Guardrails", expanded=False):
    st.markdown("- Nothing goes live without approval\n- Answers only from approved instructions, with sources\n"
                "- Safety notes kept word for word\n- Unknowns go to a person\n"
                "- Shop data not used for model training\n- Veterans credited as authors")

# ---------- user stories ----------
STORIES = [
    ("As a veteran operator, I want to talk through a job instead of writing it up, so capturing what I know "
     "doesn't eat my shift.",
     "A recording up to 5 minutes becomes a draft in under 1 minute, in the standard template, with the "
     "veteran as author."),
    ("As a supervisor, I want to review and fix drafts before anyone sees them, so new hires only learn "
     "what's correct.",
     "Drafts are invisible to new hires, every line is editable, low-confidence lines are highlighted, and "
     "approval records who and when."),
    ("As a new hire, I want plain answers that show where they came from, so I can trust them on the floor.",
     "Every answer shows its source and approver, in under 10 seconds."),
    ("As a new hire, I want the tool to tell me when it doesn't know, so I never act on a guess.",
     "Uncovered questions get \"Ask your lead\" and at least 4 of the 5 not-covered eval questions pass."),
    ("As a supervisor, I want to see questions the tool couldn't answer, so I know what to capture next.",
     "Each one appears in the gaps log with its date and can be marked covered."),
]
with st.expander("Release 1 user stories", expanded=False):
    for n, (story, done) in enumerate(STORIES, 1):
        st.markdown(card(f"Story {n}", f"{story}<br><br><b>Done when:</b> {done}"), unsafe_allow_html=True)
        st.write("")

goal_card("The goal", "The goal isn't to introduce AI for the sake of introducing it. It's to learn where the "
                      "friction is in a business and meaningfully improve how they operate.")
