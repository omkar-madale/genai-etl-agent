import os
import re
import pandas as pd
from azure.storage.blob import BlobServiceClient

# ==============================
# Azure Storage Configuration
# ==============================

CONTAINER_NAME = "data"
BLOB_NAME = "logs.txt"

# Read connection string from environment variable (Azure App Service -> Environment variables)
CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")


# ---------------- DOWNLOAD FROM BLOB ----------------
def download_logs_from_blob():
    """
    Downloads log file from Azure Blob Storage.

    Cloud apps must not depend on local disk.
    Storage is the source of truth.
    """

    if not CONNECTION_STRING:
        raise Exception("AZURE_STORAGE_CONNECTION_STRING not set in environment variables")

    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

    data = blob_client.download_blob().readall()

    # NASA logs are latin-1 encoded
    return data.decode("latin-1").splitlines()


# ---------------- EXTRACT ----------------
def extract_logs():
    """
    Parse Apache/NASA logs into structured records.
    """

    raw_lines = download_logs_from_blob()
    logs = []

    pattern = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)'
    )

    for line in raw_lines:
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
    """
    Convert structured logs into observability metrics.
    """

    if not logs:
        return {"error": "No logs found or parsing failed"}

    df = pd.DataFrame(logs)

    summary = {
        "total_requests": len(df),
        "error_count": int((df["status"] >= 400).sum()),
        "top_errors": df[df["status"] >= 400]["status"].value_counts().head(5).to_dict(),
        "most_requested": df["request"].value_counts().head(5).to_dict()
    }

    return summary


# ---------------- LOAD / PIPELINE ----------------
def run_etl():
    """
    Full ETL pipeline
    """

    logs = extract_logs()
    summary = transform_logs(logs)
    return summary
