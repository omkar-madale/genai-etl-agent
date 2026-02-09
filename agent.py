import json
from openai import OpenAI
from prompts import ANALYZE_PROMPT, ASK_PROMPT
from memory import add_message, get_memory
from etl import run_etl

client = OpenAI(timeout=60)

# In-memory cache (fast + safe for single Azure instance)
REPORT_CACHE = {}


def analyze_logs(job_id: str):
    """
    Runs ETL and generates AI incident report
    """

    summary = str(run_etl())

    messages = [
        {"role": "system", "content": ANALYZE_PROMPT},
        {"role": "user", "content": summary}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1
    )

    reply = response.choices[0].message.content

    # store ONLY final report (not raw logs)
    REPORT_CACHE[job_id] = reply

    return reply


def ask_question(job_id: str, question: str):
    """
    Ask questions about a specific analysis job
    """

    if job_id not in REPORT_CACHE:
        return "Report not found. Run analysis first."

    summary = REPORT_CACHE[job_id]

    user_prompt = f"""
INCIDENT REPORT:
{summary}

QUESTION:
{question}
"""

    messages = [
        {"role": "system", "content": ASK_PROMPT},
        *get_memory(),
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    reply = response.choices[0].message.content

    add_message("user", question)
    add_message("assistant", reply)

    return reply
