import re
import time
import ollama
from config import OLLAMA_HOST


def estimate_tokens(text):
    return len(re.findall(r'\w+|[^\w\s]', text))


def chat(message, history, _, model):
    history = history or []

    user_tokens = estimate_tokens(message)
    start_time = time.time()

    try:
        stream = ollama.chat(
            model=model,
            messages=history + [{"role": "user", "content": message}],
            stream=True
        )

        partial_message = ""
        for chunk in stream:
            if 'message' in chunk:
                content = chunk['message'].get('content', '')
                partial_message += content
                yield partial_message, "", None, model

        assistant_tokens = estimate_tokens(partial_message)
        end_time = time.time()
        time_taken = end_time - start_time
        token_rate = (user_tokens + assistant_tokens) / \
            time_taken if time_taken > 0 else 0

        info = f"""API Host: {OLLAMA_HOST}
                Model: {model}
                Estimated user message tokens: {user_tokens}
                Estimated assistant message tokens: {assistant_tokens}
                Estimated token rate: {token_rate:.2f} tokens/second"""

        yield partial_message, info, None, model

    except Exception as e:
        print(f"Error in API request: {e}")
        yield f"Error: Unable to get response from the model. {str(e)}", "", None, model
