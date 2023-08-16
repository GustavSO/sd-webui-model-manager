import os
from pathlib import Path
from modules import shared

folders = {
    "TextualInversion": Path(shared.cmd_opts.embeddings_dir),
    "Hypernetwork": Path(shared.cmd_opts.hypernetwork_dir),
    "Checkpoint": Path(shared.cmd_opts.ckpt_dir),
    "LORA": Path(shared.cmd_opts.lora_dir),
    "LoCon": Path(shared.cmd_opts.lora_dir)
}

# TODO: This could problably be done more elegantly
def get_dirs():
    for model_type, model_dir in folders.items():
        if isinstance(model_dir, Path):
            folders[model_type] = [model_dir] + [subdir for subdir in model_dir.iterdir() if subdir.is_dir()]
