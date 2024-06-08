import json, requests
from modules import script_callbacks, shared, ui_components
from modules.options import categories, options_section, OptionInfo, Options

import gradio as gr
from scripts.mm_libs import loader
from scripts.UI import single_model_page, notification_fetcher_page, utilities
from scripts.mm_libs.debug import d_print, d_warn


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
            with gr.Tab("Scrape Civitai Notifications"):
                notification_fetcher_page.UI()
        # with gr.Tab("Utilities"):
        #     utilities.UI()

        
        def get_model_url(json_file):
            d_print(f"Retrieving model URL from: {json_file}")
            download_url = "None"

            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    if "model url" in data:
                        download_url = data["model url"]
                    elif "notes" in data and data["notes"] != "":
                        download_url = data["notes"] 
            except Exception as e:
                d_warn(f"Error reading JSON file {e.__class__.__name__}")
                return "None"
            
            # TODO: Figure out some way to validate the url, (regex or something) as this causes to much delay
            # try:
            #     requests.get(download_url)
            # except Exception as e:
            #     d_warn(f"Error contacting download URL {download_url} {e.__class__.__name__}")
            #     return "None"


            if download_url == "None":
                d_warn("Couldn't find a model URL for the model. Please make sure the JSON file contains a 'model url' or 'notes' field with the URL")
            return download_url

        # Hidden elements and functions used by JavaScript
        from_js = gr.Textbox("", visible=False, elem_id="from_js")
        to_js = gr.Textbox("", visible=False, elem_id="to_js")

        js_open_model_btn = gr.Button(
            "Open Model",
            visible=False,
            elem_id="js_open_model_btn",
        )

        js_open_model_btn.click(get_model_url, inputs=from_js, outputs=to_js)


    loader.sort_dirs()
    return [(ui_component, "Model Manager", "model_manager_tab")]


#################
# Settings Menu #
#################
def on_ui_settings():
    options_templates = {}

    categories.register_category("mm", "Model Manager")



    options_templates.update(options_section(('mm_download', "Download", "mm"), {
        "mm_auto_paste": OptionInfo(True, "Auto-paste clipboard").info("Will automatically paste the clipboard contents into the URL input field when fetching models"),
        "mm_allow_NSFW": OptionInfo(True, "Allow NSFW Images").info("Will display NSFW images when fetching models"),
        "mm_civitai_api_key": OptionInfo("", "Civitai API key").info("API Key used to download certain models. Create one at https://civitai.com/user/account"),
        "mm_supress_API_warnings": OptionInfo(False, "Supress API key warning").info("Only applies when fetching. Will still show errors on download if it fails due to authentication issues"),
        "mm_folder_depth": OptionInfo(1, "Subdirectory Depth", gr.Slider, {"minimum": 0, "maximum": 10, "step": 1}).info("This is the depth of subdirectories to search for when downloading models. Default is 1, which means it will only search the immediate subdirectories of the root folder for the model type"),
        "mm_image_amount": OptionInfo(0, "Image Amount", gr.Slider, {"minimum": 0, "maximum": 10, "step": 1}).info("The amount of images to display in the model card. 0 will fetch all images, but can be slow for models with many images. Gradio 4 will fix this issue"),
    }))

    options_templates.update(options_section(('mm_auto_naming', "Auto Naming", "mm"), {
        "mm_auto_naming_formatting": OptionInfo("model_name model_version [model_base] (model_creator)", "Naming Format").js("Info", "settingsHints").info("The formatting of the auto naming suggestion. Need to adhere to filenaming restriction of the OS, eg. no / or \ in Windows. If left empty it will default to the name of the model as it is displayed on the model page"),
        "mm_auto_trim_whitespace": OptionInfo(True, "Trim Whitespace").info("Automatically trim consecutive whitespace series to a single space in the filename during model downloads"),
        "mm_auto_trim_illegal_chars": OptionInfo(True, "Trim Illegal Characters").info("Automatically remove any illegal characters from the filename when downloading a model"),
        "mm_auto_fit_brackets": OptionInfo(True, "Fit Brackets").info("Automatically removes whitespace around brackets in the filename when downloading a model. Eg. ( My Model ) -> (My Model), supports [], {} and ()"),
        "mm_capatalize": OptionInfo(False, "Capitalize").info("Capitalize the first letter of each word in the filename when downloading a model"),
        "mm_capatalize_versioning": OptionInfo(True, "Capitalize Versioning").info("Capitalize the version number in the filename when downloading a model. Eg. v1 -> V1"),
        "mm_decimalize_versioning": OptionInfo(True, "Decimalize Versioning").info("Convert the version number to decimal format in the filename when downloading a model. Eg. V1 -> V1.0"),
        "mm_remove_empty_brackets": OptionInfo(True, "Remove Empty Brackets").info("Automatically remove empty brackets from the filename when downloading a model"),
        "mm_filter_alphabet": OptionInfo([], "Filter Alphabets", ui_components.DropdownMulti, lambda: {"choices": list(["Chinese", "Japanese", "Latin", "Cyrillic", "Korean"])}).info("Automatically remove characters from the selected alphabets from the filename when downloading a model"),
        "mm_excluded_words_or_phrases": OptionInfo("", "Excluded Words or Phrases").info("Words or phrases to exclude from the filename. Only done once when fetching and only effects model_name or model_version. Useful for removing redundant words like lora, embedding etc. Separate words with a comma (,). Eg. 'lora, embedding, model'. Case insensitive"),
        "mm_format_on_fetch": OptionInfo(True, "Format on Fetch").info("Automatically format the filename when fetching a model in adherence to the formatting settings. If disabled, the filename will be formatted when downloading the model instead"),
        }))

    options_templates.update(options_section(('mm_test', "Testing", "mm"), {
        "mm_disable_download": OptionInfo(False, "Disable Download").info("Disables the downloading, useful for debugging and testing the UI without actually downloading anything"),
        "mm_github_token": OptionInfo("", "GitHub Token").info("GitHub Token used to create a Selenium session, for fetching civitai notifications. Feature still in development!"),
        "mm_print_warnings": OptionInfo(True, "Print Warnings").info("Print warnings to the console, if false the warning messages will only show on the UI"),
        "mm_print_errors": OptionInfo(True, "Print Errors").info("Print errors to the console, if false the error messages will only show on the UI"),
        "mm_print_info": OptionInfo(True, "Print Info").info("Print info to the console, if false the info messages will only show on the UI"),
        "mm_testing_model_url": OptionInfo("", "Testing Model URL").info("URL to test the model fetching with. If filled, each time the model fetching is triggered, this URL will be used. Useful for testing the fetching without having to go to the Civitai website. Leave empty to disable"),
        }))

    # TODO: When more sections are added, assign it here instead
    for key, opt in options_templates.items():
        shared.opts.add_option(key, opt)


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
