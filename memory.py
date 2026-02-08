conversation_memory = []

def add_message(role, content):
    conversation_memory.append({"role": role, "content": content})

def get_memory():
    return conversation_memory[-6:]  # last 6 messages only
