# GenAI Log Analysis Agent

AI powered log monitoring system that analyzes server logs and answers questions about production incidents.

---

## Features
- Detects errors from raw logs
- Summarizes incidents automatically
- Allows querying logs using natural language
- Maintains conversation memory

---

## Tech Stack
FastAPI  
Pandas  
OpenAI API  
ETL Pipeline  
Python

---

## API Endpoints

### Analyze Logs
POST /analyze

Returns structured incident summary.

### Ask Questions
POST /ask?q=your_question

Example:
POST /ask?q=Why are users getting 404 errors?

---

## How to Run

1. Install dependencies
pip install -r requirements.txt

2. Start server
uvicorn main:app --reload

3. Open docs
http://127.0.0.1:8000/docs
