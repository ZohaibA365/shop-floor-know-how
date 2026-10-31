import streamlit as st

from core import db
from core.ui import APP_NAME, esc, nice_date, role_badge, status_badge

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


def edit_list(label: str, items: list[str], key: str) -> list[str]:
    """One text box per line. Clearing a box removes that line."""
    st.markdown(f"**{label}**")
    values = [st.text_input(f"{label} {n}", value=item, key=f"{key}_{n}", label_visibility="collapsed")
              for n, item in enumerate(items, 1)]
    return [v.strip() for v in values if v.strip()]


# ---------- Tab A: drafts ----------
with tab_drafts:
    flash = st.session_state.get("review_flash")
    if flash:
        st.success(flash)
        if st.button("Open the Ask page as Jordan →"):
            st.session_state.review_flash = None
            st.switch_page("views/ask.py")

    if not drafts:
        if not flash:
            st.info("No drafts waiting. Dave can capture one on the Capture page.")
        for d in sent_back:
            st.markdown(f"{status_badge('sent_back')} &nbsp; {esc(d['job_name'])} ({esc(d['id'])})",
                        unsafe_allow_html=True)
    else:
        if len(drafts) > 1:
            choice = st.selectbox("Draft", drafts, format_func=lambda d: f"{d['job_name']} ({d['id']})")
        else:
            choice = drafts[0]
        d, body, k = choice, choice["body"], choice["id"]

        left, right = st.columns([2, 3], gap="large")
        with left:
            st.subheader("What Dave said")
            st.markdown(f'<div class="transcript">{esc(d["transcript"])}</div>', unsafe_allow_html=True)
            st.caption(f"Recorded by {d['author']} · {nice_date(d['created_at'])}")

        with right:
            st.markdown(f"{status_badge(d['status'])} &nbsp; **{esc(d['id'])}** · author {esc(d['author'])}",
                        unsafe_allow_html=True)
            job_name = st.text_input("Job name", value=d["job_name"], key=f"{k}_job")
            purpose = st.text_area("Purpose", value=body["purpose"], key=f"{k}_purpose", height=80)

            if body["low_confidence"]:
                with st.container(key=f"lowconf_edit_{k}"):
                    low = edit_list("❓ Please confirm (AI was unsure)", body["low_confidence"], f"{k}_low")
            else:
                low = []

            with st.container(key=f"safety_edit_{k}"):
                safety = edit_list("⚠ Safety (kept word for word)", body["safety_notes"], f"{k}_safety")

            steps = edit_list("Steps", body["steps"], f"{k}_steps")
            tools = edit_list("Tools", body["tools"], f"{k}_tools")
            checks = edit_list("Quality checks", body["quality_checks"], f"{k}_checks")
            mistakes = edit_list("Common mistakes", body["common_mistakes"], f"{k}_mistakes")
            st.caption("Every line is editable. Clear a line to remove it.")

            new_body = {"purpose": purpose.strip(), "tools": tools, "steps": steps, "quality_checks": checks,
                        "safety_notes": safety, "common_mistakes": mistakes, "low_confidence": low}

            b1, b2 = st.columns(2)
            if b1.button("✅ Approve and publish", type="primary", width="stretch"):
                db.update_instruction(k, job_name.strip(), new_body)
                db.approve(k, "Priya")
                st.session_state.review_flash = "Approved. Now visible to new hires."
                st.rerun()
            if b2.button("↩ Send back to Dave", width="stretch"):
                db.update_instruction(k, job_name.strip(), new_body)
                db.send_back(k)
                st.session_state.review_flash = "Sent back to Dave with your edits."
                st.rerun()

# ---------- Tab B: approved ----------
with tab_approved:
    st.dataframe(
        [{"ID": a["id"], "Job": a["job_name"], "Author": a["author"], "Approved by": a["approver"],
          "Date": nice_date(a["approved_at"]), "Version": a["version"]} for a in approved],
        hide_index=True, width="stretch",
    )
    for a in approved:
        with st.expander(f"{a['job_name']} ({a['id']})"):
            st.markdown("\n".join(f"{n}. {s}" for n, s in enumerate(a["body"]["steps"], 1)))
            for note in a["body"]["safety_notes"]:
                st.markdown(f"⚠ **Safety:** {note}")

# ---------- Tab C: gaps ----------
with tab_gaps:
    st.subheader("Gaps to capture next")
    st.caption("Questions new hires asked that no approved instruction covers.")
    if not gaps:
        st.success("No open gaps.")
    for g in gaps:
        c1, c2, c3 = st.columns([6, 1.3, 1.3], vertical_alignment="center")
        times = f" · asked {g['times']}×" if g["times"] > 1 else ""
        c1.markdown(f"**{esc(g['question'])}**  \n<small>asked by {esc(g['asked_by'].replace(',', ', '))}{times}</small>",
                    unsafe_allow_html=True)
        c2.write(nice_date(g["asked_at"]))
        if c3.button("Mark covered", key=f"cover_{g['id']}"):
            db.mark_covered(g["question"])
            st.rerun()
