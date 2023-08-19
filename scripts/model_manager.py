import modules.scripts as scripts

import gradio as gr
from pathlib import Path
from tkinter import Tk
from scripts.mm_libs import downloader, loader, model
from modules import script_callbacks, shared


loader.get_dirs()
dir_list = []


def select_image(evt: gr.SelectData):
    downloader.current_model.image = evt.value

def on_ui_tabs():
    def fetch(input):
        if shared.opts.mm_auto_paste:
            input = Tk().clipboard_get()

        (m_result, images) = downloader.fetch(input)
        if (m_result, images) != (None, None):
            return {
                model_box: gr.update(visible=True),
                model_url_input: input,
                model_gallery_output: images,
                model_name_output: m_result.name,
                model_creator_output: m_result.creator,
                model_size_output: m_result.size,
                model_type_output: m_result.type,
                file_name_input: f"{m_result.name} {m_result.version} ({m_result.creator})",
                model_keywords_output: gr.update(
                    value=m_result.metadata["activation text"], visible=True
                )
                if m_result.type in ("LORA", "LoCon")
                else gr.update(visible=False),
                model_base_output: m_result.metadata["sd version"],
            }
        return {
            model_url_input: input,
        }

    def download(filename, dropdown, type):
        dest = loader.folders[type][dir_list.index(Path(dropdown))]
        downloader.download(dest / filename)
        return

    # TODO: Fix this when possible
    # Annoying bug currently:
    # https://github.com/gradio-app/gradio/issues/1566
    # Essnetially when a dropdown's choices is updated you can't get the currently selected items index
    # This means that I'll have to create some sort of dublicate list and use the value to find the index. Annoying
    # Should be fixed in 4.0 version
    def update_dropdown(m_type):
        global dir_list
        subdirs = []
        for item in loader.folders[m_type]:
            subdirs.append(
                item.relative_to(
                    *item.parts[: len(loader.folders[m_type][0].parts) - 1]
                )
            )
        dir_list = subdirs.copy()
        return target_dir_drop.update(value=subdirs[0], choices=subdirs)

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
                        model_name_output = gr.Textbox(
                            label="Model Name", max_lines=1, interactive=False
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
                        model_size_output = gr.Textbox(label="Size", interactive=False, max_lines=1)
                        with gr.Accordion(label="Details", open=False):
                            model_downloads_output = gr.Textbox(label="Downloads", interactive=False, max_lines=1)
                            model_uploaded_output = gr.Textbox(label="Uploaded", interactive=False, max_lines=1)
                            model_base_output = gr.Textbox(label="Base Model", interactive=False, max_lines=1)
                            model_traning_output = gr.Textbox(label="Training", interactive=False, max_lines=1)
                            model_usage_tips_output = gr.Textbox(label="Usage Tips", interactive=False, max_lines=1)
                            


                    model_gallery_output = gr.Gallery(
                        show_download_button=False, preview=True
                    )
                with gr.Row(equal_height=True):
                    file_name_input = gr.Textbox(
                        label="Filename",
                        info="Choose the filename for the model you are downloading.",
                        interactive=True,
                        max_lines=1,
                    )
                    target_dir_drop = gr.Dropdown(
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
            ],
        )

        download_btn.click(
            download,
            [file_name_input, target_dir_drop, model_type_output],
            None,
        )

        # Component States Changes
        model_type_output.change(update_dropdown, model_type_output, target_dir_drop)
        model_gallery_output.select(select_image, None, None)

    return [(ui_component, "Model Manager", "model_manager_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)



def on_ui_settings():
    MM_SECTION =("mm", "Model Manager")

    mm_options = {
        "mm_auto_paste": shared.OptionInfo(True, "Enable Auto-paste"),
        "mm_allow_NSFW": shared.OptionInfo(False, "Allow NSFW Images"),
    }

    for key, opt in mm_options.items():
        opt.section = MM_SECTION
        shared.opts.add_option(key, opt)

script_callbacks.on_ui_settings(on_ui_settings)