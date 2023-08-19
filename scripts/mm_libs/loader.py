import os
from pathlib import Path
from modules.shared import cmd_opts

root_path = Path.cwd()

# Either assign the default locations, or fetch path to the custom location specified in COMMAND_ARGS=
folders = {
    "TextualInversion": Path(cmd_opts.embeddings_dir) if cmd_opts.embeddings_dir else root_path / "embeddings",
    "Hypernetwork": Path(cmd_opts.hypernetwork_dir) if cmd_opts.hypernetwork_dir else root_path / "models" / "hypernetworks",
    "Checkpoint": Path(cmd_opts.ckpt_dir) if cmd_opts.ckpt_dir else root_path / "models" / "Stable-diffusion",
    "LORA": Path(cmd_opts.lora_dir) if cmd_opts.lora_dir else root_path / "models" / "Lora",
    "LoCon": Path(cmd_opts.lora_dir) if cmd_opts.lora_dir else root_path / "models" / "Lora"
}

def get_dirs():
    for model_type, model_dir in folders.items():
        if isinstance(model_dir, Path):
            folders[model_type] = [model_dir] + [subdir for subdir in model_dir.iterdir() if subdir.is_dir()]


# TODO: Create a refresh dirs function