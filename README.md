# GenAI Log Analysis Agent

## Overview

This project analyzes server access logs using FastAPI + OpenAI.

Instead of sending raw logs to the AI model, the system first performs ETL (Extract → Transform → Load) to compute statistics.
The AI then reasons only on calculated data, which reduces hallucination and improves reliability.

---

## What the system does

1. Reads server log file (`logs.txt`)
2. Extracts structured statistics (errors, URLs, status codes)
3. Sends summarized data to LLM
4. Returns short incident report
5. Allows user to ask questions about logs

---

## Why ETL is used

LLMs are not reliable with huge raw logs.

So the pipeline is:

Logs → Statistics → Prompt → AI reasoning

The model never reads raw logs directly.

---

## Tech Stack

* FastAPI
* Python
* Pandas
* OpenAI API (gpt-4o-mini)

---

## Project Structure

main.py → API endpoints
agent.py → LLM interaction
etl.py → log processing
memory.py → conversation memory
prompts.py → AI instructions
logs.txt → sample log data

---

## How to Run

### 1) Create virtual environment

python -m venv venv
venv\Scripts\activate

### 2) Install dependencies

pip install -r requirements.txt

### 3) Add API key

Create `.env`

OPENAI_API_KEY=your_key_here

### 4) Start server

uvicorn main:app --reload

Open browser:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Endpoints

### Analyze Logs

POST /analyze

Returns incident summary from logs.

---

### Ask Question

POST /ask?q=your_question

Example:
Why are users getting 404 errors?

---

## Example Output

Errors: 10980
Top Issues: 404 errors
Root Cause: Missing resources
Severity: High

---

## Notes

This project demonstrates how LLMs should be combined with traditional data processing instead of replacing it.
