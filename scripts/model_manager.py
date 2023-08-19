import modules.scripts as scripts

import gradio as gr
from pathlib import Path
from tkinter import Tk
from scripts.mm_libs import downloader, loader, model
from modules import script_callbacks, shared
from functools import reduce


loader.get_dirs()

# TODO: Fix this mess when the bug regarding Gradio dropdowns not retaining/updating indexes when updating choices is fixed
selected_version_index = (
    0  # Always shows the first version of the model so this is okay
)
selected_dir_index = 0

fetched_models = []


def change_image(evt: gr.SelectData):
    fetched_models[0].selected_image = evt.value

def change_version(evt: gr.SelectData):
    global selected_version_index
    selected_version_index = evt.index
    model = fetched_models[selected_version_index]
    return [model.images, model.size, model.metadata["activation text"], model.metadata["sd version"], f"{model.name} [{model.version}] ({model.creator})"]

def change_directory(evt: gr.SelectData):
    global selected_dir_index
    selected_dir_index = evt.index
    return


def on_ui_tabs():

    def fetch(input):
        global fetched_models
        if shared.opts.mm_auto_paste:
            input = Tk().clipboard_get()

        fetched_models = downloader.fetch(input)
        if not fetched_models:
            return {model_url_input: input}
        return {
            model_box: gr.update(visible=True),
            model_url_input: input,
            model_gallery_output: fetched_models[0].images,
            model_name_output: fetched_models[0].name,
            model_creator_output: fetched_models[0].creator,
            model_size_output: fetched_models[0].size,
            model_type_output: fetched_models[0].type,
            file_name_input: f"{fetched_models[0].name} {fetched_models[0].version} ({fetched_models[0].creator})",
            model_version_dropdown: gr.Dropdown().update(
                value=fetched_models[0].version,
                choices=reduce(lambda acc, xs: acc + [xs.version], fetched_models, []),
            ),
            model_keywords_output: gr.update(
                value=fetched_models[0].metadata["activation text"], visible=True
            )
            if fetched_models[0].type in ("LORA", "LoCon")
            else gr.update(visible=False),
            model_base_output: fetched_models[0].metadata["sd version"],
        }

    def download(filename, type):
        path = loader.folders[type][selected_dir_index]
        model = fetched_models[selected_version_index]
        downloader.download_model(path / filename, model)

    # Updates the directory dropdown to show the subdirectories of the selected model type.
    # Performs a reduction on the string paths of the subdirectories to make them more readable.
    def update_directory_dropdown(model_type):
        subdirs = reduce(
            lambda acc, xs: acc
            + [xs.relative_to(*xs.parts[: len(loader.folders[model_type][0].parts) - 1])],
            loader.folders[model_type],
            [],
        )
        return directory_dropdown.update(value=subdirs[0], choices=subdirs)

    ##################
    # User Interface #
    ##################
    with gr.Blocks() as ui_component:
        gr.Markdown(
            """
            # Model Manager
            """
        )
        with gr.Tab("Downloader"):
            with gr.Row():
                model_url_input = gr.Textbox(
                    placeholder="Civitai URL or model ID",
                    show_label=False,
                    interactive=True,
                    max_lines=1,
                )
                fetch_btn = gr.Button("Fetch Model Info")

            # TODO: Figure out a better way to group and layout of sections, this feels needlessly complex
            with gr.Box(elem_classes="ch_box", visible=False) as model_box:
                gr.Markdown("## Model Information")
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            model_name_output = gr.Textbox(
                                label="Model Name", max_lines=1, interactive=False
                            )
                            model_version_dropdown = gr.Dropdown(
                                label="Version", choices=["Help", "Me"], scale=0.3
                            )
                        model_creator_output = gr.Textbox(
                            label="Model Creator", max_lines=1, interactive=False
                        )
                        model_type_output = gr.Textbox(
                            label="Type", max_lines=1, interactive=False
                        )
                        model_keywords_output = gr.Textbox(
                            label="Trigger Words",
                            placeholder="No trigger words specified by creator",
                            interactive=True,
                        )
                        model_size_output = gr.Textbox(
                            label="Size", interactive=False, max_lines=1
                        )
                        with gr.Accordion(label="Details", open=False):
                            model_downloads_output = gr.Textbox(
                                label="Downloads", interactive=False, max_lines=1
                            )
                            model_uploaded_output = gr.Textbox(
                                label="Uploaded", interactive=False, max_lines=1
                            )
                            model_base_output = gr.Textbox(
                                label="Base Model", interactive=False, max_lines=1
                            )
                            model_traning_output = gr.Textbox(
                                label="Training", interactive=False, max_lines=1
                            )
                            model_usage_tips_output = gr.Textbox(
                                label="Usage Tips", interactive=False, max_lines=1
                            )

                    model_gallery_output = gr.Gallery(
                        show_download_button=False, preview=True, elem_id="_gallery"
                    )
                with gr.Row(equal_height=True):
                    file_name_input = gr.Textbox(
                        label="Filename",
                        info="Choose the filename for the model you are downloading.",
                        interactive=True,
                        max_lines=1,
                    )
                    directory_dropdown = gr.Dropdown(
                        label="Directory",
                        info="Select the target directory for the file(s).",
                        interactive=True,
                    )
                    download_btn = gr.Button("Download")

        ##################
        # Event Handling #
        ##################

        # Buttons
        fetch_btn.click(
            fetch,
            model_url_input,
            [
                model_url_input,
                model_name_output,
                model_creator_output,
                file_name_input,
                model_type_output,
                model_keywords_output,
                model_size_output,
                model_base_output,
                model_gallery_output,
                model_box,
                model_version_dropdown,
                directory_dropdown,
            ],
        )

        download_btn.click(
            download,
            [file_name_input, model_type_output],
            None,
        )

        # Component States Changes #

        ## General
        model_type_output.change(update_directory_dropdown, model_type_output, directory_dropdown)

        ## Gallery
        model_gallery_output.select(change_image, None, None)

        ## Dropdowns
        directory_dropdown.select(change_directory, None, None)
        model_version_dropdown.select(
            change_version,
            None,
            [
                model_gallery_output,
                model_size_output,
                model_keywords_output,
                model_base_output,
                file_name_input
            ],
        )

    return [(ui_component, "Model Manager", "model_manager_tab")]


script_callbacks.on_ui_tabs(on_ui_tabs)


#################
# Settings Menu #
#################
def on_ui_settings():
    MM_SECTION = ("mm", "Model Manager")

    mm_options = {
        "mm_auto_paste": shared.OptionInfo(True, "Enable Auto-paste"),
        "mm_allow_NSFW": shared.OptionInfo(False, "Allow NSFW Images"),
    }

    for key, opt in mm_options.items():
        opt.section = MM_SECTION
        shared.opts.add_option(key, opt)


script_callbacks.on_ui_settings(on_ui_settings)
