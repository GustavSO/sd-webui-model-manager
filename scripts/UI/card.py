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

alphabet_mapping = {
    "Chinese": r"[\u4E00-\u9FFF\u3400-\u4DBF\U00020000-\U0002A6DF\U0002A700-\U0002B73F\U0002B740-\U0002B81F\U0002B820-\U0002CEAF\U0002CEB0-\U0002EBEF]", # Basic Multilingual Plane, Extension A, Extension B, Extension C, Extension D, Extension E
    "Cyrillic": r"[\u0400-\u04ff]", # Cyrillic
    "Japanese": r"[\u3040-\u30ff]", # Hiragana and Katakana (should maybe also include Kanji)
    "Latin": r"[a-zA-Z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF]", # Latin Letters, Latin-1 Supplement (excluding × [U+00D7] and ÷ [U+00F7]),
    "Korean": r"[\u3131-\u3163\uac00-\ud7a3]" # Hangul Jamo, Hangul Syllables /TODO: Validate
}

name_mapping = {
    "model_name": "self.selected_model.name",
    "model_version": "self.selected_model.version",
    "model_base": "self.selected_model.metadata['sd version']",
    "model_creator": "self.selected_model.creator",
    "model_type": "self.selected_model.type",
}

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

    alphabets = opts.mm_filter_alphabet
    for alphabet in alphabets:
        filename = re.sub(alphabet_mapping[alphabet], "", filename)

    if opts.mm_auto_fit_brackets:
        filename = re.sub(r"([\[(\{])\s*([^)\]}]+?)\s*([\])}])", lambda x: f"{x.group(1)}{x.group(2).strip()}{x.group(3)}", filename)

    if opts.mm_remove_empty_brackets:
        filename = re.sub(r"[\[(\{]\s*[\])}]", "", filename)

    if opts.mm_capatalize:
        filename = re.sub(r"\b\w", lambda x: x.group().upper(), filename)

    if opts.mm_capatalize_versioning:
        filename = re.sub(r"v(\d+)", lambda x: f"V{x.group(1)}", filename)
    
    if opts.mm_decimalize_versioning:
        filename = re.sub(r"V(\d+)(?!\.\d+)", lambda x: f"V{x.group(1)}.0", filename)

    if opts.mm_auto_trim_whitespace:
        filename = re.sub(" +", " ", filename)

    return filename.strip()



class Card:
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

    def process_name(self, name, excluded_words):
        for word in excluded_words:
            name = re.sub(word.strip(), '', name, flags=re.IGNORECASE)
        return name

    def get_name_from_formatting(self, name_format, excluded_words):
        for key, value in name_mapping.items():
            eval_value = str(eval(value))
            if key in ['model_name', 'model_version']:
                eval_value = self.process_name(eval_value, excluded_words)
            name_format = name_format.replace(key, eval_value)
        return name_format

    def get_updates(self):
        excluded_words = opts.mm_excluded_words_or_phrases.split(",") if opts.mm_excluded_words_or_phrases else []
        if opts.mm_auto_naming_formatting == "":
            name = f"{self.selected_model.name}"
            if excluded_words:
                name = self.process_name(name, excluded_words)
        else:
            name = self.get_name_from_formatting(opts.mm_auto_naming_formatting, excluded_words)

        if opts.mm_format_on_fetch:
            name = adjust_filename(name)

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
            self.selected_image = models[0].images[0][0] if models[0].images else None
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
        
        if opts.mm_disable_download:
            d_print("Download Disabled. Can be enable in settings 'Development' section")
            return
        
        downloader.download_model(
            self.dirdd.selected_dir / filename, self.selected_model, self.selected_image
        )

    