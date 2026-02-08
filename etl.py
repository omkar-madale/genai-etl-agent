import os
import re
import pandas as pd

# Always resolve correct path (important for servers)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "logs.txt")


# ---------------- EXTRACT ----------------
def extract_logs():
    logs = []
    pattern = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)'
    )

    with open(file_path, "r", encoding="latin-1") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                host, ident, user, time, request, status, size = match.groups()
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
    df = pd.DataFrame(logs)

    summary = {
        "total_requests": len(df),
        "error_count": int((df["status"] >= 400).sum()),
        "top_errors": df[df["status"] >= 400]["status"].value_counts().head(5).to_dict(),
        "most_requested": df["request"].value_counts().head(5).to_dict()
    }

    return summary


# ---------------- LOAD (not DB, returning summary) ----------------
def run_etl():
    logs = extract_logs()
    summary = transform_logs(logs)
    return summary
