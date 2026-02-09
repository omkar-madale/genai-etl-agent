import os
import re
import pandas as pd
from azure.storage.blob import BlobClient


# ---------------- RUNTIME CONFIG (IMPORTANT FIX) ----------------
# Azure Free App Service loads env variables AFTER container start.
# So NEVER read os.getenv at module load time.
# Always read inside function during execution.

def get_storage_config():
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    container = os.environ.get("AZURE_STORAGE_CONTAINER")
    blob_name = os.environ.get("AZURE_STORAGE_BLOB")

    if not connection_string:
        raise Exception("AZURE_STORAGE_CONNECTION_STRING missing at runtime")

    if not container:
        raise Exception("AZURE_STORAGE_CONTAINER missing")

    if not blob_name:
        raise Exception("AZURE_STORAGE_BLOB missing")

    return connection_string, container, blob_name


# ---------------- DOWNLOAD FROM AZURE BLOB ----------------
def download_logs_from_blob():
    """
    Downloads log file from Azure Blob Storage
    Returns list of raw log lines
    """

    connection_string, container, blob_name = get_storage_config()

    blob = BlobClient.from_connection_string(
        conn_str=connection_string,
        container_name=container,
        blob_name=blob_name
    )

    print("Downloading logs from Azure Blob...")

    # Stream instead of loading huge memory at once
    stream = blob.download_blob()
    data = stream.readall().decode("latin-1")

    return data.splitlines()


# ---------------- EXTRACT ----------------
def extract_logs():
    """
    Convert raw Apache log lines into structured records
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

    df = pd.DataFrame(logs)

    if df.empty:
        return {"error": "No logs parsed"}

    summary = {
        "total_requests": int(len(df)),
        "error_count": int((df["status"] >= 400).sum()),
        "top_errors": df[df["status"] >= 400]["status"].value_counts().head(5).to_dict(),
        "most_requested": df["request"].value_counts().head(5).to_dict()
    }

    return summary


# ---------------- ETL PIPELINE ----------------
def run_etl():
    logs = extract_logs()
    summary = transform_logs(logs)
    return summary
