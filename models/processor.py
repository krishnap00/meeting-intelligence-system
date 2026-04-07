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
    You are an expert meeting analyst.

    Your task is to extract structured intelligence from the transcript.

    STRICT RULES:
    - Only include REAL decisions (not discussions)
    - Action items MUST include a responsible person
    - If no deadline is mentioned, use "TBD"
    - Keep answers concise and clear
    - Do NOT hallucinate

    Return ONLY valid JSON in this exact format:
    {{
        "summary": "2-sentence executive summary.",
        "decisions": ["Clear decision 1", "Clear decision 2"],
        "action_items": [
            {{"who": "Person name", "what": "Specific task", "by_when": "Deadline or TBD"}}
        ]
    }}

    Transcript:
    {truncated_text}
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
    You are an AI Meeting Assistant.

    Rules:
    - Answer ONLY using the provided context
    - If answer not found, say "Not mentioned in the meetings"
    - Always mention speaker or meeting context if possible
    - Be concise and factual

    Question: {user_question}

    Context:
    {combined_text[:20000]}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

def explain_decision(decision, transcript_text):
    prompt = f"""
    You are an AI meeting analyst.

    A decision was extracted:
    "{decision}"

    Find the exact parts of the transcript that justify this decision.

    Rules:
    - Quote relevant lines from transcript
    - Include speaker names if available
    - Keep it short and precise
    - Do NOT hallucinate

    Transcript:
    {transcript_text[:15000]}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content