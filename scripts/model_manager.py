import modules.scripts as scripts

import gradio as gr
from pathlib import Path
from tkinter import Tk
from scripts.mm_libs import downloader, loader, model, state
from scripts.mm_libs.state import settings
from modules import script_callbacks

loader.get_dirs()
auto_paste = True
dir_list = []

test = {"Huh": False}


def select_image(evt: gr.SelectData):
    downloader.current_model.image = evt.value


def on_ui_tabs():
    def fetch(url):
        if auto_paste:
            url = Tk().clipboard_get()

        (m_result, images) = downloader.fetch(url)
        if (m_result, images):
            return {
                model_box: gr.update(visible=True),
                model_url_input: url,
                model_gallery_output: images,
                model_name_output: m_result.name,
                model_creator_output: m_result.creator,
                model_type_output: m_result.type,
                file_name_input: f"{m_result.name} {m_result.version} ({m_result.creator})",
                model_keywords_output: gr.update(
                    value=m_result.metadata["activation text"], visible=True
                )
                if m_result.type in ("LORA", "LoCon")
                else gr.update(visible=False),
                model_base_output: m_result.base_model,
            }
        return {
            model_url_input: url,
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
                        with gr.Row():
                            model_creator_output = gr.Textbox(
                                label="Model Creator", max_lines=1, interactive=False
                            )
                            creator_btn = gr.Button(
                                "View", scale=0.25, visible=False
                            )  # TODO: Implement
                        model_type_output = gr.Textbox(
                            label="Type", max_lines=1, interactive=False
                        )
                        model_keywords_output = gr.Textbox(
                            label="Trigger Words",
                            placeholder="No trigger words specified by creator",
                            interactive=True,
                        )
                        model_base_output = gr.Textbox(
                            label="Base Model", interactive=False, max_lines=1
                        )

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

        # TODO: Implement a settings page
        with gr.Tab("Settings", visible=False):
            auto_paste_cb = gr.Checkbox(
                label="Auto-paste clipboard", value=True
            )
            nsfw_img_cb = gr.Checkbox(
                label="Allow NSFW Images", value=True
            )
            # nsfw_img_cb = gr.Checkbox(label="Allow NSFW Images", value=True)
            save_settings_btn = gr.Button("Save settings")

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

        save_settings_btn.click(state.save_settings, [auto_paste_cb, nsfw_img_cb], None)

        # Component States Changes
        model_type_output.change(update_dropdown, model_type_output, target_dir_drop)
        model_gallery_output.select(select_image, None, None)

    return [(ui_component, "Model Manager", "model_manager_tab")]


script_callbacks.on_ui_tabs(on_ui_tabs)
