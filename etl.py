import os
import re
import pandas as pd
from azure.storage.blob import BlobClient


# ---------------- CONFIG ----------------
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER = os.getenv("BLOB_CONTAINER")
BLOB_NAME = os.getenv("BLOB_NAME")


# ---------------- EXTRACT ----------------
def extract_logs():
    """
    Read logs directly from Azure Blob Storage
    """

    blob = BlobClient.from_connection_string(
        CONNECTION_STRING,
        container_name=CONTAINER,
        blob_name=BLOB_NAME
    )

    data = blob.download_blob().content_as_text(encoding="latin-1")

    logs = []

    pattern = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)'
    )

    for line in data.splitlines():
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

    if df.empty:
        return {"error": "No logs found"}

    summary = {
        "total_requests": len(df),
        "error_count": int((df["status"] >= 400).sum()),
        "top_errors": df[df["status"] >= 400]["status"].value_counts().head(5).to_dict(),
        "most_requested": df["request"].value_counts().head(5).to_dict()
    }

    return summary


# ---------------- PIPELINE ----------------
def run_etl():
    logs = extract_logs()
    return transform_logs(logs)
