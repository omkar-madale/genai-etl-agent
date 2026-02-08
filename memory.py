conversation_memory = []

def add_message(role, content):
    conversation_memory.append({
        "role": role,
        "content": str(content)  # ALWAYS STRING
    })

def get_memory():
    safe_memory = []

    for msg in conversation_memory:
        safe_memory.append({
            "role": msg["role"],
            "content": str(msg["content"])
        })

    return safe_memory[-6:]  # keep last 6 only (prevents token explosion)
