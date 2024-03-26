from functools import reduce
from math import e
import os
import re
import gradio as gr
from scripts.mm_libs.debug import d_print
from scripts.mm_libs.model import Model
from scripts.mm_libs import downloader
from .directory_dropdown import Directory_DropDown as dir_dd

from modules.shared import opts

# TODO: Should detect on a per-OS basis
IILEGAL_WIN_CHARS = re.compile(r'[<>:"/|?*\\]')

def vaidate_filename(filename : str):
    if IILEGAL_WIN_CHARS.search(filename):
        gr.Warning("Invalid Filename: Illegal characters detected. Remove them or enable 'Trim Illegal Characters' in settings")
        return

    if filename == "":
        gr.Warning("Invalid Filename: Filename cannot be empty")
        return

    return filename


def adjust_filename(filename : str):
    if opts.mm_auto_trim_illegal_chars:
        filename = IILEGAL_WIN_CHARS.sub('', filename)


    if opts.mm_auto_trim_whitespace:
        filename = re.sub(" +", " ", filename)

    if opts.mm_auto_fit_brackets:
        filename = re.sub(r"([\[(\{])\s*([^)\]}]+?)\s*([\])}])", lambda x: f"{x.group(1)}{x.group(2).strip()}{x.group(3)}", filename)

     # Removes leading and trailing whitespace as the OS would do it automatically when saving a file
    filename = filename.strip()

    return filename

class Card:
    mapping = {
        "model_name": "self.selected_model.name",
        "model_version": "self.selected_model.version",
        "model_base": "self.selected_model.metadata['sd version']",
        "model_creator": "self.selected_model.creator",
        "model_type": "self.selected_model.type",
    }

    def __init__(
        self, title="huh", creator="defcreator", type="deftype", visibility=True
    ) -> None:
        self.models: list[Model] = None
        self.selected_model: Model = None

        self.selected_image = None
        self.selected_image_index = 0

        self.visibility = visibility

        # Gradio Structure
        with gr.Box(visible=visibility) as self.card_box:
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        self.model_name_text = gr.Textbox(
                            label="Model Name", max_lines=1, interactive=False
                        )
                        self.model_version_dropdown = gr.Dropdown(
                            label="Version", interactive=True, scale=0.3
                        )
                    self.model_creator_text = gr.Textbox(
                        label="Model Creator", max_lines=1, interactive=False
                    )
                    self.model_type_text = gr.Textbox(
                        label="Type", max_lines=1, interactive=False
                    )
                    self.model_keywords_text = gr.Textbox(
                        label="Trigger Words",
                        placeholder="No trigger words specified by creator",
                        interactive=True,
                    )
                    self.model_size_text = gr.Textbox(
                        label="Size", interactive=False, max_lines=1
                    )
                    self.model_base_text = gr.Textbox(
                        label="Base Model", interactive=False, max_lines=1
                    )
                self.model_gallery = gr.Gallery(
                    show_download_button=False, preview=True, elem_id="_gallery"
                )
            with gr.Row(equal_height=True):
                self.filename_input = gr.Textbox(
                    label="Filename",
                    info="Choose the filename for the model you are downloading.",
                    interactive=True,
                    max_lines=1,
                )
                self.dirdd = dir_dd()
                download_btn = gr.Button("Download")


        download_btn.click(adjust_filename, self.filename_input, self.filename_input).then(self.download, self.filename_input, None)
        
        self.model_version_dropdown.select(
            self.change_model, None, self.get_components()
        ).then(
            self.update_gallery, None, self.model_gallery
        )
        self.model_gallery.select(self.change_image, None, None)
    
    def get_components(self):
        return [
            self.card_box,
            self.model_name_text,
            self.model_version_dropdown,
            self.model_creator_text,
            self.model_type_text,
            self.model_keywords_text,
            self.model_size_text,
            self.model_base_text,
            # self.model_gallery, #Images are loaded after other info
            self.filename_input,
            self.dirdd.get_components(),
        ]

    def get_updates(self):
        # Name creation
        if opts.mm_auto_naming_formatting == "":
            name = f"{self.selected_model.name}"
        else:
            name = opts.mm_auto_naming_formatting
            for key, value in self.mapping.items():
                name = name.replace(key, str(eval(value)))

        return [
            gr.update(visible=self.visibility),
            self.selected_model.name,
            gr.Dropdown.update(
                value=self.selected_model.version,
                choices=reduce(lambda acc, xs: acc + [xs.version], self.models, []),
            ),
            self.selected_model.creator,
            self.selected_model.type,
            self.selected_model.metadata["activation text"],
            self.selected_model.size,
            self.selected_model.metadata["sd version"],
            # self.selected_model.images, #Images are loaded after other info
            name,
            self.dirdd.get_updates(),
        ]

    def insert_models(self, models: list[Model] = None):
        if models:
            self.models = models
            self.selected_model = models[0]
            self.selected_image = models[0].images[0][0]
            self.dirdd.update_choices(models[0].type)
            self.visibility = True
        else:
            self.visibility = False

    def change_image(self, evt: gr.SelectData):
        self.selected_image_index = evt.index
        self.selected_image = evt.value

    def update_gallery(self):
        if not self.selected_model:
            return self.model_gallery.value
        return self.selected_model.images

    # Should also update image to the one in the UI
    def change_model(self, evt: gr.SelectData):
        self.selected_model = self.models[evt.index]
        if len(self.selected_model.images) > self.selected_image_index:
            self.selected_image = self.selected_model.images[self.selected_image_index][0]
        else:
            self.selected_image = self.selected_model.images[0][0]
        return self.get_updates()

    def download(self, filename):
        filename = vaidate_filename(filename)

        if not filename:
            return
        
        downloader.download_model(
            self.dirdd.selected_dir / filename, self.selected_model, self.selected_image
        )

    