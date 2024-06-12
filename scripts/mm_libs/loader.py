import hashlib
from pathlib import Path

from modules.shared import cmd_opts, opts
from scripts.mm_libs.debug import d_debug
from scripts.mm_libs.model import convert_size
from scripts.mm_libs.storage import FileDetail

HASH_FILE_SUFFIXES = [".safetensors", ".pt", ".ckpt"]

root_path = Path.cwd()
search_depth = opts.mm_folder_depth if opts.mm_folder_depth else 1

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

# TODO: Test if this is still needed
# Relic from when the folders shared directories (e.g. LORA, DoRA, LoCon)
# Might still be useful if a user is storing models in the same directory (don't even know if that's possible)
def get_unique_paths(keys=None):
    reverse_folders = {}
    for key, paths in folders.items():
        for path in paths:
            if path not in reverse_folders:
                reverse_folders[path] = set()
            reverse_folders[path].add(key)

    # Use a set to track unique paths for the given keys
    unique_paths = set()
    for key in keys:
        if key in folders:
            for path in folders[key]:
                unique_paths.add(path)

    # Return the unique paths as a list
    return list(unique_paths)


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

def get_file_details(model_type):
    if model_type not in folders:
        print(f"Model type {model_type} not found")
        return

    file_details = []
    for folder in folders[model_type]:
        for file in folder.iterdir():
            if (
                file.is_file()
                and not file.is_dir()
                and file.suffix in HASH_FILE_SUFFIXES
            ):
                file_detail = FileDetail(
                    filePath=file,
                    fileName=file.name,
                    fileSize=file.stat().st_size,
                    sha256="sha256 encoded string",
                    crc32="crc32 encoded string",
                    blake3="blake3 encoded string",
                    api="custom api string if available",
                )
                # print(f"File Detail [{model_type}]: {file_detail.fileName}")
                file_details.append(file_detail)

    # print(f"Found {len(file_details)} files of type {model_type}")
    return file_details

# def sort_dirs():
#     global search_depth
#     if opts.mm_folder_depth == search_depth:
#         return

#     folders.update(original_folders)
#     for model_type, model_dir in folders.items():
#         if not isinstance(model_dir[0], Path):
#             model_dir[0] = Path(model_dir[0])
#         folders[model_type] = model_dir + get_subdirs(
#             model_dir[0], opts.mm_folder_depth
#         )
#     search_depth = opts.mm_folder_depth

def get_files(path : Path) -> list[Path]:
    files = [file for file in path.iterdir() if file.is_file()]
    return files

def get_hashable_files(path : Path, print_file_details=False) -> list[Path]:
    files = get_files(path)
    hashable_files: list[Path] = []

    for file in files:
        if file.suffix in HASH_FILE_SUFFIXES and not file.is_dir():
            hashable_files.append(file)
            if print_file_details:
                file_size = file.stat().st_size
                converted_size = convert_size(file_size)
                d_debug(f"File: {file.name} - Size: {converted_size}")
            
    d_debug(f"Found {len(hashable_files)} hashable files in {path} \n")
    return hashable_files

# Find every file in all the directories. Only find the files of type .safetensors
def get_models():
    # For now only find all files in "D:\Productivity\AI\Stable Diffusion\models-symlink\Lora\Test"

    subdirs = get_subdirs(lora_dir, 1)
    d_debug(f"Found {len(subdirs)} subdirectories")
    # for subdir in subdirs:
    #     d_debug(subdir)

    # Keep count of each type of file
    model_types = {
        ".safetensors": 0,
        ".json": 0,
        ".jpeg": 0,
        ".txt": 0,
        ".info": 0,
        ".png": 0,
        ".pt": 0,
        ".ckpt": 0,
        ".url": 0,
        "other": 0,
    }

    model_types_to_hash = [".safetensors", ".pt", ".ckpt"]
    models_to_hash = []

    other_files_type = []

    models = []
    for subdir in subdirs:
        for file in subdir.iterdir():
            if file.is_dir():
                continue
            file_suffix = file.suffix
            if file.is_file() and file_suffix in model_types:
                if file_suffix in model_types_to_hash:
                    models_to_hash.append(file)
                models.append(file)
                model_types[file_suffix] += 1
            else:
                other_files_type.append(file_suffix)
                model_types["other"] += 1
                if file_suffix == "":
                    d_debug(f"File with no suffix found: {file}")
                    d_debug(f"Parent directory: {file.parent}")
                    d_debug(f"File name: {file.name}")

    d_debug(f"Found {len(models)} models in the subdirs of {lora_dir}")
    for model_type, count in model_types.items():
        d_debug(f"{model_type}: {count}")

    for file_type in other_files_type:
        d_debug(f"Other file type: {file_type}")

    model_info = {"name": "", "SHA256": ""}

    model_info_list = []

    test_count = 50
    d_debug(f"Generating Hashes for {len(models_to_hash)} models...")
    # Only do the first 50 models for now
    for model in models_to_hash[:test_count]:
        d_debug(f"{models_to_hash.index(model) + 1}/{test_count}")
        hash = gen_hash(model)
        model_info["name"] = model.name
        model_info["SHA256"] = hash
        model_info_list.append(model_info)
    d_debug("Hashes Generated")

    # search_directory = lora_dir / "Test"
    # models = []
    # for file in search_directory.iterdir():
    #     if file.is_file() and file.suffix == ".safetensors":
    #         models.append(file)

    # sort_dirs()
    # models = []
    # for model_type, model_dir in folders.items():
    #     for dir in model_dir:
    #         for file in dir.iterdir():
    #             if file.is_file() and file.suffix == ".safetensors":
    #                 models.append(file)

    # d_debug(f"Found {len(models)} models in {search_directory}")


# TODO: Create a refresh dirs function


def gen_hash(file: Path, print=False):
    # Check if file exists
    if not file.exists() and print:
        d_debug("File not found")
        return

    if print:
        d_debug("File found")

    # Generate Hash
    hasher = hashlib.sha256()
    with open(file, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)

    digest = hasher.hexdigest()

    if not digest and print:
        d_debug("Hash Generation Failed")
        return

    if print:
        d_debug("Hash Generated")
        d_debug(f"Hash: {digest}")
    return digest
