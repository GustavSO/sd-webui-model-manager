from sympy import true
import modules.scripts as scripts
from modules import script_callbacks, shared
from modules.options import categories

import gradio as gr
from scripts.mm_libs import loader
from scripts.UI import single_model_page, notification_fetcher_page, utilities


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
        # with gr.Tab("Utilities"):
        #     utilities.UI()

    loader.sort_dirs()
    return [(ui_component, "Model Manager", "model_manager_tab")]


#################
# Settings Menu #
#################
def on_ui_settings():
    categories.register_category("mm", "Model Manager")
    cat_id = "mm"

    # Sections
    download = ("mm_download", "Download")

    if not (hasattr(shared.OptionInfo, "info") and callable(getattr(shared.OptionInfo, "info"))):
        def info(self, info):
            self.label += f" ({info})"
            return self
        shared.OptionInfo.info = info

    
    mm_options = {
        "mm_auto_paste": shared.OptionInfo(
            True, 
            "Enable Auto-paste",
            section=download,
            ).info("Will automatically paste the clipboard contents into the URL input field when fetching models"),

        "mm_allow_NSFW": shared.OptionInfo(
            True,
            "Allow NSFW Images",
            section=download,
            ).info("Will display NSFW images when fetching models"),

        "mm_civitai_api_key": shared.OptionInfo(
            "",
            "Civitai API key",
            section=download,
        ).info("API Key used to download certain models. Create one at https://civitai.com/user/account"),

        "mm_supress_API_warnings": shared.OptionInfo(
            False,
            "Supress API key warning",
            section=download,
        ).info("Only applies when fetching. Will still show errors on download if it fails due to authentication issues"),

        "mm_folder_depth": shared.OptionInfo(
            1,
            "Subdirectory Depth",
            gr.Slider,
            {"minimum": 0, "maximum": 10, "step": 1},
            section=download,
        ).info("This is the depth of subdirectories to search for when downloading models. Default is 1, which means it will only search the immediate subdirectories of the root folder for the model type"),

        "mm_github_token": shared.OptionInfo(
            "",
            "GitHub Token",
            section=download,
        ).info("GitHub Token used to create a Selenium session, for fetching civitai notifications. Feature still in development!"),
    }

    # TODO: When more sections are added, assign it here instead
    for key, opt in mm_options.items():
        opt.category_id = cat_id
        shared.opts.add_option(key, opt)


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
