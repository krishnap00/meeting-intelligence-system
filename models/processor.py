# models/processor.py
import os
import random

def load_transcripts(uploaded_files):
    """
    Reads uploaded transcripts and returns a dictionary:
    {filename: content}
    """
    transcripts = {}
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        transcripts[file.name] = content
    return transcripts

def extract_decisions_actions(transcript_text):
    """
    Mock function: returns fake Decisions & Action Items
    """
    decisions = [
        "Approve the new API launch timeline",
        "Shift focus to marketing campaign next quarter"
    ]
    action_items = [
        {"who": "Alice", "what": "Prepare API documentation", "by_when": "Tomorrow"},
        {"who": "Bob", "what": "Schedule QA testing", "by_when": "Next Monday"},
        {"who": "Charlie", "what": "Draft marketing plan", "by_when": "Next Friday"}
    ]
    return {"decisions": decisions, "action_items": action_items}

def analyze_sentiment(transcript_text):
    """
    Mock sentiment analysis: returns random values for visualization
    """
    speakers = ["Alice", "Bob", "Charlie"]
    sentiment_data = {}
    for speaker in speakers:
        sentiment_data[speaker] = random.choice(["Positive", "Neutral", "Negative"])
    return sentiment_data

def chatbot_response(user_question, transcripts):
    """
    Mock chatbot response
    """
    return f"Mock answer to '{user_question}' based on {len(transcripts)} transcript(s)."