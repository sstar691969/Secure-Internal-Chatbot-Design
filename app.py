import streamlit as st
from datetime import datetime
import pandas as pd
import json



# ---------- BASIC PAGE CONFIG ----------
st.set_page_config(
    page_title="Sentinel Internal Chatbot Prototype",
    page_icon="💬",
    layout="wide",
)

# ---------- FICTIONAL SENTINEL PLAYERS ----------
SENTINEL_PLAYERS = [
    {
        "number": 1,
        "name": "Marcus Reed",
        "position": "QB",
        "injury": "Right shoulder strain",
        "status": "Day-to-day – limited throws only",
    },
    {
        "number": 22,
        "name": "Devin Cole",
        "position": "RB",
        "injury": "Left hamstring tightness",
        "status": "Limited practice – no full-speed cuts",
    },
    {
        "number": 11,
        "name": "Tyler Brooks",
        "position": "WR",
        "injury": "Concussion (Phase 2)",
        "status": "Non-contact drills only",
    },
    {
        "number": 17,
        "name": "Jalen Ortiz",
        "position": "WR",
        "injury": "Right ankle sprain",
        "status": "Out 1–2 weeks – rehab only",
    },
    {
        "number": 85,
        "name": "Cameron Price",
        "position": "TE",
        "injury": "Rib contusion",
        "status": "No live contact, individual periods only",
    },
    {
        "number": 52,
        "name": "Malik Harris",
        "position": "LB",
        "injury": "Patellar tendinitis (right knee)",
        "status": "Practice reps managed – no back-to-back full days",
    },
    {
        "number": 24,
        "name": "Isaiah Grant",
        "position": "CB",
        "injury": "Groin strain",
        "status": "Day-to-day – avoid long sprints",
    },
    {
        "number": 33,
        "name": "Andre Walker",
        "position": "S",
        "injury": "Fractured right thumb",
        "status": "Club cast – can practice, monitor contact",
    },
    {
        "number": 72,
        "name": "Logan Hayes",
        "position": "LT",
        "injury": "Lower back spasms",
        "status": "Questionable – limited team periods",
    },
    {
        "number": 90,
        "name": "Jordan Fox",
        "position": "DE",
        "injury": "Calf strain",
        "status": "Individual drills only, no full-speed rushes",
    },
    {
        "number": 3,
        "name": "Eli Summers",
        "position": "K",
        "injury": "Right quad strain",
        "status": "Short-range kicks only, no max effort",
    },
    {
        "number": 60,
        "name": "Nate Dawson",
        "position": "C",
        "injury": "Left hand sprain",
        "status": "Full participation with taped support",
    },
]

# ---------- SESSION STATE ----------
if "step" not in st.session_state:
    st.session_state.step = "login"  # login -> mfa -> dashboard/chat

if "user" not in st.session_state:
    st.session_state.user = {
        "username": None,
        "role": None,
        "login_time": None,
    }

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "sender": "system",
            "label": "Sentinel Chatbox",
            "text": (
                "Welcome to the internal Sentinels chat platform. "
                "This demo focuses on a **12-player injury report** use case. "
                "Ask something like “List all injuries” or “Show the injury report.”"
            ),
        }
    ]

if "query_db" not in st.session_state:
    st.session_state.query_db = []

if "query_id_counter" not in st.session_state:
    st.session_state.query_id_counter = 1

# live, editable players list
if "players" not in st.session_state:
    # copy and add last_updated
    st.session_state.players = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    for p in SENTINEL_PLAYERS:
        p_copy = dict(p)
        p_copy["last_updated"] = now_str
        st.session_state.players.append(p_copy)


# ---------- HELPERS ----------
def header_bar():
    with st.container():
        left, right = st.columns([3, 2])
        with left:
            st.markdown(
                """
                <div style="display:flex;align-items:center;gap:10px;">
                  <div style="
                      width:32px;height:32px;border-radius:999px;
                      border:1px solid rgba(255,255,255,0.4);
                      display:flex;align-items:center;justify-content:center;
                      font-weight:700;font-size:14px;
                      color:#FFFFFF;
                  ">
                    WS
                  </div>
                  <div style="font-weight:600;font-size:15px;color:#FFFFFF;">
                    Washington Sentinels | Internal Chatbot Prototype
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with right:
            user = st.session_state.user
            if user["username"]:
                st.markdown(
                    f"""
                    <div style="text-align:right;font-size:12px;color:#D0D7F5;">
                      {user["username"]} &nbsp;|&nbsp; {user["role"] or "Unknown"}<br/>
                      <span>Logged in: {user["login_time"] or ""}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def footer_bar():
    st.markdown(
        """
        <hr style="opacity:0.4;border-color:#2E3650;" />
        <div style="font-size:12px;color:#9CA5D1;text-align:center;">
          Prototype only – no real PHI. Shared chat UI for all roles, with live injury updates when logged in as Team Physician.
        </div>
        """,
        unsafe_allow_html=True,
    )


def switch_step(new_step: str):
    st.session_state.step = new_step


def log_query(question: str, status: str = "new", note: str = "") -> int:
    q_id = st.session_state.query_id_counter
    st.session_state.query_id_counter += 1

    entry = {
        "id": q_id,
        "user": st.session_state.user["username"] or "internal_user",
        "role": st.session_state.user["role"] or "Unknown",
        "question": question,
        "status": status,  # new | reviewed | answered | ignored
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.query_db.append(entry)
    return q_id


def update_last_query(status: str, note: str):
    if not st.session_state.query_db:
        return
    st.session_state.query_db[-1]["status"] = status
    st.session_state.query_db[-1]["note"] = note


def format_injury_report() -> str:
    lines = []
    lines.append("Here’s the current Sentinels injury report (demo data):\n")
    for p in st.session_state.players:
        lines.append(
            f"- **#{p['number']} {p['name']} ({p['position']})**  \n"
            f"  **Injury:** {p['injury']}  \n"
            f"  **Status:** {p['status']}  \n"
            f"  _Last updated: {p['last_updated']}_"
        )
    return "\n".join(lines)


def ai_answer(text: str, role: str) -> str:
    """
    Simple "AI" centered on the injury report use case.
    - When the user asks about injuries / report / roster, it lists all 12 players from live state.
    - Otherwise gives a friendly, role-aware answer.
    """
    lower = text.lower()

    # If user asks for injuries, report, roster, or list
    if any(word in lower for word in ["injury", "injuries", "report", "roster", "list"]):
        report = format_injury_report()

        if role == "Team Physician":
            tail = (
                "\n\nAs Team Physician, you’d be able to update these entries in the real system "
                "directly from this interface (clearing players, changing phases, etc.). "
                "Use the **Live Injury Update** panel below to simulate that in this demo."
            )
        else:
            tail = (
                "\n\nIn the full platform, this view would be filtered based on your role so that "
                "non-clinical staff only see what they’re allowed to see."
            )

        return report + tail

    # General / small talk
    if any(greet in lower for greet in ["hi", "hello", "hey"]):
        return (
            "Hey 👋 This prototype is focused on the **injury report** use case. "
            "Try asking me something like: *“List all injuries”* or *“Show the Sentinels injury report.”*"
        )

    if "what can you do" in lower or "help" in lower:
        return (
            "Right now this demo is centered on an **injury report** use case:\n"
            "- I can list 12 fictional Washington Sentinels players and their current injuries.\n"
            "- Every question you ask is logged into a **query database** for later analysis.\n"
            "- If you’re logged in as Team Physician, you can update injuries live from this screen."
        )

    # Fallback
    return (
        "For this demo, my main job is to show the **injury report** for our 12 fictional Sentinels players. "
        "Try asking: *“List all injuries”* or *“Show the current injury report.”*"
    )


# ---------- SCREENS ----------
def screen_login():
    header_bar()
    st.title("Internal Login", anchor=False)
    st.caption(
        "Single shared platform. Different roles see different levels of detail, "
        "but everyone comes through this front door."
    )

    roles = ["Team Physician", "Athletic Trainer", "Head Coach", "Assistant Coach", "Front Office"]

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="e.g. kkitching")
        role = st.selectbox("Role for this session", roles, index=0)
        password = st.text_input(
            "Password", type="password", placeholder="Demo password (not actually checked)"
        )
        submitted = st.form_submit_button("Sign In")

    if submitted:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            st.session_state.user["username"] = username
            st.session_state.user["role"] = role
            st.session_state.user["login_time"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
            switch_step("mfa")


def screen_mfa():
    header_bar()
    st.title("Multi-Factor Authentication (Simulated)", anchor=False)
    st.caption("In production this would be a real MFA flow. Here we just ask for any 6-digit code.")

    with st.form("mfa_form"):
        code = st.text_input("Verification code", max_chars=6, placeholder="e.g. 123456")
        submitted = st.form_submit_button("Verify & Continue")

    if submitted:
        if not code.isdigit() or len(code) != 6:
            st.error("Enter a valid 6-digit numeric code.")
        else:
            switch_step("dashboard")


def screen_dashboard():
    header_bar()
    role = st.session_state.user["role"] or "Unknown"

    st.subheader("Internal Chatbot Home")
    st.caption(
        f"You’re logged in as **{role}**. This prototype shows how a shared chat UI can drive an "
        "injury-report workflow while still supporting role-based behavior."
    )

    st.info(
        "- All roles: can ask for the 12-player injury report and log questions into the query database.\n"
        "- Team Physician: can also change injuries and statuses live from this screen."
    )

    if st.button("Open Chat", type="primary"):
        st.session_state.step = "chat_screen"

    st.markdown("<hr style='border-color:#2E3650;opacity:0.5;' />", unsafe_allow_html=True)

    if st.session_state.step == "chat_screen":
        screen_chat(embed=True)


def screen_chat(embed: bool = False):
    if not embed:
        header_bar()

    role = st.session_state.user["role"] or "Unknown"

    # Layout: LEFT = previous questions (history), RIGHT = chat + DB + update form
    col_left, col_right = st.columns([1, 3], gap="large")

    # ---------- LEFT: HISTORY LIST ----------
    with col_left:
        st.markdown("#### Previous Questions", unsafe_allow_html=True)
        st.caption("Newest at the top. This is the query database view for the demo.")

        if st.session_state.query_db:
            items = st.session_state.query_db[::-1]  # newest first
            for q in items:
                st.markdown(
                    f"""
                    <div style="
                        font-size:12px;
                        color:#E5E9FF;
                        margin-bottom:6px;
                        padding:6px 8px;
                        border-radius:6px;
                        border:1px solid #38426B;
                        background:rgba(17,24,64,0.9);
                    ">
                      <div style="font-weight:600;">
                        Q{q['id']}
                        <span style="font-weight:400;color:#A0A8D8;">({q['created_at']})</span>
                      </div>
                      <div>{q['question']}</div>
                      <div style="font-size:11px;color:#A0A8D8;margin-top:2px;">
                        status: <strong>{q['status']}</strong>
                        {(" · note: " + q["note"]) if q.get("note") else ""}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div style='color:#E5E9FF;font-size:13px;'>No questions logged yet. As you chat, they’ll show up here.</div>",
                unsafe_allow_html=True,
            )

    # ---------- RIGHT: CHAT + INPUT + GUIDED DB UPDATE + INJURY FORM ----------
    with col_right:
        st.markdown("#### Chat", unsafe_allow_html=True)
        st.caption(
            "Ask general questions or ask for the full injury report. I’ll answer differently depending on your role."
        )

        # Chat window
        chat_box = st.container()
        with chat_box:
            for msg in st.session_state.chat_history:
                if msg["sender"] == "user":
                    align = "flex-end"
                    bg = "linear-gradient(135deg,#4C6FFF,#9F7AEA)"  # bright gradient
                    border = "rgba(255,255,255,0.1)"
                    text_color = "#FFFFFF"
                elif msg["sender"] == "system":
                    align = "flex-start"
                    bg = "#1A2340"
                    border = "#3D4973"
                    text_color = "#E5E9FF"
                else:  # bot
                    align = "flex-start"
                    bg = "#151B34"
                    border = "#3D4973"
                    text_color = "#F7FAFF"

                st.markdown(
                    f"""
                    <div style="display:flex;justify-content:{align};margin-bottom:8px;">
                      <div style="max-width:80%;">
                        <div style="font-size:11px;color:#A0A8D8;text-transform:uppercase;margin-bottom:2px;">
                          {msg["label"]}
                        </div>
                        <div style="
                            padding:10px 14px;
                            border-radius:12px;
                            background:{bg};
                            font-size:13px;
                            white-space:pre-wrap;
                            border:1px solid {border};
                            color:{text_color};
                        ">
                          {msg["text"]}
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Bottom input bar
        st.markdown("<hr style='border-color:#2E3650;opacity:0.6;' />", unsafe_allow_html=True)
        left_bar, center_bar, right_bar = st.columns([0.6, 4, 0.8])

        with left_bar:
            st.button("+", help="(Prototype) Attach context / template")

        with center_bar:
            with st.form("chat_form"):
                user_text = st.text_input(
                    "",
                    key="chat_input",
                    placeholder="Try: 'List all injuries' or 'Show the injury report'…",
                    label_visibility="collapsed",
                )
                send = st.form_submit_button("Send")

        with right_bar:
            st.write("")
            st.markdown(
                "<div style='font-size:16px;color:#A0A8D8;margin-top:4px;'>••</div>",
                unsafe_allow_html=True,
            )

        if send and user_text.strip():
            question = user_text.strip()

            # append user message
            st.session_state.chat_history.append(
                {"sender": "user", "label": "You", "text": question}
            )

            # AI answer with role awareness
            answer = ai_answer(question, role)
            st.session_state.chat_history.append(
                {"sender": "bot", "label": "Chatbox", "text": answer}
            )

            # record into query DB as "new"
            log_query(question, status="new", note="")

            st.rerun()

        # Guided DB update (for the latest question)
        st.markdown("### Guided Database Update (latest question)", unsafe_allow_html=True)
        if st.session_state.query_db:
            last = st.session_state.query_db[-1]
            st.markdown(
                f"<div style='color:#F7FAFF;font-size:13px;'><strong>Last question (Q{last['id']}):</strong> {last['question']}</div>",
                unsafe_allow_html=True,
            )

            col_status, col_note = st.columns([1.2, 2])

            with col_status:
                new_status = st.selectbox(
                    "Mark this as:",
                    ["new", "reviewed", "answered", "ignored"],
                    index=["new", "reviewed", "answered", "ignored"].index(last["status"]),
                    key="guided_status",
                )

            with col_note:
                new_note = st.text_input(
                    "Internal note (optional)",
                    value=last.get("note", ""),
                    key="guided_note",
                    placeholder="e.g. 'Good candidate for future FAQ entry.'",
                )

            if st.button("Save to query database"):
                update_last_query(new_status, new_note)
                st.success("Saved. The history list on the left is now updated.")
        else:
            st.info("Once you ask something, I’ll walk you through how we log it.")

        # Live Injury Update form (Team Physician only)
        st.markdown("### Live Injury Update (Team Physician only)", unsafe_allow_html=True)
        if role == "Team Physician":
            players = st.session_state.players
            labels = [f"#{p['number']} {p['name']} ({p['position']})" for p in players]
            selected_label = st.selectbox(
                "Select player to update",
                labels,
                index=0,
            )
            idx = labels.index(selected_label)
            player = players[idx]

            col_inj, col_status = st.columns(2)
            with col_inj:
                new_injury = st.text_input(
                    "Injury description",
                    value=player["injury"],
                    key=f"inj_{idx}",
                )
            with col_status:
                new_status_text = st.text_area(
                    "Status / availability",
                    value=player["status"],
                    key=f"status_{idx}",
                    height=80,
                )

            if st.button("Save Injury Update", key=f"save_{idx}"):
                player["injury"] = new_injury
                player["status"] = new_status_text
                player["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.players[idx] = player

                # Let the chat know we updated
                summary = (
                    f"Updated injury report for **#{player['number']} {player['name']} ({player['position']})**:\n\n"
                    f"- **Injury:** {player['injury']}\n"
                    f"- **Status:** {player['status']}\n"
                    f"_Last updated: {player['last_updated']}_"
                )
                st.session_state.chat_history.append(
                    {"sender": "bot", "label": "Chatbox", "text": summary}
                )

                # log as a query-style event
                log_query(
                    f"Doctor updated injury for #{player['number']} {player['name']}.",
                    status="answered",
                    note="Live injury update performed in demo UI.",
                )

                st.success("Injury updated. Ask for the injury report again to see the change.")
                st.rerun()
        else:
            st.info(
                "Live medical data updates are restricted. Log in as Team Physician to simulate changing injuries in real time."
            )

        # Optional: full DB table for demo
        with st.expander("View full query database (demo)", expanded=False):
            if st.session_state.query_db:
                df = pd.DataFrame(st.session_state.query_db)
                st.dataframe(df, use_container_width=True)

                json_data = json.dumps(st.session_state.query_db, indent=2)
                st.download_button(
                    "Download as JSON",
                    data=json_data,
                    file_name="query_db.json",
                    mime="application/json",
                )
            else:
                st.write("No entries yet.")


# ---------- ROUTER ----------
def main():
    # Dark, high-contrast styling
    st.markdown(
        """
        <style>
          body {
            background-color: #050814;
            color:#F7FAFF;
          }
          .stApp {
            background: radial-gradient(circle at top left,#151A30,#050814);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    step = st.session_state.step

    if step == "login":
        screen_login()
    elif step == "mfa":
        screen_mfa()
    elif step in ("dashboard", "chat_screen"):
        screen_dashboard()
    else:
        screen_login()

    footer_bar()


if __name__ == "__main__":
    main()