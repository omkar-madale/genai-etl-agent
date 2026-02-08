from openai import OpenAI
from prompts import ANALYZE_PROMPT, ASK_PROMPT
from memory import add_message, get_memory
from etl import run_etl

client = OpenAI()


def analyze_logs():
    summary = str(run_etl())

    messages = [
        {"role": "system", "content": ANALYZE_PROMPT},
        *get_memory(),
        {"role": "user", "content": summary}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1
    )

    reply = response.choices[0].message.content

    add_message("user", summary)
    add_message("assistant", reply)

    return reply


def ask_question(question: str):
    summary = str(run_etl())

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    reply = response.choices[0].message.content

    add_message("user", question)
    add_message("assistant", reply)

    return reply
