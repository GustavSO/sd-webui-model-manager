import modules.scripts as scripts

import gradio as gr
from pathlib import Path
from tkinter import Tk
from scripts.mm_libs import downloader, loader, model
from scripts.UI import single_model_page, notification_fetcher_page
from modules import script_callbacks, shared
from functools import reduce

def on_ui_tabs():
    with gr.Blocks() as ui_component:
        gr.Markdown(
            """
            # Model Manager
            """
        )
        with gr.Tab("Downloader"):
            with gr.Tab("Single Model"):
                single_model_page.UI()
            with gr.Tab("Fetch from Civitai notifications"):
                notification_fetcher_page.UI()

    return [(ui_component, "Model Manager", "model_manager_tab")]


script_callbacks.on_ui_tabs(on_ui_tabs)


#################
# Settings Menu #
#################
def on_ui_settings():
    MM_SECTION = ("mm", "Model Manager")

    mm_options = {
        "mm_auto_paste": shared.OptionInfo(True, "Enable Auto-paste"),
        "mm_allow_NSFW": shared.OptionInfo(True, "Allow NSFW Images"),
        "mm_github_token": shared.OptionInfo("", 'The GitHub Token used to create a Selenium session'),
    }

    for key, opt in mm_options.items():
        opt.section = MM_SECTION
        shared.opts.add_option(key, opt)


script_callbacks.on_ui_settings(on_ui_settings)
