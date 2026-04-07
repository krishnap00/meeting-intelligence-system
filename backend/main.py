from fastapi import FastAPI
from pydantic import BaseModel
from models.processor import extract_decisions_actions, analyze_sentiment_real, chatbot_response

app = FastAPI(title="Meeting Intelligence API")

class TranscriptRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    question: str
    context: str

@app.get("/")
def home():
    return {
        "status": "online",
        "system": "Meeting Intelligence Hub"
    }

@app.post("/analyze")
def analyze(request: TranscriptRequest):
    analysis = extract_decisions_actions(request.text)
    sentiment = analyze_sentiment_real(request.text)

    return {
        "analysis": analysis,
        "sentiment": sentiment
    }

@app.post("/chat")
def chat(request: ChatRequest):
    answer = chatbot_response(request.question, request.context)
    return {"answer": answer}

from pydantic import BaseModel
from models.processor import explain_decision

class ExplainRequest(BaseModel):
    decision: str
    context: str

@app.post("/explain")
def explain(req: ExplainRequest):
    result = explain_decision(req.decision, req.context)
    return {"explanation": result}