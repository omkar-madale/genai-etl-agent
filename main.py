from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, BackgroundTasks
from agent import analyze_logs, ask_question
import uuid
from memory import clear_memory

app = FastAPI(title="AI Log Analysis Agent")

# in-memory job store
JOBS = {}

@app.post("/memory/clear")
def reset_memory():
    clear_memory()
    return {"status": "memory cleared"}

@app.get("/")
def home():
    return {"message": "AI ETL Log Agent Running"}


# ---------- START ANALYSIS ----------
@app.post("/analyze/start")
def start_analysis(background_tasks: BackgroundTasks):

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "running", "result": None}

    background_tasks.add_task(run_analysis_job, job_id)

    return {"job_id": job_id, "status": "started"}


def run_analysis_job(job_id: str):
    try:
        result = analyze_logs(job_id)
        JOBS[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        JOBS[job_id] = {"status": "failed", "result": str(e)}


# ---------- CHECK STATUS ----------
@app.get("/analyze/status/{job_id}")
def get_status(job_id: str):
    return JOBS.get(job_id, {"error": "job not found"})


# ---------- GET RESULT ----------
@app.get("/analyze/result/{job_id}")
def get_result(job_id: str):
    job = JOBS.get(job_id)

    if not job:
        return {"error": "job not found"}

    if job["status"] != "completed":
        return {"status": job["status"]}

    return {"analysis": job["result"]}


# ---------- Q&A ----------
@app.post("/ask/{job_id}")
def ask(job_id: str, q: str):
    answer = ask_question(job_id, q)
    return {"answer": answer}
