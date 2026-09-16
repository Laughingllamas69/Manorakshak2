"""
ManoRakshak (मनोरक्षक) — Mental Health & Wellness Support Portal
For Police Personnel & Armed Forces

Updated to use Local Ollama AI and expanded to 15 questions.
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import streamlit as st
import ollama

try:
    from app_ui import inject_css, hero_header
except ImportError:
    st.error("Error: 'app_ui.py' module not found. Please ensure it exists in the same directory.")
    st.stop()


DB_PATH = "manorakshak.db"
APP_TITLE = "ManoRakshak | मनोरक्षक"
APP_SUBTITLE = "Confidential Mental Wellness Support for Police & Armed Forces Personnel"

DEPARTMENTS = [
    "State Police", "CRPF", "BSF", "CISF", "ITBP", "SSB",
    "Indian Army", "Indian Navy", "Indian Air Force", "Other / Prefer not to say",
]

HELPLINES = [
    {"name": "Tele-MANAS (Govt. of India Mental Health Helpline)", "number": "14416"},
    {"name": "KIRAN Mental Health Helpline (Ministry of Social Justice)", "number": "1800-599-0019"},
    {"name": "iCall Psychosocial Helpline (TISS)", "number": "9152987821"},
    {"name": "Department In-house Peer Support Cell", "number": "Contact your unit welfare officer"},
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            department TEXT,
            timestamp TEXT NOT NULL,
            total_score INTEGER NOT NULL,
            category TEXT NOT NULL,
            responses TEXT,
            ai_recommendation TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_assessment(user_id, department, total_score, category, responses_dict, ai_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assessments (user_id, department, timestamp, total_score, category, responses, ai_recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            department,
            datetime.now().isoformat(timespec="seconds"),
            total_score,
            category,
            json.dumps(responses_dict, ensure_ascii=False),
            ai_text,
        ),
    )
    conn.commit()
    conn.close()


def get_user_history(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM assessments WHERE user_id = ? ORDER BY timestamp ASC",
        conn,
        params=(user_id,),
    )
    conn.close()
    return df


def get_all_assessments():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM assessments ORDER BY timestamp ASC", conn)
    conn.close()
    return df


def hash_pseudonym(raw_id: str) -> str:
    raw_id = raw_id.strip().lower()
    return "OFC-" + hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:10].upper()


ANSWER_SCALE = [
    "Not at all",
    "Several days",
    "More than half the days",
    "Nearly every day",
]

QUESTIONS = [
    {
        "id": "q1",
        "text": "Little interest or pleasure in doing things you'd normally enjoy, on or off duty",
        "domain": "Mood",
    },
    {
        "id": "q2",
        "text": "Feeling down, low, or hopeless",
        "domain": "Mood",
    },
    {
        "id": "q3",
        "text": "Feeling nervous, anxious, or 'on edge'",
        "domain": "Anxiety",
    },
    {
        "id": "q4",
        "text": "Not being able to stop or control worrying",
        "domain": "Anxiety",
    },
    {
        "id": "q5",
        "text": "Trouble falling or staying asleep due to shift timings or a racing mind",
        "domain": "Sleep / Fatigue",
    },
    {
        "id": "q6",
        "text": "Unwanted memories, flashbacks, or distress linked to an incident on duty",
        "domain": "Trauma Exposure",
    },
    {
        "id": "q7",
        "text": "Feeling isolated or disconnected from family and friends because of work",
        "domain": "Isolation",
    },
    {
        "id": "q8",
        "text": "Feeling unusually irritable, quick to anger, or constantly 'on guard' even off duty",
        "domain": "Hypervigilance",
    },
    {
        "id": "q9",
        "text": "Feeling emotionally numb or finding it hard to feel positive emotions",
        "domain": "Emotional Suppression",
    },
    {
        "id": "q10",
        "text": "Physical exhaustion affecting your alertness, focus, or performance on duty",
        "domain": "Burnout",
    },
    {
        "id": "q11",
        "text": "Relying on alcohol, tobacco, or other substances to cope with stress or sleep",
        "domain": "Substance Use",
    },
    {
        "id": "q12",
        "text": "Difficulty concentrating or making decisions, even on simple tasks",
        "domain": "Cognitive Function",
    },
    {
        "id": "q13",
        "text": "Feeling guilty about past actions or inactions during an incident",
        "domain": "Guilt / Moral Injury",
    },
    {
        "id": "q14",
        "text": "Difficulty trusting colleagues or feeling unsupported by your team",
        "domain": "Team Dynamics",
    },
    {
        "id": "q15",
        "text": "Physical symptoms like headaches, stomach issues, or muscle tension without a clear medical cause",
        "domain": "Psychosomatic",
    },
]

MAX_SCORE = len(QUESTIONS) * 3
# Adjusted thresholds for 15 questions (Max 45)
# 0-10: Low, 11-21: Moderate, 22-33: High, 34+: Critical
SCORE_CATEGORIES = [
    (0, 10, "Low Stress", "🟢"),
    (11, 21, "Moderate Fatigue", "🟡"),
    (22, 33, "High Burnout", "🟠"),
    (34, MAX_SCORE, "Critical Distress", "🔴"),
]


def score_to_category(total_score: int):
    for low, high, label, emoji in SCORE_CATEGORIES:
        if low <= total_score <= high:
            return label, emoji
    return "Unknown", "⚪"


SOP_RESETS = [
    "**Box Breathing (Tactical Reset):** Inhale 4s → Hold 4s → Exhale 4s → Hold 4s. Repeat 4–6 cycles before/after a high-stress call.",
    "**Post-Shift Decompression:** Take 10 minutes in the vehicle/locker room before driving home — change out of uniform mentally, not just physically.",
    "**5-4-3-2-1 Grounding:** Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste — use during acute stress spikes.",
    "**Sleep Hygiene for Rotating Shifts:** Blackout curtains, no screens 30 min before sleep, consistent wind-down ritual regardless of shift time.",
    "**Peer Check-In Protocol:** After a critical incident, a structured 10-minute peer debrief within 24–72 hours significantly reduces long-term impact.",
]

def get_ollama_response(system_prompt: str, user_prompt: str) -> str | None:
    """Call Ollama local server. Returns text or None on failure."""
    try:
        # Configure model name. Ensure you have pulled this model (e.g., ollama pull llama3)
        model_name = "llama3" 
        
        # Construct the full prompt
        full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"

        # Generate response
        response = ollama.chat(
            model=model_name,
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt,
                },
                {
                    'role': 'user',
                    'content': user_prompt,
                },
            ]
        )
        
        if response and response['message'] and response['message']['content']:
            return response['message']['content'].strip()
        else:
            print("Ollama returned empty response.")
            return None

    except Exception as e:
        print(f"Ollama Error: {e}. Ensure Ollama is running (ollama serve) and the model is pulled.")
        return None


RAKSHAK_SAHAYAK_PERSONA = """
You are "Rakshak Sahayak", a warm, confidential, trauma-informed debriefing
companion built specifically for Indian police and armed forces personnel.

Your tone: respectful, calm, non-clinical, never condescending. You address
the officer as a professional who serves under real operational stress —
never as a "patient". You NEVER diagnose. You validate their service and
their feelings, then offer 2-3 concrete, actionable grounding or
tactical-reset techniques (e.g. box breathing, grounding exercises,
post-shift decompression routines). Keep the response under 220 words,
in plain conversational English (a few Hindi words like "himmat" or
"seva" are welcome if natural, but do not overdo it).

If the distress category is "Critical Distress", gently and non-alarmingly
encourage them to reach out to a confidential helpline or their peer
support contact, and mention that reaching out is a sign of operational
readiness, not weakness. Do not be preachy about this — one sentence is enough.
"""

def build_debrief_prompt(category: str, responses: dict) -> str:
    """Build the prompt from category + top 3 concerns."""
    scored_items = []
    for q in QUESTIONS:
        q_id = q["id"]
        if q_id in responses:
            score_val = responses[q_id]
            if isinstance(score_val, dict):
                score_val = score_val.get("score", 0)
            
            scored_items.append({
                "question": q["text"],
                "domain": q["domain"],
                "score": score_val
            })
    
    scored_items.sort(key=lambda x: x["score"], reverse=True)
    top_concerns = scored_items[:3]

    concerns_list = []
    for item in top_concerns:
        score_val = item['score']
        label = ANSWER_SCALE[score_val] if score_val < len(ANSWER_SCALE) else "Unknown"
        concerns_list.append(f"- {item['domain']}: \"{item['question']}\" — reported as \"{label}\"")
    
    concerns_text = "\n".join(concerns_list)

    prompt = f"""{RAKSHAK_SAHAYAK_PERSONA}

An officer has just completed a confidential wellness screener.
Overall result category: {category}

Their top reported challenge areas:
{concerns_text}

Write their confidential debrief now, addressed directly to them ("you").
"""
    return prompt


def get_ai_debrief(category: str, responses: dict) -> str:
    """
    Calls the Ollama server. If it fails, returns the offline template.
    """
    prompt = build_debrief_prompt(category, responses)
    
    ai_response = get_ollama_response(RAKSHAK_SAHAYAK_PERSONA, prompt)
    
    if ai_response and len(ai_response) > 10:
        return ai_response
    
    return _offline_debrief(category)


def _offline_debrief(category: str) -> str:
    templates = {
        "Low Stress": (
            "Your readings look steady today — that's good, and it's worth "
            "acknowledging the discipline it takes to maintain that under duty "
            "pressure. Keep your routine: box breathing before high-stress calls, "
            "consistent sleep, and regular check-ins with your peers. Steady as she goes."
        ),
        "Moderate Fatigue": (
            "What you're carrying is real — shift work and duty pressure add up "
            "even when everything looks fine on the surface. Try box breathing "
            "(4s in, 4s hold, 4s out, 4s hold) before and after high-intensity calls, "
            "and protect a wind-down window before sleep. Small resets, done "
            "consistently, prevent bigger dips later."
        ),
        "High Burnout": (
            "Thank you for your service, and thank you for being honest here — "
            "that honesty takes real courage. What you're experiencing sounds like "
            "genuine burnout, not weakness. Try the 5-4-3-2-1 grounding technique "
            "during acute moments, and consider a structured peer check-in this week. "
            "You don't have to carry this alone."
        ),
        "Critical Distress": (
            "First — thank you for trusting this space with something difficult. "
            "What you're describing deserves real support, not just a breathing "
            "exercise. Please consider reaching out to Tele-MANAS (14416) or the "
            "KIRAN helpline (1800-599-0019) today — confidentially, and on your terms. "
            "Reaching out is operational readiness, not a weakness. You've carried a lot; "
            "you don't have to carry it alone."
        ),
    }
    return templates.get(category, "Thank you for completing your check-in. Take a moment to breathe.")


st.set_page_config(
    page_title="ManoRakshak",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()
inject_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = ""
if "department" not in st.session_state:
    st.session_state.department = ""

with st.sidebar:
    st.markdown("## 🛡️ ManoRakshak")
    st.caption(APP_SUBTITLE)
    st.divider()

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Confidential Check-In")
        st.caption(
            "Use a badge number, service number, or any pseudonym you like. "
            "Your identity is one-way hashed before storage — nobody, "
            "including admins, can reverse it back to your real identity."
        )
        raw_id = st.text_input("Badge Number / Pseudonym", placeholder="e.g. Falcon-07")
        dept = st.selectbox("Department / Force", DEPARTMENTS)

        if st.button("🔓 Enter Confidentially", use_container_width=True, type="primary"):
            if raw_id.strip():
                st.session_state.user_id = hash_pseudonym(raw_id)
                st.session_state.department = dept
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.warning("Please enter a badge number or pseudonym to continue.")
    else:
        st.success(f"Signed in as **{st.session_state.user_id}**")
        st.caption(f"Department: {st.session_state.department}")
        
        if st.button("🚪 End Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ["logged_in", "user_id", "department"]:
                    del st.session_state[key]
                
                st.session_state.logged_in = False
                st.session_state.user_id = ""
                st.session_state.department = ""
                st.rerun()

    st.divider()
    st.markdown("#### 🚨 In Crisis Right Now?")
    for h in HELPLINES:
        st.markdown(f"**{h['name']}**  \n📞 {h['number']}")

st.title("🛡️ ManoRakshak (मनोरक्षक)")
st.caption(APP_SUBTITLE)

if not st.session_state.logged_in:
    hero_header(
        "ManoRakshak",
        "A confidential wellness check-in for police and armed forces personnel. "
        "Two minutes. No names. No service record.",
        chips=[
            "🔒 Identity one-way hashed",
            "🇮🇳 Tele-MANAS 14416 always one click away",
            "📊 Command sees averages, never individuals",
        ],
    )

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("#### Begin your check-in")
        st.caption(
            "Use a badge number, service number, or any pseudonym you like. "
            "It is hashed before it touches the database — admins cannot reverse it."
        )
        with st.form("checkin_form"):
            raw_id = st.text_input(
                "Badge number or pseudonym", placeholder="e.g. Falcon-07"
            )
            dept = st.selectbox("Department / Force", DEPARTMENTS)
            go = st.form_submit_button(
                "Enter confidentially  →",
                use_container_width=True,
                type="primary",
            )
        if go and raw_id.strip():
            st.session_state.user_id = hash_pseudonym(raw_id)
            st.session_state.department = dept
            st.session_state.logged_in = True
            st.rerun()
        elif go:
            st.warning("Please enter a badge number or pseudonym to continue.")

    with right:
        st.markdown("#### If you're in crisis right now")
        st.markdown(
            """
            <div class="mr-crisis">
              You do not need to complete a check-in to get help.<br><br>
              <b>Tele-MANAS</b> &nbsp;·&nbsp; 14416 &nbsp;(24×7, free)<br>
              <b>KIRAN</b> &nbsp;·&nbsp; 1800-599-0019<br>
              <b>iCall (TISS)</b> &nbsp;·&nbsp; 9152987821
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Available in 20+ Indian languages. Confidential.")

    st.stop()

tab_assess, tab_dashboard, tab_admin = st.tabs(
    [
        "📝 Wellness Screener",
        "📊 My Dashboard & Resources",
        "🔐 Command Analytics (Admin)",
    ]
)

with tab_assess:
    st.markdown("### Confidential Duty Wellness Check-In")
    st.caption("Over the **last 2 weeks**, how often have you been bothered by any of the following?")

    
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    

    if not st.session_state.get("processing"):
        current_q = st.session_state.q_index
        total_q = len(QUESTIONS)
        progress = current_q / total_q
        
        c1, c2 = st.columns([4, 1])
        c1.progress(progress, text=f"Question {current_q + 1} of {total_q}")
        
        if current_q > 0:
            c2.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back", use_container_width=True):
                st.session_state.q_index -= 1
                st.rerun()

        q = QUESTIONS[current_q]
        
        st.markdown(
            f"""
            <div class="mr-qcard">
              <div class="mr-domain">{q['domain']}</div>
              <div class="mr-qtext">{q['text']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        answer = st.radio(         
            "How often...",
            options=list(range(4)),
            format_func=lambda i: ANSWER_SCALE[i],
            index=None,
            key=f"q_{q['id']}",
            label_visibility="collapsed",
        )

        n1, n2 = st.columns([1, 3])

        if answer is None:
            n1.button(
                "Finish" if current_q == total_q - 1 else "Next →",
                type="secondary",
                use_container_width=True,
                disabled=True,
            )
        else:
            if n1.button(
                "Finish" if current_q == total_q - 1 else "Next →",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.answers[q["id"]] = answer

                if current_q < total_q - 1:
                    st.session_state.q_index += 1
                    st.rerun()
                else:
                    st.session_state.processing = True
                    st.rerun()

    
    if st.session_state.get("processing"):
        
        total_score = sum(v for v in st.session_state.answers.values() if v is not None)
        category, emoji = score_to_category(total_score)

       
        ai_input = {
            q["id"]: {
                "question": q["text"],
                "domain": q["domain"],
                "score": st.session_state.answers[q["id"]]
            }
            for q in QUESTIONS
        }

        
        with st.spinner("Rakshak Sahayak is preparing your confidential debrief..."):
            ai_text = get_ai_debrief(category, ai_input)

        
        save_assessment(
            st.session_state.user_id,
            st.session_state.department,
            total_score,
            category,
            ai_input,
            ai_text,
        )

        
        st.session_state.processing = False

        
        st.divider()
        st.markdown(f"## {emoji} Your Result: **{category}**")
        st.progress(min(total_score / MAX_SCORE, 1.0))
        st.caption(f"Score: {total_score} / {MAX_SCORE}")

        st.markdown("### 🤝 A Message from Rakshak Sahayak")
        st.markdown(
            f'<div class="mr-letter">{ai_text}</div><div class="sig">— Rakshak Sahayak</div>',
            unsafe_allow_html=True,
        )

        if category == "Critical Distress":
            st.error(
                "⚠️ Your responses suggest you may be going through a significant "
                "amount of distress. Please consider reaching out to a confidential "
                "helpline listed in the sidebar, or your unit's peer support contact. "
                "You do not have to face this alone."
            )

        st.success("This check-in has been saved to your private wellness trend.")

        
        b1, b2 = st.columns(2)
        if b1.button("🔄 Take check-in again", use_container_width=True):
            st.session_state.answers = {}
            st.session_state.q_index = 0
            st.rerun()
        if b2.button("📊 Go to my dashboard", use_container_width=True):
            st.session_state.answers = {}
            st.session_state.q_index = 0
            st.rerun()

with tab_dashboard:
    
    if not st.session_state.logged_in:
        st.warning("Please log in to view your dashboard.")
        st.stop()

    st.subheader("📈 Your Wellness Trend")

    history_df = get_user_history(st.session_state.user_id)

    if history_df.empty:
        st.info("No check-ins yet. [Complete a screener →](#tab_assess)")
    else:
        history_df["timestamp"] = pd.to_datetime(history_df["timestamp"])
        chart_df = history_df.set_index("timestamp")[["total_score"]].rename(
            columns={"total_score": "Stress Score"}
        )
        st.line_chart(chart_df, height=300)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Check-ins", len(history_df))
        col2.metric("Latest Score", int(history_df.iloc[-1]["total_score"]), help=f"out of {MAX_SCORE}")
        col3.metric("Latest Category", history_df.iloc[-1]["category"])

        with st.expander("📋 View full check-in history"):
            display_df = history_df[["timestamp", "total_score", "category"]].rename(
                columns={"timestamp": "Date/Time", "total_score": "Score", "category": "Category"}
            )
            st.dataframe(display_df.sort_values("Date/Time", ascending=False), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("🧰 Shift Reset Resource Bank")
    for tip in SOP_RESETS:
        st.markdown(f"- {tip}")

    st.divider()
    st.subheader("📞 Crisis & Peer Support Directory")
    hc1, hc2 = st.columns(2)
    for i, h in enumerate(HELPLINES):
        col = hc1 if i % 2 == 0 else hc2
        col.markdown(f"**{h['name']}**  \n📞 `{h['number']}`")

with tab_admin:
    st.subheader("🔐 Command-Level Wellness Analytics")
    st.caption(
        "Password-protected, aggregate-only view. Individual identities are "
        "never shown here — only unit-level patterns, to support proactive "
        "welfare planning without compromising any single officer's privacy."
    )

    admin_password = st.text_input("Admin Password", type="password", key="admin_pw")

    
    if "ADMIN_PASSWORD" not in st.secrets:
        st.error("⚠️ Admin access requires a password to be configured in `secrets.toml`. Contact the system administrator.")
        st.stop()
    
    
    try:
        expected_password = st.secrets.get("ADMIN_PASSWORD")
    except Exception:
        st.error("Admin password not found in secrets.toml.")
        st.stop()

    if admin_password == "":
        st.info("Enter the admin password to view aggregate analytics.")
    elif admin_password != expected_password:
        st.error("Incorrect password.")
    else:
        all_df = get_all_assessments()

        if all_df.empty:
            st.info("No screenings recorded yet.")
        else:
            st.success("Access granted — showing anonymized aggregate data only.")

            total_screenings = len(all_df)
            unique_officers = all_df["user_id"].nunique()
            high_risk_pct = (
                all_df["category"].isin(["High Burnout", "Critical Distress"]).mean() * 100
            )
            low_risk_pct = (all_df["category"] == "Low Stress").mean() * 100

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Screenings", total_screenings)
            m2.metric("Unique Anonymous Officers", unique_officers)
            m3.metric("% High Burnout / Critical", f"{high_risk_pct:.1f}%")
            m4.metric("% Low Stress", f"{low_risk_pct:.1f}%")

            st.divider()
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("#### Category Distribution")
                cat_counts = all_df["category"].value_counts()
                st.bar_chart(cat_counts)

            with col_b:
                st.markdown("#### Average Score by Department")
                dept_avg = all_df.groupby("department")["total_score"].mean().sort_values(ascending=False)
                st.bar_chart(dept_avg)

            st.divider()
            st.markdown("#### Screenings Over Time")
            all_df["timestamp"] = pd.to_datetime(all_df["timestamp"])
            all_df["date"] = all_df["timestamp"].dt.date
            daily_counts = all_df.groupby("date").size()
            st.line_chart(daily_counts)

            with st.expander("📋 Raw anonymized records (no names, badge numbers hashed)"):
                safe_cols = ["user_id", "department", "timestamp", "total_score", "category"]
                st.dataframe(all_df[safe_cols], use_container_width=True, hide_index=True)
