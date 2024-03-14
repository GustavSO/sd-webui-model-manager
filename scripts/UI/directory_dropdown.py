from functools import reduce
import os
import gradio as gr
from numpy import short
from scripts.mm_libs.loader import folders

# Reusable Gradio Dropdown for selecting target directories
class Directory_DropDown:
    def __init__(self, subdirs=["Hello", "There"]) -> None:
        self.short_dirs = subdirs
        self.selected_dir = None
        self.model_type = None
        self.changed = False

        # Gradio Structure
        self.dropdown = gr.Dropdown(
            label="Directory",
            info="Select the target directory for the file(s).",
            choices=subdirs,
            interactive=True,
        )

        self.dropdown.select(self.change_directory, None, None)

    def get_components(self):
        return self.dropdown

    # Retain selected directory if another of the same type of model is fetched
    def get_updates(self):
        if self.changed:
            self.changed = False
            return gr.Dropdown.update(value=self.short_dirs[0], choices=self.short_dirs)
        else:
            return gr.Dropdown.update()

    # Updates the choices of the directory dropdown based on the type of model fetched.
    # Performs a reduction on the string paths of the subdirectories to make them more readable.
    def update_choices(self, model_type: str):
        if self.model_type == model_type:
            return
        self.changed = True
        self.model_type = model_type
        self.short_dirs = reduce(
            lambda acc, xs: acc
            + [xs.relative_to(*xs.parts[: len(folders[model_type][0].parts) - 1])],
            folders[model_type],
            [],
        )
        self.selected_dir = folders[model_type][0]

    def change_directory(self, evt: gr.SelectData):
        self.selected_dir = folders[self.model_type][evt.index]
