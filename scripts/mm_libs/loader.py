import os
from pathlib import Path
from modules import shared

root_path = Path.cwd()

folders = {
    "TextualInversion": root_path / "embeddings",
    "Hypernetwork": root_path / "models" / "hypernetworks",
    "Checkpoint": root_path / "models" / "Stable-diffusion",
    "LORA": root_path / "models" / "Lora",
    "LoCon": root_path / "models" / "Lora"
}

# TODO: This could problably be done more elegantly
def get_dirs():
    get_custom_dirs()
    for model_type, model_dir in folders.items():
        if isinstance(model_dir, Path):
            folders[model_type] = [model_dir] + [subdir for subdir in model_dir.iterdir() if subdir.is_dir()]

def get_custom_dirs():
    if shared.cmd_opts.embeddings_dir and Path(shared.cmd_opts.embeddings_dir).is_dir():
        folders["TextualInversion"] = Path(shared.cmd_opts.embeddings_dir)
    if shared.cmd_opts.hypernetwork_dir and Path(shared.cmd_opts.hypernetwork_dir).is_dir():
        folders["Hypernetwork"] = Path(shared.cmd_opts.hypernetwork_dir)
    if shared.cmd_opts.ckpt_dir and Path(shared.cmd_opts.ckpt_dir).is_dir():
        folders["Checkpoint"] = Path(shared.cmd_opts.ckpt_dir)
    if shared.cmd_opts.lora_dir and Path(shared.cmd_opts.lora_dir).is_dir():
        folders["LORA"] = Path(shared.cmd_opts.lora_dir)
        folders["LoCon"] = Path(shared.cmd_opts.lora_dir)