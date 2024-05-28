import gradio as gr
from scripts.mm_libs import downloader, loader
from modules import shared


def UI():
    gr.Markdown(
        """
        # SHA256 Hasher
        Store all your hashes in one place.
        Useful when downloading new models, as the hash can be used to verify if you already have the model.
        """
    )
    gr.Button(
        "Validate Hashes", variant="primary", elem_classes="mm_btn"
    )