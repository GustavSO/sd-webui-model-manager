import os
from pathlib import Path
from modules.shared import cmd_opts, opts

root_path = Path.cwd()
search_depth = -1

# Either assign the default locations, or fetch path to the custom location specified in COMMAND_ARGS=
# Should also check if the path exists, and if not, default to root_path
# TODO: This whole thing could do with a refactor
folders = {
    "TextualInversion": Path(cmd_opts.embeddings_dir) if cmd_opts.embeddings_dir else root_path / "embeddings",
    "Hypernetwork": Path(cmd_opts.hypernetwork_dir) if cmd_opts.hypernetwork_dir else root_path / "models" / "hypernetworks",
    "Checkpoint": Path(cmd_opts.ckpt_dir) if cmd_opts.ckpt_dir else root_path / "models" / "Stable-diffusion",
    "LORA": Path(cmd_opts.lora_dir) if cmd_opts.lora_dir else root_path / "models" / "Lora",
    "LoCon": Path(cmd_opts.lora_dir) if cmd_opts.lora_dir else root_path / "models" / "Lora"
}

original_folders = {model_type: model_dir for model_type, model_dir in folders.items()}

def get_subdirs(dir, depth=1):
    if depth < 1:
        return []
    subdirs = [subdir for subdir in dir.iterdir() if subdir.is_dir()]
    for subdir in subdirs:
        subdirs.extend(get_subdirs(subdir, depth-1))
    return subdirs

def sort_dirs():
    global search_depth
    if opts.mm_folder_depth == search_depth:
        return
    
    folders.update(original_folders)
    for model_type, model_dir in folders.items():
        if not isinstance(model_dir, Path):
            model_dir = Path(model_dir)
        folders[model_type] = [model_dir] + get_subdirs(model_dir, opts.mm_folder_depth)
    search_depth = opts.mm_folder_depth


# TODO: Create a refresh dirs function