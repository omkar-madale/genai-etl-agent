from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from agent import analyze_logs, ask_question
import json

app = FastAPI(title="AI Log Analysis Agent")

@app.get("/")
def home():
    return {"message": "AI ETL Log Agent Running"}

@app.post("/analyze")
def analyze():
    result = analyze_logs()
    return {"analysis": result}

@app.post("/ask")
def ask(q: str):
    answer = ask_question(q)
    return {"answer": answer}

@app.get("/report")
def get_report():
    try:
        with open("report.json", "r") as f:
            data = json.load(f)
        return data
    except:
        return {"error": "No report generated yet"}
