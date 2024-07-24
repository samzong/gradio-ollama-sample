import os
import gradio as gr
import openai
from datetime import datetime
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Environment variables configuration
model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
api_host = os.getenv("API_HOST", "http://localhost:11434/v1")

# Configure OpenAI client
client = openai.OpenAI(
    base_url=api_host,
    api_key="sk-xxx"  # Ollama doesn't need an actual API key, but we need to set a placeholder
)

# Initialize conversations
conversations = {}

# Function to estimate tokens
def estimate_tokens(text):
    # This is a rough estimate. Actual token count may vary.
    return len(re.findall(r'\w+|[^\w\s]', text))

def chat(message, history, conversation_id):
    global conversations
    if not conversation_id:
        conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        conversations[conversation_id] = {"name": message[:20], "messages": []}
    
    conversations[conversation_id]["messages"].append({"role": "user", "content": message})
    
    user_tokens = estimate_tokens(message)
    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model_name,
        messages=conversations[conversation_id]["messages"],
        stream=True
    )

    partial_message = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            partial_message += chunk.choices[0].delta.content
            yield history + [[message, partial_message]], ""

    assistant_tokens = estimate_tokens(partial_message)
    end_time = time.time()
    time_taken = end_time - start_time
    token_rate = (user_tokens + assistant_tokens) / time_taken if time_taken > 0 else 0

    conversations[conversation_id]["messages"].append({"role": "assistant", "content": partial_message})
    
    info = f"""API Host: {api_host}
Model: {model_name}
Estimated user message tokens: {user_tokens}
Estimated assistant message tokens: {assistant_tokens}
Estimated token rate: {token_rate:.2f} tokens/second"""
    
    yield history + [[message, partial_message]], info

def get_conversation_list():
    return [{"name": conv["name"], "id": conv_id} for conv_id, conv in conversations.items()]

def start_new_conversation():
    return None, [], ""

def load_conversation(conversation_id):
    if conversation_id in conversations:
        return [(msg["content"], conversations[conversation_id]["messages"][i+1]["content"])
                for i, msg in enumerate(conversations[conversation_id]["messages"][:-1:2])], ""
    return [], ""

# Gradio interface
with gr.Blocks(css="#chatbot { height: 400px; overflow-y: scroll; }") as demo:
    gr.Markdown("# AI Chat")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(elem_id="chatbot")
            msg = gr.Textbox(placeholder="Enter your message here...")
            send = gr.Button("Send")
            info = gr.Textbox(label="Model Info", lines=5, interactive=False)
        
        with gr.Column(scale=1):
            conversation_list = gr.Dropdown(choices=get_conversation_list(), label="Conversations", interactive=True)
            new_conversation = gr.Button("New Conversation")
    
    conversation_id = gr.State()

    send.click(chat, inputs=[msg, chatbot, conversation_id], outputs=[chatbot, info])
    msg.submit(chat, inputs=[msg, chatbot, conversation_id], outputs=[chatbot, info])
    
    new_conversation.click(start_new_conversation, outputs=[conversation_id, chatbot, info])
    conversation_list.change(load_conversation, inputs=[conversation_list], outputs=[chatbot, info])

    gr.HTML("""
    <script src="/static/script.js"></script>
    <style>
    body.dark {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    body.dark #chatbot {
        background-color: #2a2a2a;
    }
    </style>
    """)

demo.launch()