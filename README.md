# meeting-intelligence-system
AI-powered meeting insights and chatbot system
# 📊 Meeting Intelligence Hub

# Project Title
Meeting Intelligence Hub

## The Problem
Meetings often generate large amounts of information, making it difficult to track decisions, action items, and key insights efficiently.

## The Solution
Our platform automatically extracts decisions, action items, and sentiment from meeting transcripts and audio. Users can search, filter, and export insights in real-time, improving team productivity and clarity.

## Tech Stack
- **Programming Languages:** Python, JavaScript
- **Frameworks:** Streamlit (frontend), FastAPI (backend)
- **Databases:** None (can store feedback locally or use SQLite)
- **APIs / Tools:** OpenAI API (for NLP processing), Plotly (visualizations)

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/meeting-intelligence-system.git
cd meeting-intelligence-system
```

### 2. Create a virtual environment and install dependencies:
python -m venv venv
** Activate environment**
# Windows
venv\Scripts\activate
** macOS/Linux**
source venv/bin/activate
pip install -r requirements.txt

### 3. Run the backend (FastAPI):
uvicorn backend.main:app --reload

### 4.Run the frontend (Streamlit):
streamlit run frontend/app.py

### 5.Open the app in your browser:
Frontend: http://localhost:8501
Backend: http://localhost:8000

## Usage: 
Upload meeting transcripts and optional audio.
Click Extract Intelligence to analyze meetings.
Browse the Dashboard:
View Summaries, Decisions, Action Items, Sentiment Charts, and Assistant answers.
Use the search bar to filter meetings by keywords.
Download action items as a CSV.
Provide feedback via the Feedback section.
