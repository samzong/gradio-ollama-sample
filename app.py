import gradio as gr
from config import OLLAMA_HOST
from model_utils import initialize_models
from chat_utils import chat

current_model, available_models = initialize_models()


def chat_with_models(message, history1, history2, model1, model2):
    response1 = ""
    response2 = ""
    info1 = ""
    info2 = ""

    for r1, i1, _, _ in chat(message, history1, None, model1):
        response1, info1 = r1, i1
        yield [history1 + [[message, response1]], history2 + [[message, response2]]], info1, info2

    for r2, i2, _, _ in chat(message, history2, None, model2):
        response2, info2 = r2, i2
        yield [history1 + [[message, response1]], history2 + [[message, response2]]], info1, info2


# Gradio interface
with gr.Blocks(css="#chatbot1, #chatbot2 { height: 400px; overflow-y: scroll; }") as demo:
    gr.Markdown("# AI Chat")

    with gr.Row():
        with gr.Column(scale=1):
            model_dropdown1 = gr.Dropdown(
                choices=available_models, label="Model 1", value=current_model)
            chatbot1 = gr.Chatbot(elem_id="chatbot1", label="Model 1")
            info1 = gr.Textbox(label="Model 1 Info",
                               lines=5, interactive=False)

        with gr.Column(scale=1, visible=False) as col2:
            model_dropdown2 = gr.Dropdown(
                choices=available_models, label="Model 2", value=current_model)
            chatbot2 = gr.Chatbot(elem_id="chatbot2", label="Model 2")
            info2 = gr.Textbox(label="Model 2 Info",
                               lines=5, interactive=False)

    with gr.Row():
        msg = gr.Textbox(placeholder="Enter your message here...", scale=3)
        send = gr.Button("Send", scale=1)

    with gr.Row():
        compare_button = gr.Button("Toggle Comparison Mode")

    is_compare_mode = gr.State(False)

    def toggle_comparison_mode(compare_mode):
        new_mode = not compare_mode
        return (
            gr.update(visible=new_mode),  # col2
            new_mode  # is_compare_mode
        )

    def chat_wrapper(message, history1, history2, model1, model2, is_compare):
        history1 = history1 or []
        history2 = history2 or []
        if is_compare:
            for (h1, h2), i1, i2 in chat_with_models(message, history1, history2, model1, model2):
                yield h1, h2, i1, i2
        else:
            for r, i, _, _ in chat(message, history1, None, model1):
                yield history1 + [[message, r]], history2, i, ""

    send.click(chat_wrapper,
               inputs=[msg, chatbot1, chatbot2, model_dropdown1,
                       model_dropdown2, is_compare_mode],
               outputs=[chatbot1, chatbot2, info1, info2])

    msg.submit(chat_wrapper,
               inputs=[msg, chatbot1, chatbot2, model_dropdown1,
                       model_dropdown2, is_compare_mode],
               outputs=[chatbot1, chatbot2, info1, info2])

    compare_button.click(toggle_comparison_mode,
                         inputs=[is_compare_mode],
                         outputs=[col2, is_compare_mode])

demo.launch()
