import hashlib
from pathlib import Path

from modules.shared import cmd_opts, opts
from scripts.mm_libs.debug import d_debug
from scripts.mm_libs.model import convert_size
from scripts.mm_libs.storage import FileDetail

HASH_FILE_SUFFIXES = [".safetensors", ".pt", ".ckpt"]

root_path = Path.cwd()

try:
    search_depth = opts.mm_folder_depth if opts.mm_folder_depth else 1
except AttributeError:
    search_depth = 1

embeddings_dir = Path(cmd_opts.embeddings_dir) if cmd_opts.embeddings_dir else root_path / "embeddings"
hypernetwork_dir = Path(cmd_opts.hypernetwork_dir) if cmd_opts.hypernetwork_dir else root_path / "models" / "hypernetworks"
ckpt_dir = Path(cmd_opts.ckpt_dir) if cmd_opts.ckpt_dir else root_path / "models" / "Stable-diffusion"
lora_dir = Path(cmd_opts.lora_dir) if cmd_opts.lora_dir else root_path / "models-symlink" / "Lora"

def get_subdirs(dir, depth=1):
    if depth < 1:
        return []
    subdirs = [subdir for subdir in dir.iterdir() if subdir.is_dir()]
    for subdir in subdirs:
        subdirs.extend(get_subdirs(subdir, depth - 1))
    return subdirs

folders = {
    "TextualInversion": [embeddings_dir] + get_subdirs(embeddings_dir, search_depth),
    "Hypernetwork": [hypernetwork_dir] + get_subdirs(hypernetwork_dir, search_depth),
    "Checkpoint": [ckpt_dir] + get_subdirs(ckpt_dir, search_depth),
    "LORA": [lora_dir] + get_subdirs(lora_dir, search_depth),
    # "LoCon": [lora_dir] + get_subdirs(lora_dir, search_depth),
    # "DoRA": [lora_dir] + get_subdirs(lora_dir, search_depth) # Keeping this for now, will be removed if no conflicts arise
}


def get_all_files_of_type(model_type, valid_suffix=HASH_FILE_SUFFIXES) -> list[Path]:
    if model_type not in folders:
        print(f"Model type {model_type} not found")
        return
    files = []
    for folder in folders[model_type]:
        for file in folder.iterdir():
            if file.is_file() and (not valid_suffix or file.suffix in valid_suffix):
                files.append(file)
    return files
# TODO: Create a refresh dirs function