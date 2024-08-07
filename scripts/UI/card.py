import gradio as gr

from scripts.mm_libs.debug import d_message, d_warn
from scripts.mm_libs.model import Model, sanitize_trigger_words
from scripts.mm_libs import fetcher, downloader, namer
from .directory_dropdown import Directory_Dropdown as dir_dd
from modules import ui 
from modules.shared import opts
from modules.ui_components import ToolButton

from functools import reduce

# Should probably move this to a more appropriate place
CLEAN_SYMBOL = '\U0001f9f9\ufe0f' #🧹
FORMAT_SYMBOL = '\u270F\ufe0f' #✏️

class Card:
    def __init__(
        self,
        visibility=True,
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
                    with gr.Row():
                        self.model_trigger_words_text = gr.Textbox(
                            label="Trigger Words",
                            placeholder="No trigger words specified by creator",
                            interactive=True,
                        )
                        sanitize_words = ToolButton(CLEAN_SYMBOL, tooltip="Sanitize Trigger Words") # Figure out how to enable tooltips, something to do with classname i think
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
                clean_filename = ToolButton(CLEAN_SYMBOL, tooltip="Clean Filename")
                self.dirdd = dir_dd()
                download_btn = gr.Button("Download", elem_classes="mm_btn")
            progress_bar = gr.HTML(
                value='<div style="min-height: 0px;"></div>',
                elem_id="cardProgressBar",
                elem_classes="progress_bar",
            )

        download_btn.click(
            name_process, self.filename_input, self.filename_input
        ).then(
            fn=self.ready_download,
            inputs=[self.filename_input, self.model_trigger_words_text],
            outputs=progress_bar,
            _js="initializeProgressbar",
        )

        self.model_version_dropdown.select(
            fn=self.change_model, outputs=self.get_components()
        ).then(self.update_gallery, None, outputs=self.model_gallery)
        self.model_gallery.select(self.change_image, None, None)

        sanitize_words.click(fn=sanitize_trigger_words, inputs=self.model_trigger_words_text, outputs=self.model_trigger_words_text)
        clean_filename.click(namer.adjust_filename, self.filename_input, self.filename_input)

    def get_components(self):
        return [
            self.card_box,
            self.model_name_text,
            self.model_version_dropdown,
            self.model_creator_text,
            self.model_type_text,
            self.model_trigger_words_text,
            self.model_size_text,
            self.model_base_text,
            # self.model_gallery, #Images are loaded after other info
            self.filename_input,
            self.dirdd.get_components(),
        ]

    def get_updates(self):
        # If no model is selected, don't update the UI
        if not self.selected_model:
            return [gr.update() for _ in range(10)]

        name = namer.format_filename(
            opts.mm_auto_naming_formatting, self.selected_model
        )

        if opts.mm_format_on_fetch:
            name = namer.adjust_filename(name)

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

    def insert_models(self, models: list[Model] = None, version_index=0):
        if models:
            self.models = models
            self.selected_model = models[version_index]
            self.selected_image = models[version_index].images[0][0] if models[version_index].images else None
            self.dirdd.update_choices(models[version_index].type, models[version_index].main_tag)
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
            self.selected_image = self.selected_model.images[self.selected_image_index][
                0
            ]
        else:
            self.selected_image = self.selected_model.images[0][0]
        return self.get_updates()

    ## TODO: Fix this
    def ready_download(self, filename, trigger_words, progress=gr.Progress()):
        if namer.vaidate_filename(filename) == False:
            return

        # Ensures the metadata is the same as the one in the UI
        # TODO: Move this to its own function
        self.selected_model.metadata["activation text"] = trigger_words

        if opts.mm_disable_download:
            d_message(
                "Download Disabled. Can be enable in settings 'Development' section"
            )
            return

        downloader.download_model(
            self.dirdd.selected_dir / filename,
            self.selected_model,
            self.selected_image,
            progress,
        )


def name_process(name):
    if opts.mm_format_on_download:
        return namer.adjust_filename(name)
    return name