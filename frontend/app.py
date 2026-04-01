# frontend/app.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from models.processor import load_transcripts, extract_decisions_actions, analyze_sentiment, chatbot_response

st.set_page_config(page_title="Meeting Intelligence System", layout="wide")

st.title("Meeting Intelligence System")
st.subheader("Upload one or more transcripts")

# 1. Upload transcripts
uploaded_files = st.file_uploader("Choose transcript files", type=["txt", "vtt"], accept_multiple_files=True)

if uploaded_files:
    transcripts = load_transcripts(uploaded_files)
    st.success(f"{len(transcripts)} file(s) uploaded successfully!")

    for filename, content in transcripts.items():
        st.markdown(f"## 📄 {filename}")

        # Split into 2 columns
        col1, col2 = st.columns(2)

        # LEFT → Decisions & Actions
        with col1:
            st.subheader("📌 Decisions & Action Items")
            result = extract_decisions_actions(content)

            st.markdown("**Decisions**")
            st.table(result["decisions"])

            st.markdown("**Action Items**")
            st.table(result["action_items"])
            import pandas as pd

            # Convert to DataFrame
            df = pd.DataFrame(result["action_items"])

            # Download button
            st.download_button(
                label="📥 Download Action Items as CSV",
                data=df.to_csv(index=False),
                file_name=f"{filename}_action_items.csv",
                mime="text/csv"
            )

        # RIGHT → Sentiment
        with col2:
            st.subheader("😊 Sentiment Analysis")
            sentiment = analyze_sentiment(content)
            st.table(sentiment)

        st.markdown("---")

    # Chatbot Section
    st.subheader("💬 Meeting Chatbot")

    user_question = st.text_input("Ask something about your meetings")

    if user_question:
        answer = chatbot_response(user_question, transcripts)
        st.success(answer)