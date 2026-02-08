import os
import re
import pandas as pd

# Resolve absolute path of project directory
# Important when app runs from different working directory (e.g. Uvicorn / Docker / Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "logs.txt")


# ---------------- EXTRACT ----------------
def extract_logs():
    """
    Reads raw server log file and converts text lines into structured records.

    We parse Apache/NASA log format using regex.
    Raw logs → structured JSON-like objects

    Why needed:
    LLM cannot reliably understand raw logs at scale.
    We first structure data → then analyze.
    """

    logs = []

    # Regex for Common Log Format
    # Example:
    # host ident user [time] "request" status size
    pattern = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)'
    )

    with open(file_path, "r", encoding="latin-1") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                host, ident, user, time, request, status, size = match.groups()

                # Convert raw text into structured record
                logs.append({
                    "host": host,
                    "time": time,
                    "request": request,
                    "status": int(status),
                    "size": 0 if size == "-" else int(size)
                })

    return logs


# ---------------- TRANSFORM ----------------
def transform_logs(logs):
    """
    Converts structured logs into aggregated metrics.

    This is the core observability step:
    raw events → monitoring statistics

    LLM will NOT see individual logs.
    LLM sees only computed metrics (reduces hallucination).
    """

    df = pd.DataFrame(logs)

    summary = {
        # traffic volume
        "total_requests": len(df),

        # failures
        "error_count": int((df["status"] >= 400).sum()),

        # top failure types
        "top_errors": df[df["status"] >= 400]["status"].value_counts().head(5).to_dict(),

        # most accessed endpoints
        "most_requested": df["request"].value_counts().head(5).to_dict()
    }

    return summary


# ---------------- LOAD ----------------
def run_etl():
    """
    Full ETL pipeline:

    Extract  → parse logs
    Transform → compute metrics
    Load → return structured summary (used by AI agent)

    Not loading into DB because this project focuses on
    real-time analysis instead of storage.
    """

    logs = extract_logs()
    summary = transform_logs(logs)
    return summary
