import streamlit as st

st.title("Meeting Intelligence System")

uploaded_file = st.file_uploader("Upload Transcript", type=["txt"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    st.text_area("Transcript", content, height=300)