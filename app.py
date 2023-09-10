import os
from controller import Controller
import gradio as gr

os.environ["TOKENIZERS_PARALLELISM"] = "false"
colors = ["#64A087", "green", "black"]

CSS = """
#question input {
    font-size: 16px;
}
#app-title {
    width: 100%;
    margin: auto;
}
#url-textbox {
    padding: 0 !important;
}
#short-upload-box .w-full {
    min-height: 10rem !important;
}

#select-a-file {
    display: block;
    width: 100%;
}
#file-clear {
    padding-top: 2px !important;
    padding-bottom: 2px !important;
    padding-left: 8px !important;
    padding-right: 8px !important;
	margin-top: 10px;
}
.gradio-container .gr-button-primary {
    background: linear-gradient(180deg, #CDF9BE 0%, #AFF497 100%);
    border: 1px solid #B0DCCC;
    border-radius: 8px;
    color: #1B8700;
}
.gradio-container.dark button#submit-button {
    background: linear-gradient(180deg, #CDF9BE 0%, #AFF497 100%);
    border: 1px solid #B0DCCC;
    border-radius: 8px;
    color: #1B8700
}
table.gr-samples-table tr td {
    border: none;
    outline: none;
}
table.gr-samples-table tr td:first-of-type {
    width: 0%;
}
div#short-upload-box div.absolute {
    display: none !important;
}
gradio-app > div > div > div > div.w-full > div, .gradio-app > div > div > div > div.w-full > div {
    gap: 0px 2%;
}
gradio-app div div div div.w-full, .gradio-app div div div div.w-full {
    gap: 0px;
}
gradio-app h2, .gradio-app h2 {
    padding-top: 10px;
}
#answer {
    overflow-y: scroll;
    color: white;
    background: #666;
    border-color: #666;
    font-size: 20px;
    font-weight: bold;
}
#answer span {
    color: white;
}
#answer textarea {
    color:white;
    background: #777;
    border-color: #777;
    font-size: 18px;
}
#url-error input {
    color: red;
}
"""

# TODO: Copy
controller = Controller()


def process_pdf(file):
    if file is not None:
        controller.embed_document(file)
    return (
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
    )


def respond(message, history):
    botmessage = controller.retrieve(message)
    history.append((message, botmessage))
    return "", history


def clear_everything():
    return (None, None, None)


with gr.Blocks(css=CSS, title="") as demo:
    gr.Markdown("# AskPDF ", elem_id="app-title")
    gr.Markdown("## Upload a PDF and Ask Questions!", elem_id="select-a-file")
    gr.Markdown(
        "Drop an interesting PDF and ask questions about it!",
        elem_id="select-a-file",
    )
    with gr.Row():
        with gr.Column(scale=3):
            upload = gr.File(label="Upload PDF", type="file")
            with gr.Row():
                clear_button = gr.Button("Clear", variant="secondary")

        with gr.Column(scale=6):
            chatbot = gr.Chatbot()
            with gr.Row().style(equal_height=True):
                with gr.Column(scale=8):
                    question = gr.Textbox(
                        show_label=False,
                        placeholder="e.g. What is the document about?",
                        lines=1,
                        max_lines=1,
                    ).style(container=False)
                with gr.Column(scale=1, min_width=60):
                    submit_button = gr.Button(
                        "Ask me 🤖", variant="primary", elem_id="submit-button"
                    )

    upload.change(
        fn=process_pdf,
        inputs=[upload],
        outputs=[
            question,
            clear_button,
            submit_button,
            chatbot,
        ],
        api_name="upload",
    )
    question.submit(respond, [question, chatbot], [question, chatbot])
    submit_button.click(respond, [question, chatbot], [question, chatbot])
    clear_button.click(
        fn=clear_everything,
        inputs=[],
        outputs=[upload, question, chatbot],
        api_name="clear",
    )

if __name__ == "__main__":
    demo.launch(enable_queue=False, share=False)