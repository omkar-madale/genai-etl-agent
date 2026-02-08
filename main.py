# Loads environment variables from .env (used for OPENAI_API_KEY)
from dotenv import load_dotenv
load_dotenv()

# FastAPI framework to expose REST endpoints
from fastapi import FastAPI

# Core agent functions
# analyze_logs → generates incident report from computed statistics
# ask_question → Q&A over previously analyzed data
from agent import analyze_logs, ask_question

import json 

# Create API application
app = FastAPI(title="AI Log Analysis Agent")


# Health check endpoint
# Used to verify server is running (DevOps style readiness probe)
@app.get("/")
def home():
    return {"message": "AI ETL Log Agent Running"}


# Main analysis endpoint
# Triggers ETL pipeline + AI reasoning
# Flow:
# logs.txt → ETL → summary stats → LLM → structured incident output
@app.post("/analyze")
def analyze():
    result = analyze_logs()
    return {"analysis": result}


# Q&A endpoint
# Allows querying the analyzed log context
# Example:
# /ask?q=Why are users getting 404 errors?
@app.post("/ask")
def ask(q: str):
    answer = ask_question(q)
    return {"answer": answer}


# Returns last generated structured report
# This avoids recomputing ETL + LLM each time (acts like cache layer)
@app.get("/report")
def get_report():
    try:
        # Reads report generated during analysis phase
        with open("report.json", "r") as f:
            data = json.load(f)
        return data
    except:
        # Happens if /analyze not executed yet
        return {"error": "No report generated yet"}
