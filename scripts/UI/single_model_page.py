import gradio as gr
from tkinter import Tk, TclError
from modules import shared
from scripts.mm_libs import downloader, loader
from scripts.mm_libs.debug import *
from .card import Card


# TODO: Refactor this, I don't like it
def UI():
    def fetch(input):
        if shared.opts.mm_testing_model_url:
            d_info("Testing URL found. Using it as input.")
            input = shared.opts.mm_testing_model_url
        elif shared.opts.mm_auto_paste:
            try:
                input = Tk().clipboard_get()
            except TclError:
                d_warn("Clipboard is empty, using current input as URL")
                return input

        models = downloader.fetch(input)
        if models:
            model_card.insert_models(models)
        return input

    with gr.Row():
        model_url_input = gr.Textbox(
            placeholder="Civitai URL or model ID",
            show_label=False,
            interactive=True,
            max_lines=1,
            elem_classes="mm_input",
        )
        fetch_btn = gr.Button(
            "Fetch Model Info", variant="primary", elem_classes="mm_btn"
        )

    model_card = Card()

    fetch_btn.click(
        fn=fetch,
        inputs=model_url_input,
        outputs=model_url_input,
    ).then(
        fn=model_card.get_updates, outputs=model_card.get_components()
    ).then(fn=model_card.update_gallery, outputs=model_card.model_gallery)
