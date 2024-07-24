import gradio as gr
from config import OLLAMA_HOST
from model_utils import initialize_models
from chat_utils import chat, get_conversation_list, start_new_conversation, load_conversation

current_model, available_models = initialize_models()

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
    
    new_conversation.click(start_new_conversation, outputs=[conversation_id, chatbot, info]).then(
        update_conversation_list, outputs=[conversation_list])
    conversation_list.change(load_conversation, inputs=[conversation_list], outputs=[chatbot, info])

demo.launch()