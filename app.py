import os
import sys
import gradio as gr
import ollama
from datetime import datetime
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

# Environment variables configuration
os.environ['OLLAMA_HOST'] = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Function to get available models using Ollama library
def get_available_models():
    try:
        models = ollama.list()
        return [model['name'] for model in models['models']]
    except Exception as e:
        print(f"Error fetching models: {e}")
        sys.exit(1)

# Get available models
available_models = get_available_models()
if not available_models:
    print("No models available from Ollama service.")
    sys.exit(1)

# Set the default model to the first available model
current_model = available_models[0]

# Initialize conversations
conversations = {}

# Function to estimate tokens
def estimate_tokens(text):
    # This is a rough estimate. Actual token count may vary.
    return len(re.findall(r'\w+|[^\w\s]', text))

def chat(message, history, conversation_id, model):
    global conversations, current_model
    current_model = model
    if not conversation_id:
        conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        conversations[conversation_id] = {"name": message[:20], "messages": []}
    
    conversations[conversation_id]["messages"].append({"role": "user", "content": message})
    
    user_tokens = estimate_tokens(message)
    start_time = time.time()
    
    try:
        stream = ollama.chat(
            model=current_model,
            messages=conversations[conversation_id]["messages"],
            stream=True
        )

        partial_message = ""
        for chunk in stream:
            if 'message' in chunk:
                content = chunk['message'].get('content', '')
                partial_message += content
                yield history + [[message, partial_message]], "", conversation_id, current_model

        assistant_tokens = estimate_tokens(partial_message)
        end_time = time.time()
        time_taken = end_time - start_time
        token_rate = (user_tokens + assistant_tokens) / time_taken if time_taken > 0 else 0

        conversations[conversation_id]["messages"].append({"role": "assistant", "content": partial_message})
        
        info = f"""API Host: {os.environ['OLLAMA_HOST']}
Model: {current_model}
Estimated user message tokens: {user_tokens}
Estimated assistant message tokens: {assistant_tokens}
Estimated token rate: {token_rate:.2f} tokens/second"""
        
        yield history + [[message, partial_message]], info, conversation_id, current_model

    except Exception as e:
        print(f"Error in API request: {e}")
        yield history + [[message, f"Error: Unable to get response from the model. {str(e)}"]], "", conversation_id, current_model

def get_conversation_list():
    return {conv["name"]: conv_id for conv_id, conv in conversations.items()}

def start_new_conversation():
    new_id = datetime.now().strftime("%Y%m%d%H%M%S")
    conversations[new_id] = {"name": "New Conversation", "messages": []}
    return new_id, [], "", current_model

def load_conversation(conversation_name):
    conversation_id = next((conv_id for conv_id, conv in conversations.items() if conv["name"] == conversation_name), None)
    if conversation_id:
        history = [(msg["content"], conversations[conversation_id]["messages"][i+1]["content"])
                   for i, msg in enumerate(conversations[conversation_id]["messages"][:-1:2])]
        return history, ""
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
            model_dropdown = gr.Dropdown(choices=available_models, label="Select Model", value=current_model)
            conversation_list = gr.Dropdown(choices=[], label="Conversations", interactive=True)
            new_conversation = gr.Button("New Conversation")
    
    conversation_id = gr.State()

    def update_conversation_list():
        conv_list = get_conversation_list()
        return gr.update(choices=list(conv_list.keys()))

    send.click(chat, inputs=[msg, chatbot, conversation_id, model_dropdown], outputs=[chatbot, info, conversation_id, model_dropdown]).then(
        update_conversation_list, outputs=[conversation_list])
    msg.submit(chat, inputs=[msg, chatbot, conversation_id, model_dropdown], outputs=[chatbot, info, conversation_id, model_dropdown]).then(
        update_conversation_list, outputs=[conversation_list])
    
    new_conversation.click(start_new_conversation, outputs=[conversation_id, chatbot, info, model_dropdown]).then(
        update_conversation_list, outputs=[conversation_list])
    conversation_list.change(load_conversation, inputs=[conversation_list], outputs=[chatbot, info])

demo.launch()