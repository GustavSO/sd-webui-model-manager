from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from pathlib import Path
import json
from zlib import crc32

from blake3 import blake3
import requests

from modules import scripts
from scripts.mm_libs import loader
from scripts.mm_libs.debug import Color, d_debug, d_info, d_message
from scripts.mm_libs.model import convert_size
from scripts.mm_libs.storage import Storage, FileDetail
from scripts.mm_libs.utilities import get_obj_size

storage_instance = Storage()


# TODO: This is not used, consider removing if there is no obvious use case
def prepare_files(model_types) -> dict:
    """Prepares files of the specified types without updating the cache"""

    storage_instance.clear()

    total_files = 0
    for model_type in model_types:
        paths = loader.get_all_files_of_type(
            model_type, valid_suffix=[".pt", ".safetensors", ".ckpt"]
        )
        file_details = []

        for path in paths:
            file_detail = FileDetail(
                filePath=path,
                fileName=path.name,
                fileSize=path.stat().st_size,
                sha256="",
                crc32="",
                blake3="",
                api="",
            )
            file_details.append(file_detail)

        storage_instance.add_files_by_type(model_type, file_details)
        total_files += len(file_details)
    print(f"Added {total_files} files to storage\n")
    return storage_instance.to_dict(ui_friendly=True)


def update_cache_file(types) -> dict:
    """Update the cache file with new files of the specified types. Checks for existing files before adding them to the cache."""
    d_message("Updating cache...")
    total_files = 0
    for model_type in types:
        # d_message(f"Updating cache for {model_type}")
        paths = loader.get_all_files_of_type(
            model_type, valid_suffix=[".pt", ".safetensors", ".ckpt"]
        )
        file_details = []

        cleaned_paths = storage_instance.filter_existing_files(model_type, paths)
        if not cleaned_paths:
            d_message(f"{model_type}: cache is up to date")
            continue

        d_message(
            f"{model_type}: {len(cleaned_paths)} new files found. Adding to cache..."
        )

        for path in cleaned_paths:
            file_detail = FileDetail(
                filePath=path,
                fileName=path.name,
                fileSize=path.stat().st_size,
                sha256="",
                crc32="",
                blake3="",
                api="",
            )
            file_details.append(file_detail)

        storage_instance.add_files_by_type(model_type, file_details)
        total_files += len(file_details)

    if total_files == 0:
        d_message("No new files added to cache\n")
        return storage_instance.to_dict(ui_friendly=True)

    storage_instance.update_cache_file()
    d_message(f"Added {total_files} new files to cache\n")
    return storage_instance.to_dict(ui_friendly=True)


################
# File hashing #
################
def reverse_byte_order(crc):
    # Convert CRC-32 integer to bytes, reverse the bytes, and then convert back to hex string
    crc_bytes = crc.to_bytes(4, byteorder="big")
    reversed_bytes = crc_bytes[::-1]
    return reversed_bytes.hex()


def hash_file(file, algorithm):
    """Hash a single file using the specified algorithm."""

    with open(file, "rb") as f:
        data = f.read()

    match algorithm:
        case "crc32":
            crc_value = crc32(data) & 0xFFFFFFFF  # Ensure CRC-32 is a 32-bit value
            return reverse_byte_order(crc_value)
        case "blake3":
            return blake3(data).hexdigest()
        case "sha256":
            return sha256(data).hexdigest()
        case _:
            raise ValueError(f"Unknown algorithm: {algorithm}")


def hash_files(files, algo) -> dict:
    """Hash a collection of files using the specified algorithm."""
    results = {}
    for file in files:
        d_message(f"{files.index(file) + 1}/{len(files)} - {file.name}")
        try:
            results[file] = hash_file(file, algo)
        except Exception as e:
            results[file] = f"Error: {e}"
    return results


# TODO: Look into the MissingModuleError
def hash_files_concurrently(file_paths, algorithm) -> dict:
    """Hash a collection of files concurrently using the specified algorithm."""
    raise NotImplementedError("Concurrent hashing is not yet implemented")
    results = {}
    d_debug(f"Beginning hashing of {len(file_paths)} files using {algorithm}")
    with ProcessPoolExecutor() as executor:
        future_to_file = {
            executor.submit(hash_file, file_path, algorithm): file_path
            for file_path in file_paths
        }
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                results[file_path] = future.result()
                # if OPTS_PRINT_HASHING:
                #     print(f"Hashed {file_path}")
            except Exception as exc:
                results[file_path] = f"Error: {exc}"
    return results


def perform_hashing(model_types, algorith, multi_process) -> dict:
    for type in model_types:
        if not storage_instance.contains_model_type(type):
            d_debug(f"No files of type {type} found")
            continue

        # TODO: Fix the bug where if the files are already hashed with a different algorithm, the size calculations in Storage, essentially breaking the cache file
        unhashed_files = storage_instance.get_non_hashed_files_by_type(type)
        # unhashed_files = storage_instance.get_non_hashed_files_by_type_and_algorithm(type, algorith)

        if not unhashed_files:
            d_message(f"{type}: All files are already hashed using {algorith}")
            continue

        d_message(
            f"Found {len(unhashed_files)}/{storage_instance.get_type_count(type)} unhashed {type} files"
        )

        file_paths = [file.filePath for file in unhashed_files]
        if multi_process:
            # TODO: Implement multi-processing
            hash_results = hash_files_concurrently(file_paths, algorith)
        d_message(f"Hashing {len(file_paths)} {type} files using {algorith}:")
        hash_results = hash_files(file_paths, algorith)

        for file_path, hash_value in hash_results.items():
            storage_instance.add_hash_to_file_by_model(
                type, file_path, algorith, hash_value
            )

        storage_instance.update_cache_file()
        d_message(f"Finished hashing {len(hash_results)} {type} files using {algorith}\n")

    d_info("Hashing complete\n")
    return storage_instance.to_dict(ui_friendly=True)


def validate_model_json(model_path: Path) -> bool:
    """Check if the model has a json file with a "model url" in it"""
    json_file = model_path.with_suffix(".json")
    d_message(f"Checking {model_path.name}...")

    if not json_file.exists():
        d_debug(f"No JSON file found for {model_path.name}", Color.RED)
        return False

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "model url" in data:
            d_debug(f"Model URL found for {model_path.name}", Color.GREEN)
            return True
        d_debug(f"No Model URL found for {model_path.name}", Color.YELLOW)
        return False


def check_civitai():
    api = "https://civitai.com/api/v1/model-versions/by-hash/"

    initial_files = storage_instance.get_all_hashed_files()

    d_debug(f"Found {len(initial_files)} with hashes", Color.GREEN)

    cleaned_files = [
        file for file in initial_files if not validate_model_json(Path(file.filePath))
    ]

    if not cleaned_files:
        d_info("All models already have a model URL\n")
        return

    if (len(initial_files) - len(cleaned_files)) > 0:
        d_message(
            f"{len(initial_files) - len(cleaned_files)}/{len(initial_files)} files already have a model URL. Skipping..."
        )

    d_message(f"Checking {len(cleaned_files)} against Civitai API...:")

    files_updated = 0
    for file in cleaned_files:
        d_message(
            f"{cleaned_files.index(file) + 1}/{len(cleaned_files)} - {file.fileName}"
        )
        request = f"{api}{file.get_hash()}"
        response = requests.get(request)

        if response.status_code == 404:
            d_message(f"Error: Model {file.fileName} not found on Civitai\n")
            continue
        elif response.status_code != 200:
            d_message(f"Error: {response.status_code} \n")
            continue

        d_debug(f"Success: {response.status_code}", Color.GREEN)

        json_data = response.json()
        id = json_data["id"]
        model_id = json_data["modelId"]

        civit_page = f"https://civitai.com/models/{model_id}?modelVersionId={id}"
        update_model_json(Path(file.filePath), civit_page)
        files_updated += 1

    d_info(f"Civitai check complete - {files_updated} models updated\n")
    return


def update_model_json(model_path: Path, page: str = None):
    # Get the json file that is stored beside the model using the same name
    json_file = model_path.with_suffix(".json")

    # If it doesn't exist, create it and add the model url
    if not json_file.exists():
        d_debug(f"No JSON file found for {model_path.name}", Color.RED)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"model url": page}, f, indent=4)
            d_debug(f"Created JSON file for {model_path.name}", Color.YELLOW)
            d_message(f"Success: Model URL added to {model_path.name} \n")
        return

    # If it exists, add the model url to it
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["model url"] = page
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
            d_debug(f"Model URL added to {model_path.name}", Color.GREEN)
            d_message(f"Success: Model URL added to {model_path.name} \n")


def purge_cache():
    storage_instance.purge_cache()


def get_storage_size():
    d_message(
        f"Storage size: {get_obj_size(storage_instance)} bytes or {convert_size(get_obj_size(storage_instance))}\n"
    )
