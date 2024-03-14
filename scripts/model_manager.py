import modules.scripts as scripts
from modules import script_callbacks, shared

import gradio as gr
from pathlib import Path
from tkinter import Tk
from scripts.mm_libs import downloader, loader, model
from scripts.UI import single_model_page, notification_fetcher_page
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

    loader.sort_dirs()
    return [(ui_component, "Model Manager", "model_manager_tab")]


#################
# Settings Menu #
#################
def on_ui_settings():
    MM_SECTION = ("mm", "Model Manager")

    mm_options = {
        "mm_auto_paste": shared.OptionInfo(True, "Enable Auto-paste"),
        "mm_allow_NSFW": shared.OptionInfo(True, "Allow NSFW Images"),
        "mm_civitai_api_key": shared.OptionInfo("", 'Civitai API Key used to download certain models. Create one at https://civitai.com/user/account'),
        "mm_supress_API_warnings": shared.OptionInfo(False, "Supress API Key warnings on fetch. Will still show errors on download if it fails due to authentication issues."),
        "mm_folder_depth": shared.OptionInfo(1, "Depth of subdirectories to search for when downloading models. Default is 1, which means it will only search the immediate subdirectories of the root folder for the model type.", gr.Slider,
        {"minimum": 0, "maximum": 10, "step": 1}),
        "mm_github_token": shared.OptionInfo("", 'The GitHub Token used to create a Selenium session. Feature still in development.'),
    }

    for key, opt in mm_options.items():
        opt.section = MM_SECTION
        shared.opts.add_option(key, opt)


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)

