import os
import gradio as gr

from modules.shared import opts
from scripts.mm_libs.debug import d_debug, d_message, d_warn
from scripts.mm_libs.loader import folders

from pathlib import Path
from modules.ui_components import ToolButton
import subprocess


FOLDER_SYMBOL = '\U0001f4c1\ufe0f' #📁

# Reusable Gradio Dropdown for selecting target directories
class Directory_Dropdown:
    def __init__(self) -> None:
        self.selected_dir = None  # Used by card.py to get the selected directory
        self.update_value = None

        self.model_type = None
        self.main_tag = None

        # Gradio Structure
        with gr.Row():
            self.dropdown = gr.Dropdown(
                label="Directory",
                info="Select the target directory for the file(s).",
                choices=[],
                interactive=True,
            )
            open_folder_btn = ToolButton(FOLDER_SYMBOL, tooltip="Open Folder")

        self.dropdown.select(self.change_directory)
        open_folder_btn.click(self.open_folder)

    def get_components(self):
        return self.dropdown

    # Should only update the dropdown if the directory has changed or the dropdown has been initialized.
    def get_updates(self):
        return gr.Dropdown.update(
            value=self.update_value, choices=get_short_dirs(self.model_type)
        )

    def update_choices(self, model_type: str, main_tag: str):
        model_type = process_model_type(model_type)

        # If the path and main tag are the same as the previous, skip the update 
        # TODO: Fix it so that the dropdown will still update even if the type and tag are the same BUT the update_value (dropdown value) is different from the options path
        if compare_model(self.model_type, model_type) and self.main_tag == main_tag:
            return

        option_path = check_options(model_type, main_tag)
        self.model_type = model_type
        self.main_tag = main_tag

        if option_path and option_path in folders[model_type]:
            d_debug(f"Options path in folders: {option_path}")
            self.update_value = shorten_path(option_path, folders[model_type][0].parent)
            self.selected_dir = option_path
            return

        self.update_value = get_short_dirs(model_type)[0]
        self.selected_dir = folders[model_type][0]

    def change_directory(self, evt: gr.SelectData):
        self.selected_dir = folders[self.model_type][evt.index]
        self.update_value = shorten_path(
            self.selected_dir, folders[self.model_type][0].parent
        )
    
    def open_folder(self):
        if self.selected_dir:
            subprocess.Popen(f'explorer "{self.selected_dir}"')
        else:
            d_warn("No directory selected. Cannot open folder.")




def check_options(model_type: str, main_tag: str) -> Path:
    # Quick fix to make sure that DoRA and LoCon are treated as LORA
    if model_type.lower() in ["dora", "locon"]:
        model_type = "lora"

    options_name = f"opts.mm_af_{model_type.lower()}_{main_tag}"
    d_debug(f"Checking options for {options_name}")
    try:
        value: str = eval(options_name) if eval(options_name) else "Option not set"
    except Exception as e:
        d_debug(f"Error fetching value from options: {e}")
        return

    option_path = Path(value)
    if not option_path.exists():
        d_debug(f"Path from options does not exist: {option_path}")
        return

    return option_path


def compare_model(model_type1: str, model_type2: str) -> bool:
    if not model_type1 or not model_type2:
        d_debug("Model type not set")
        return False

    if model_type1 == model_type2:
        d_debug("Model types are the same")
        return True

    if model_type1.lower() in ["dora", "locon"]:
        model_type1 = "lora"

    if model_type2.lower() in ["dora", "locon"]:
        model_type2 = "lora"

    return model_type1.lower() == model_type2.lower()


def process_model_type(model_type: str) -> str:
    if model_type.lower() in ["dora", "locon"]:
        d_debug("Model type is DoRA or LoCon. Reading as LORA")
        return "LORA"

    return model_type

def shorten_path(path: Path, parent: Path) -> str:
    return os.path.relpath(path, parent)

def get_short_dirs(model_type: str) -> list[str]:
    return [
        os.path.relpath(dir, folders[model_type][0].parent)
        for dir in folders[model_type]
    ]
