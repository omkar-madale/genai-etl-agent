# In-memory conversation storage
# Acts as short-term context memory for the LLM
# (similar to chat history in ChatGPT)
conversation_memory = []


def add_message(role, content):
    """
    Adds a message to conversation history.

    Why:
    LLM responses improve when it remembers previous interactions.
    We store both user questions and assistant answers.

    Important:
    OpenAI API requires message content to be STRING.
    Some objects (dict/list) can break the API request,
    so we force conversion to string for safety.
    """
    conversation_memory.append({
        "role": role,
        "content": str(content)  # ALWAYS STRING
    })


def get_memory():
    """
    Returns recent conversation context.

    Why limit history:
    LLM cost + latency grows with token size.
    Large history = slow + expensive + sometimes API errors.

    Strategy:
    Keep only last 6 messages → enough context, prevents token explosion.
    (Production systems use sliding window memory like this)
    """

    safe_memory = []

    # Defensive copy:
    # prevents accidental mutation & guarantees valid format
    for msg in conversation_memory:
        safe_memory.append({
            "role": msg["role"],
            "content": str(msg["content"])
        })

    # Sliding window memory
    return safe_memory[-6:]  # keep last 6 only
