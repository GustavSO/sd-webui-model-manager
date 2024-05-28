import gradio as gr
from scripts.mm_libs.model import Model

class Card():
    def __init__(self, title="huh", creator="defcreator", type="deftype", visibility=False) -> None:
        self.title = title
        self.creator = creator
        self.type = type
        self.image = None
        self.visibility = visibility

        # Gradio Structure
        with gr.Box(visible=visibility) as self.card_box:
            # gr.Markdown(f"# {self.title}")
            with gr.Row():
                with gr.Column():
                    self.model_name_text = gr.Textbox(label="Model Name", value=self.title, max_lines=1, interactive=True)
                    self.model_type_text = gr.Textbox(label="Model Type", value=self.type, max_lines=1)
                    gr.Dropdown(choices=["Help", "Me"])
                with gr.Column():
                    self.image_output = gr.Image()
                    download_btn = gr.Button("Download")
        download_btn.click(self.download, None, None)

    def get_components(self):
        return [self.card_box, self.model_name_text, self.model_type_text, self.image_output]

    def get_updates(self):
        return [gr.update(visible=self.visibility), self.title, self.type, self.image]
    
    def insert_models(self, models: list[Model] = None):
        if models:
            self.title = models[0].name
            self.creator = models[0].creator
            self.type = models[0].type
            self.image = models[0].selected_image
            self.visibility = True
        else:
            self.visibility = False

    def download(self):
        print(self.title)