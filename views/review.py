import streamlit as st

from core import db
from core.ui import APP_NAME, esc, mono, nice_date, nice_datetime, role_badge, safety_box, status_badge

role_badge("supervisor")
st.title("Review & Approve")
st.caption(f"{APP_NAME} · nothing reaches new hires until it is approved here.")

drafts = db.list_instructions("draft")
sent_back = db.list_instructions("sent_back")
approved = db.approved_for_ask(st.session_state.get("use_backup", False))
gaps = db.open_gaps()

tab_drafts, tab_approved, tab_gaps = st.tabs([
    f"Drafts ({len(drafts)})",
    f"Approved instructions ({len(approved)})",
    f"Unanswered questions ({len(gaps)})",
])


def box_label(eyebrow: str, sub: str):
    st.markdown(f'<div class="eyebrow">{esc(eyebrow)}</div><div class="box-sub">{esc(sub)}</div>',
                unsafe_allow_html=True)


def edit_list(label: str, items: list[str], key: str) -> list[str]:
    """One text box per line, sized to its text. Clearing a box removes that line."""
    with st.container(key=f"edit_{key}"):
        values = [st.text_area(f"{label} {n}", value=item, key=f"{key}_{n}", height="content",
                               label_visibility="collapsed")
                  for n, item in enumerate(items, 1)]
    return [v.strip() for v in values if v.strip()]


def field_list(label: str, items: list[str], key: str) -> list[str]:
    st.markdown(f'<div class="field-label">{esc(label)}</div>', unsafe_allow_html=True)
    return edit_list(label, items, key)


def decision_buttons(where: str) -> tuple[bool, bool]:
    b1, b2 = st.columns(2)
    approve = b1.button("Approve and publish", type="primary", width="stretch", icon=":material/check:",
                        key=f"approve_{where}")
    back = b2.button("Send back to Dave", width="stretch", key=f"back_{where}")
    return approve, back


# ---------- Tab A: drafts ----------
with tab_drafts:
    flash = st.session_state.get("review_flash")
    if flash:
        st.success(flash)
        if st.button("Open the Ask page as Jordan"):
            st.session_state.review_flash = None
            st.switch_page("views/ask.py")

    if not drafts:
        if not flash:
            st.info("No drafts waiting. Dave can capture one on the Capture page.")
        for d in sent_back:
            st.markdown(f"{status_badge('sent_back')} &nbsp; {esc(d['job_name'])} ({mono(d['id'])})",
                        unsafe_allow_html=True)
    else:
        if len(drafts) > 1:
            choice = st.selectbox("Draft", drafts, format_func=lambda d: f"{d['job_name']} ({d['id']})")
        else:
            choice = drafts[0]
        d, body, k = choice, choice["body"], choice["id"]

        with st.container(key="review_cols"):
            left, right = st.columns([2, 3], gap="large")
        with left:
            st.subheader("What Dave said")
            st.markdown(f'<div class="transcript">{esc(d["transcript"])}</div>', unsafe_allow_html=True)
            st.caption(f"Recorded by {esc(d['author'])} · {mono(nice_datetime(d['created_at']))}",
                       unsafe_allow_html=True)

        with right:
            st.markdown(f"{status_badge(d['status'])} &nbsp; {mono(d['id'])} · author {esc(d['author'])}",
                        unsafe_allow_html=True)
            job_name = st.text_input("Job name", value=d["job_name"], key=f"{k}_job")
            top_approve, top_back = decision_buttons("top")
            with st.container(key=f"edit_{k}_purpose_box"):
                purpose = st.text_area("Purpose", value=body["purpose"], key=f"{k}_purpose", height="content")

            if body["low_confidence"]:
                with st.container(key=f"lowconf_edit_{k}"):
                    box_label("Needs review", "Please confirm (AI was unsure)")
                    low = edit_list("Please confirm", body["low_confidence"], f"{k}_low")
            else:
                low = []

            with st.container(key=f"safety_edit_{k}"):
                box_label("Safety", "Kept word for word")
                safety = edit_list("Safety", body["safety_notes"], f"{k}_safety")

            steps = field_list("Steps", body["steps"], f"{k}_steps")
            tools = field_list("Tools", body["tools"], f"{k}_tools")
            checks = field_list("Quality checks", body["quality_checks"], f"{k}_checks")
            mistakes = field_list("Common mistakes", body["common_mistakes"], f"{k}_mistakes")
            st.caption("Every line is editable. Clear a line to remove it.")

            new_body = {"purpose": purpose.strip(), "tools": tools, "steps": steps, "quality_checks": checks,
                        "safety_notes": safety, "common_mistakes": mistakes, "low_confidence": low}

            bottom_approve, bottom_back = decision_buttons("bottom")
            if top_approve or bottom_approve:
                db.update_instruction(k, job_name.strip(), new_body)
                db.approve(k, "Priya")
                st.session_state.review_flash = "Approved. Now visible to new hires."
                st.rerun()
            if top_back or bottom_back:
                db.update_instruction(k, job_name.strip(), new_body)
                db.send_back(k)
                st.session_state.review_flash = "Sent back to Dave with your edits."
                st.rerun()

# ---------- Tab B: approved ----------
with tab_approved:
    table = "| ID | Job | Author | Approved by | Date | Version |\n|---|---|---|---|---:|---:|\n"
    table += "".join(f"| {mono(a['id'])} | {esc(a['job_name'])} | {esc(a['author'])} | {esc(a['approver'])} | "
                     f"{nice_date(a['approved_at'])} | {a['version']} |\n" for a in approved)
    st.markdown(table, unsafe_allow_html=True)
    for a in approved:
        with st.expander(f"{a['job_name']} ({a['id']})"):
            st.markdown("\n".join(f"{n}. {s}" for n, s in enumerate(a["body"]["steps"], 1)))
            for note in a["body"]["safety_notes"]:
                st.markdown(safety_box(note), unsafe_allow_html=True)

# ---------- Tab C: gaps ----------
with tab_gaps:
    st.subheader("Gaps to capture next")
    st.caption("Questions new hires asked that no approved instruction covers.")
    if not gaps:
        st.success("No open gaps.")
    for g in gaps:
        c1, c2, c3 = st.columns([6, 1.6, 1.6], vertical_alignment="center")
        times = f" · asked {g['times']}×" if g["times"] > 1 else ""
        c1.markdown(f"**{esc(g['question'])}**  \n<small>asked by {esc(g['asked_by'].replace(',', ', '))}{times}</small>",
                    unsafe_allow_html=True)
        c2.markdown(mono(nice_date(g["asked_at"])), unsafe_allow_html=True)
        if c3.button("Mark covered", key=f"cover_{g['id']}"):
            db.mark_covered(g["question"])
            st.rerun()
