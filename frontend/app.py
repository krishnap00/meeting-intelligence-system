import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API_URL = "http://localhost:8000"

# --- 1. DYNAMIC PATH RESOLUTION ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from models.processor import load_transcripts

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Meeting Intelligence Hub", layout="wide")

# --- 3. GOOGLE AUTHENTICATION ---
# REPLACE THESE WITH YOUR ACTUAL CREDENTIALS FROM GOOGLE CONSOLE

st.session_state.connected = True
st.session_state.user_info = {"name": "Demo User"}

if not st.session_state.get('connected'):
    st.markdown('<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh;">', unsafe_allow_html=True)
    st.title("🧠 Meeting Intelligence Hub")
    st.write("Please sign in to access your dashboard.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. THE "SAAS" VISUAL ENGINE (CSS) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        html, body { font-family: 'Sora', sans-serif !important; color: #F8F9FA; }
        .stApp {
            background:
                linear-gradient(rgba(10,10,15,0.85), rgba(10,10,15,0.95)),
                url("https://images.unsplash.com/photo-1556761175-4b46a572b786");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }       
        /* Keep your card, sidebar, tables, etc. styles here */
    </style>
""", unsafe_allow_html=True)

# --- 5. SESSION STATE ---
if 'all_meetings' not in st.session_state:
    st.session_state.all_meetings = {}

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"**User:** {st.session_state['user_info'].get('name')}")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    st.markdown("---")
    st.markdown('<div class="text-2xl font-bold mb-6 text-white">Meeting <span class="text-[#6366F1]">Hub</span></div>', unsafe_allow_html=True)
    
    # Checkbox to trigger new uploads from sidebar if needed
    st.markdown('<div class="mt-10 mb-4 text-[#94A3B8] text-[11px] font-bold tracking-widest uppercase">Meeting History</div>', unsafe_allow_html=True)
    for name in st.session_state.all_meetings.keys():
        st.markdown(f'<div class="sidebar-item"><div class="text-[13px] font-semibold text-white">{name}</div></div>', unsafe_allow_html=True)

# --- 7. MAIN CONTENT ---
if not st.session_state.all_meetings:
    # THE CLOUD UPLOAD SCREEN (EMPTY STATE)
    st.markdown('<div style="margin-top: 50px;"></div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("", type=["txt", "vtt"], accept_multiple_files=True)
    
    # --- 🎙️ AUDIO UPLOAD ---
    st.markdown("### 🎙 Upload Meeting Audio (Optional)")

    audio_file = st.file_uploader("Upload meeting audio", type=["mp3", "wav"])

    if audio_file:
        st.info("🎧 Audio uploaded (transcription feature can be added)")

    # --- HERO SECTION (ADVANCED) ---
    # HERO SECTION
    st.markdown("""
    <div class="hero">
        <div class="hero-bg" style="text-align:center;">
            <h1 style="font-size: 48px; font-weight: 700; color: white;">
                Turn Meetings into Actionable Intelligence
            </h1>

            <p style="font-size: 18px; color: #CBD5F5; margin-top: 10px;">
                Extract decisions, action items, and insights — instantly.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # STREAMLIT BUTTONS BELOW HTML
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Get Started"):
            st.info("Get Started clicked")
    with col2:
        if st.button("▶ Watch Demo"):
            st.info("Watch Demo clicked")
    


    if uploaded_files:
        if st.button("✨ Extract Intelligence", use_container_width=True):
            with st.spinner("Analyzing..."):
                transcripts = load_transcripts(uploaded_files)
                for name, content in transcripts.items():
                    try:
                        response = requests.post(
                            f"{API_URL}/analyze",
                            json={"text": content}
                        )

                        if response.status_code != 200:
                            st.error(f"Backend error: {response.text}")
                            st.stop()

                        data = response.json()

                        analysis = data["analysis"]
                        sentiment = data["sentiment"]

                        st.session_state.all_meetings[name] = {
                            "content": content,
                            "analysis": analysis,
                            "sentiment": sentiment
                        }

                    except Exception as e:
                        st.error(f"Connection error: {e}")
                        st.stop()
            st.rerun()
else:
    # THE DASHBOARD (DATA STATE)
    st.markdown('<h1 class="text-3xl font-bold mb-1 text-white">Intelligence Dashboard</h1>', unsafe_allow_html=True)
    
        # --- 🔍 SEARCH / FILTER FEATURE ---
    st.markdown("### 🔍 Search Meetings")

    search_query = st.text_input("Search decisions or action items")

    if search_query:
        filtered_meetings = {}
        for name, data in st.session_state.all_meetings.items():

            decisions = [d for d in data["analysis"]["decisions"] if search_query.lower() in d.lower()]
            actions = [a for a in data["analysis"]["action_items"] if search_query.lower() in a["what"].lower()]

            if decisions or actions:
                filtered_meetings[name] = {
                    "analysis": {
                        "decisions": decisions,
                        "action_items": actions
                    },
                    "content": data["content"],
                    "sentiment": data["sentiment"]
                }

        display_data = filtered_meetings
    else:
        display_data = st.session_state.all_meetings

    for name, data in display_data.items():
        st.markdown(f"### 📝 Summary — {name}")
        st.write(data["analysis"]["summary"])

    m1, m2, m3 = st.columns(3)
    st.markdown("<br>", unsafe_allow_html=True)

    m1.metric("Meetings", len(display_data))
    m2.metric("Decisions", sum(len(m["analysis"]["decisions"]) for m in display_data.values()))
    m3.metric("Action Items", sum(len(m["analysis"]["action_items"]) for m in display_data.values()))


    tab_dec, tab_act, tab_sent, tab_chat = st.tabs(["📌 Decisions", "📋 Action Items", "😊 Sentiment", "💬 Assistant"])

    with tab_dec:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)

        for name, data in display_data.items():
            for d in data["analysis"]["decisions"]:

                col1, col2 = st.columns([5,1])

                with col1:
                    st.markdown(f"""
                    <div class="card fade-in">
                        <div class="card-title">{d}</div>
                        <div class="card-sub">{name}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("Explain", key=f"{name}-{d}"):
                        response = requests.post(
                            f"{API_URL}/explain",
                            json={
                                "decision": d,
                                "context": data["content"]
                            }
                        )
                        explanation = response.json()["explanation"]
                        st.info(explanation)


    with tab_act:
        for name, data in display_data.items():
            for item in data["analysis"]["action_items"]:

                st.markdown(f"""
                <div class="card fade-in">
                    <div class="card-title">{item["what"]}</div>
                    <div class="card-sub">
                        👤 {item["who"]} | ⏳ {item["by_when"]} | 📁 {name}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # --- CSV DOWNLOAD ---
        all_items = []
        for name, data in display_data.items():
            for item in data["analysis"]["action_items"]:
                item_copy = item.copy()
                item_copy["meeting"] = name
                all_items.append(item_copy)

        if all_items:
            df = pd.DataFrame(all_items)
            st.download_button(
                "📥 Download Action Items (CSV)",
                df.to_csv(index=False),
                file_name="action_items.csv",
                mime="text/csv"
            )

    with tab_sent:
        for name, data in display_data.items():
            st.write(f"**Participation for {name}**")
            df_sent = pd.DataFrame(list(data["sentiment"].items()), columns=["Speaker", "Sentiment"])
            fig = px.pie(df_sent, names="Speaker", hole=0.5)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=300)
            st.plotly_chart(fig, use_container_width=True)

    with tab_chat:
        user_q = st.text_input("Ask a question about these meetings...")
        if user_q:
            all_txt = "\n\n".join([v['content'] for v in st.session_state.all_meetings.values()])
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "question": user_q,
                        "context": all_txt
                    }
                )

                if response.status_code != 200:
                    st.error(f"Chatbot error: {response.text}")
                    st.stop()

                ans = response.json()["answer"]

            except Exception as e:
                st.error(f"Chat connection error: {e}")
                st.stop()
            st.markdown(f'<div style="background: #1A1A24; padding: 20px; border-radius: 10px; border-left: 5px solid #6366F1;">{ans}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 💬 Feedback")

feedback = st.text_area("Share your thoughts")

col1, col2 = st.columns(2)

with col1:
    rating = st.slider("Rate the app", 1, 5, 4)

with col2:
    category = st.selectbox("Category", ["UI", "Bug", "Feature Request", "Other"])

if st.button("Submit Feedback"):
    with open("feedback.txt", "a") as f:
        f.write(f"Rating: {rating}\nCategory: {category}\nFeedback: {feedback}\n---\n")
    st.success("Thanks! 🚀")