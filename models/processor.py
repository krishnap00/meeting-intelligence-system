import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def clean_vtt(text):
    """Removes WEBVTT headers and timestamps to optimize token usage."""
    text = re.sub(r"WEBVTT\n", "", text)
    text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n", "", text)
    return text

def load_transcripts(uploaded_files):
    """Processes uploaded files and cleans VTT data."""
    transcripts = {}
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        if file.name.endswith(".vtt"):
            content = clean_vtt(content)
        transcripts[file.name] = content
    return transcripts

def extract_decisions_actions(transcript_text):
    """Feature 1: Extracts structured Summary, Decisions, and Action Items."""
    truncated_text = transcript_text[:15000]
    
    prompt = f"""
    Analyze the meeting transcript and provide a structured report.
    You MUST return ONLY a JSON object with this exact structure:
    {{
        "summary": "2-sentence executive summary.",
        "decisions": ["Decision 1", "Decision 2"],
        "action_items": [
            {{"who": "Name", "what": "Task", "by_when": "Deadline/TBD"}}
        ]
    }}
    Transcript: {truncated_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"summary": "Processing error.", "decisions": [], "action_items": []}

def analyze_sentiment_real(transcript_text):
    """Feature: Real AI-powered sentiment analysis per speaker."""
    prompt = f"Identify speakers and sentiment (Positive, Neutral, Negative). Return JSON: {{'Speaker': 'Sentiment'}}. Transcript: {transcript_text[:5000]}"
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {}

def chatbot_response(user_question, combined_text):
    """Feature 2: Contextual query reasoning using high-parameter model."""
    prompt = f"""
    You are an AI Meeting Assistant. Answer based ONLY on the context.
    Cite the meeting or speaker.
    Question: {user_question}
    Context: {combined_text[:20000]}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content