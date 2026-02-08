from openai import OpenAI
from prompts import SYSTEM_PROMPT
from memory import add_message, get_memory
from etl import run_etl

client = OpenAI()

def analyze_logs():
    summary = run_etl()

    prompt = f"""
Here is the system log summary:

{summary}

Explain what incident is happening in production.
"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += get_memory()
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )

    reply = response.choices[0].message.content

    add_message("user", prompt)
    add_message("assistant", reply)

    return reply


def ask_question(question: str):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += get_memory()
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )

    reply = response.choices[0].message.content

    add_message("user", question)
    add_message("assistant", reply)

    return reply
