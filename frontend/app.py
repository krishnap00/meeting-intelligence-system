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
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; color: #F8F9FA; }
        .stApp { background: radial-gradient(circle at top left, #1A1A2E, #0A0A0F); background-attachment: fixed; }
        
        /* Glassmorphism Sidebar */
        [data-testid="stSidebar"] { background: rgba(10, 10, 15, 0.8) !important; backdrop-filter: blur(20px); border-right: 1px solid rgba(255,255,255,0.1); }
        .sidebar-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 12px; margin-bottom: 10px; }

        /* CLOUD UPLOAD ZONE STYLING */
        [data-testid="stFileUploadDropzone"] {
            background-color: #1A1A24 !important;
            border: 2px dashed #6366F1 !important;
            border-radius: 20px !important;
            padding: 60px !important;
            text-align: center !important;
        }
        [data-testid="stBaseButton-section"]::before {
            content: url('https://img.icons8.com/ios-filled/50/6366F1/cloud-upload.png');
            display: block; margin-bottom: 20px;
        }
        [data-testid="stBaseButton-section"]::after {
            content: "Drop your transcript here";
            font-size: 24px; font-weight: 700; color: white; display: block; margin-top: 10px;
        }

        /* Tables & Cards */
        .custom-table-container { background: rgba(26, 26, 36, 0.4); backdrop-filter: blur(12px); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); overflow: hidden; margin-top: 20px; }
        .custom-table { width: 100%; border-collapse: collapse; }
        .custom-table th { text-align: left; padding: 18px; color: #94A3B8; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .custom-table td { padding: 18px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.05); }

        header { visibility: hidden; }
        footer { visibility: hidden; }
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
    
    if uploaded_files:
        if st.button("✨ Extract Intelligence", use_container_width=True, type="primary"):
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
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Meetings", len(st.session_state.all_meetings))
    m2.metric("Decisions", sum(len(m["analysis"]["decisions"]) for m in st.session_state.all_meetings.values()))
    m3.metric("Action Items", sum(len(m["analysis"]["action_items"]) for m in st.session_state.all_meetings.values()))

    tab_dec, tab_act, tab_sent, tab_chat = st.tabs(["📌 Decisions", "📋 Action Items", "😊 Sentiment", "💬 Assistant"])

    with tab_dec:
        st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
        table_html = '<table class="custom-table"><thead><tr><th>Decision</th><th>Source</th></tr></thead><tbody>'
        for name, data in st.session_state.all_meetings.items():
            for d in data["analysis"]["decisions"]:
                table_html += f'<tr><td>{d}</td><td class="text-[#94A3B8]">{name}</td></tr>'
        table_html += '</tbody></table></div>'
        st.markdown(table_html, unsafe_allow_html=True)

    with tab_act:
        st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
        table_html = '<table class="custom-table"><thead><tr><th>Who</th><th>What</th><th>Deadline</th></tr></thead><tbody>'
        for name, data in st.session_state.all_meetings.items():
            for item in data["analysis"]["action_items"]:
                table_html += f'<tr><td>{item["who"]}</td><td>{item["what"]}</td><td class="text-[#6366F1]">{item["by_when"]}</td></tr>'
        table_html += '</tbody></table></div>'
        st.markdown(table_html, unsafe_allow_html=True)

    with tab_sent:
        for name, data in st.session_state.all_meetings.items():
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