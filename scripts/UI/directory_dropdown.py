from functools import reduce
import os
import gradio as gr
from numpy import short
from scripts.mm_libs.loader import folders
from pathlib import Path

# Reusable Gradio Dropdown for selecting target directories
class Directory_Dropdown:
    def __init__(self) -> None:
        self.short_dirs = []
        self.selected_dir = None
        self.model_type = None
        self.changed = False
        self.path : Path = None

        # Gradio Structure
        self.dropdown = gr.Dropdown(
            label="Directory",
            info="Select the target directory for the file(s).",
            choices=[],
            interactive=True,
        )
        
        self.dropdown.select(self.change_directory, None, None)

    def get_components(self):
        return self.dropdown

    # Retain selected directory if another of the same type of model is fetched
    def get_updates(self):
        if self.changed or self.dropdown.value != self.selected_dir:
            self.changed = False
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