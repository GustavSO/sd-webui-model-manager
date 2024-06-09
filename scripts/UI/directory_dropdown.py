import os
import gradio as gr

from modules.shared import opts
from scripts.mm_libs.debug import d_print
from scripts.mm_libs.loader import folders

from pathlib import Path


# Reusable Gradio Dropdown for selecting target directories
class Directory_Dropdown:
    def __init__(self) -> None:
        self.short_dirs = []
        self.selected_dir = None  # Used by card.py to get the selected directory
        self.update_value = None

        self.model_type = None
        self.main_tag = None

        self.changed = False
        self.path: Path = None
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
        self.js_init_dropdown_btn = gr.Button(
            "False", visible=False, elem_id="js_init_dir_dropdown"
        )
        self.js_init_dropdown_btn.click(
            self.init_dropdown, outputs=self.js_init_dropdown_btn
        )

    def get_components(self):
        return self.dropdown

    # Should only update the dropdown if the directory has changed or the dropdown has been initialized.
    def get_updates(self):
        if self.changed or self.init:
            self.changed = False
            self.init = False
            return gr.Dropdown.update(value=self.update_value, choices=self.short_dirs)
        else:
            return gr.Dropdown.update()

    # Updates the choices of the directory dropdown based on the type of model fetched.
    def update_choices(self, model_type: str, main_tag: str):

        option_path = check_options(model_type, main_tag)
        if option_path:
            s_option_path = shorten_path(option_path, folders[model_type][0].parent)
            d_print(f"Options path: {option_path}")
            d_print(f"Shortened path: {s_option_path}")



        if self.path == folders[model_type][0] and self.main_tag == main_tag:
            return self.short_dirs

        self.path = folders[model_type][0]
        self.changed = True
        self.model_type = model_type
        self.main_tag = main_tag

        self.short_dirs = [
            os.path.relpath(dir, self.path.parent) for dir in folders[model_type]
        ]

        if option_path and s_option_path in self.short_dirs:
            d_print(f"Options path in short dirs: {s_option_path}")
            self.selected_dir = option_path
            self.update_value = s_option_path
            return

        self.update_value = self.short_dirs[0]
        self.selected_dir = folders[model_type][0]

    def change_directory(self, evt: gr.SelectData):
        self.selected_dir = folders[self.model_type][evt.index]

    def init_dropdown(self):
        self.init = True
        return "True"


def check_options(model_type: str, main_tag: str) -> Path:
    # Quick fix to make sure that DoRA and LoCon are treated as LORA
    if model_type.lower() in ["dora", "locon"]:
        model_type = "lora"

    options_name = f"opts.mm_af_{model_type.lower()}_{main_tag}"
    d_print(f"Checking options for {options_name}")
    try:
        value: str = eval(options_name) if eval(options_name) else "Option not set"
    except Exception as e:
        d_print(f"Error fetching value from options: {e}")
        return

    option_path = Path(value)
    if not option_path.exists():
        d_print(f"Path from options does not exist: {option_path}")
        return

    return option_path


def shorten_path(path: Path, parent: Path) -> str:
    return os.path.relpath(path, parent)
