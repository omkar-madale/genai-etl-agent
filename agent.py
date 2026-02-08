from openai import OpenAI
from prompts import ANALYZE_PROMPT, ASK_PROMPT
from memory import add_message, get_memory
from etl import run_etl

# Initialize OpenAI client using API key from environment
client = OpenAI()


def analyze_logs():
    """
    Generates automated incident summary from logs.

    Flow:
    ETL → structured statistics → LLM → monitoring-style report

    We DO NOT send raw logs to LLM.
    We send processed summary only.
    This reduces:
    - cost
    - latency
    - hallucinations
    - token overflow
    """

    # Run ETL pipeline to compute log statistics
    summary = str(run_etl())

    # Construct chat history for LLM
    # system prompt defines strict output format
    # memory provides conversational continuity
    messages = [
        {"role": "system", "content": ANALYZE_PROMPT},
        *get_memory(),
        {"role": "user", "content": summary}
    ]

    # Low temperature = deterministic monitoring-style output
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1
    )

    reply = response.choices[0].message.content

    # Store conversation for contextual follow-ups
    add_message("user", summary)
    add_message("assistant", reply)

    return reply


def ask_question(question: str):
    """
    Allows interactive investigation over computed log data.

    Difference from analyze_logs():
    analyze_logs → automatic incident summary
    ask_question → human-driven investigation

    We again attach computed ETL statistics so
    the LLM answers ONLY from real data (RAG style).
    """

    # Always recompute latest log state
    summary = str(run_etl())

    # Combine question + data context
    user_prompt = f"""
LOG DATA:
{summary}

QUESTION:
{question}
"""

    messages = [
        {"role": "system", "content": ASK_PROMPT},
        *get_memory(),
        {"role": "user", "content": user_prompt}
    ]

    # Slightly higher temperature for flexible Q&A reasoning
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    reply = response.choices[0].message.content

    # Save conversation memory
    add_message("user", question)
    add_message("assistant", reply)

    return reply
