
from tkinter import Tk
import gradio as gr
from scripts.mm_libs import downloader, loader
from modules import shared
from .card2 import Card


def UI():
    def fetch(input):
        if shared.opts.mm_auto_paste:
            input = Tk().clipboard_get()
        models = downloader.fetch(input)
        if models:
            model_card.insert_models(models)
            return model_card.get_updates() + [input]
        else:
            return {model_url_input: input}

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
    fetch_btn.click(fetch, model_url_input, model_card.get_components() + [model_url_input])
