import os
import gradio as gr
from scripts.mm_libs.debug import d_print
from scripts.mm_libs.loader import folders
from pathlib import Path

# Reusable Gradio Dropdown for selecting target directories
class Directory_Dropdown:
    def __init__(self) -> None:
        self.short_dirs = []
        self.selected_dir = None # Used by card.py to get the selected directory
        self.model_type = None
        self.changed = False
        self.path : Path = None
        self.init = None

        # Gradio Structure
        self.dropdown = gr.Dropdown(
            label="Directory",
            info="Select the target directory for the file(s).",
            choices=[],
            interactive=True,
        )

        self.dropdown.select(self.change_directory)
        
        # Hidden elements and functions used by JavaScript for initialization
        self.js_init_dropdown_btn = gr.Button("False", visible=False, elem_id="js_init_dir_dropdown")
        self.js_init_dropdown_btn.click(self.init_dropdown, outputs=self.js_init_dropdown_btn)
        

    def get_components(self):
        return self.dropdown

    # Should only update the dropdown if the directory has changed or the dropdown has been initialized.
    def get_updates(self):
        if self.changed or self.init:
            self.changed = False
            self.init = False
            return gr.Dropdown.update(value=self.short_dirs[0], choices=self.short_dirs)
        else:
            return gr.Dropdown.update()

    # Updates the choices of the directory dropdown based on the type of model fetched.
    def update_choices(self, model_type: str):
        if self.path == folders[model_type][0]:
            return self.short_dirs
        
        self.path = folders[model_type][0]
        self.changed = True
        self.model_type = model_type

        self.short_dirs = [os.path.relpath(dir, self.path.parent) for dir in folders[model_type]]
        self.selected_dir = folders[model_type][0]

    def change_directory(self, evt: gr.SelectData):
        self.selected_dir = folders[self.model_type][evt.index]

    def init_dropdown(self):
        self.init = True
        return "True"
        