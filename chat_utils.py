import re
import time
import ollama
from datetime import datetime
from config import OLLAMA_HOST

conversations = {}

def estimate_tokens(text):
    return len(re.findall(r'\w+|[^\w\s]', text))

def chat(message, history, conversation_id, model):
    global conversations
    if not conversation_id:
        conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        conversations[conversation_id] = {"name": message[:20], "messages": []}
    
    conversations[conversation_id]["messages"].append({"role": "user", "content": message})
    
    user_tokens = estimate_tokens(message)
    start_time = time.time()
    
    try:
        stream = ollama.chat(
            model=model,
            messages=conversations[conversation_id]["messages"],
            stream=True
        )

        partial_message = ""
        for chunk in stream:
            if 'message' in chunk:
                content = chunk['message'].get('content', '')
                partial_message += content
                yield history + [[message, partial_message]], "", conversation_id, model

        assistant_tokens = estimate_tokens(partial_message)
        end_time = time.time()
        time_taken = end_time - start_time
        token_rate = (user_tokens + assistant_tokens) / time_taken if time_taken > 0 else 0

        conversations[conversation_id]["messages"].append({"role": "assistant", "content": partial_message})
        
        info = f"""API Host: {OLLAMA_HOST}
Model: {model}
Estimated user message tokens: {user_tokens}
Estimated assistant message tokens: {assistant_tokens}
Estimated token rate: {token_rate:.2f} tokens/second"""
        
        yield history + [[message, partial_message]], info, conversation_id, model

    except Exception as e:
        print(f"Error in API request: {e}")
        yield history + [[message, f"Error: Unable to get response from the model. {str(e)}"]], "", conversation_id, model

def get_conversation_list():
    return {conv["name"]: conv_id for conv_id, conv in conversations.items()}

def start_new_conversation():
    new_id = datetime.now().strftime("%Y%m%d%H%M%S")
    conversations[new_id] = {"name": "New Conversation", "messages": []}
    return new_id, [], ""

def load_conversation(conversation_name):
    conversation_id = next((conv_id for conv_id, conv in conversations.items() if conv["name"] == conversation_name), None)
    if conversation_id:
        history = [(msg["content"], conversations[conversation_id]["messages"][i+1]["content"])
                   for i, msg in enumerate(conversations[conversation_id]["messages"][:-1:2])]
        return history, ""
    return [], ""