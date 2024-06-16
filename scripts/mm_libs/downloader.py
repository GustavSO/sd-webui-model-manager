import time
import requests
import json

from .model import Model, convert_size
from .debug import d_debug, d_info, d_message, d_warn
from tqdm import tqdm
from pathlib import Path
from modules.shared import opts


def download_model(file_target, model: Model, image_url, progress_callback):
    """
    Initiates the download of a model and its image if provided.
    """
    d_message("Requesting download from CivitAI")
    model_response = fetch_model_data(model.download_url)

    if model_response is None:
        return

    file_format = extract_file_format(model_response)
    save_file(f"{file_target}.{file_format}", model_response, progress_callback)

    if image_url:
            image_response = fetch_image_data(image_url)
            save_file(f"{file_target}.jpeg", image_response, progress_callback)

    if model.type in ("LORA", "LoCon", "DoRA"):
        dump_metadata(file_target, model.metadata)

    d_info("Download Complete")


def fetch_model_data(download_url):
    """
    Fetches model data from the given download URL.
    """
    response = requests.get(
        download_url,
        headers={"Authorization": f"Bearer {opts.mm_civitai_api_key}"},
        stream=True,
    )

    if response.status_code == 401:
        d_warn("Required authentication failed, please add your Civitai API key in the settings or ensure it is correct")
        return None

    if not response.ok:
        d_warn(f"Couldn't contact CivitAI API, try again."), d_message(f"Error: {response.status_code} - {response.text}")
        return None

    return response


def fetch_image_data(image_url):
    """
    Fetches image data from the given URL.
    """
    return requests.get(image_url, allow_redirects=True)


def extract_file_format(response):
    """
    Extracts the file format from the Content-Disposition header of the response.
    """
    return response.headers["Content-Disposition"].split(".")[-1].strip('"')


def save_file(file_path, response, progress_callback):
    """
    Saves the file from the response to the given file path, updating progress.
    """
    if Path(file_path).exists():
        d_warn(f"{file_path} already exists, skipping download")
        return

    total_size = int(response.headers.get("content-length", 0))
    with open(file_path, "wb") as file, tqdm(
        desc=Path(file_path).name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=1024 * 64):
            file.write(chunk)
            update_progress(progress_bar, chunk, total_size, progress_callback)


def update_progress(progress_bar, chunk, total_size, progress_callback):
    """
    Updates the progress bar and callback with the current download progress.
    """
    progress_bar.update(len(chunk))
    downloaded_size = convert_size(progress_bar.n)
    total_size_formatted = convert_size(total_size)
    speed = f"Speed: {convert_size(progress_bar.format_dict['rate'])}/s" if progress_bar.format_dict["rate"] else "N/A"
    eta = calculate_eta(progress_bar, total_size)
    description = f"{progress_bar.desc} - {downloaded_size}/{total_size_formatted} - {speed} - ETA: {eta}"
    progress_callback(progress_bar.n / total_size, desc=description)


def calculate_eta(progress_bar, total_size):
    """
    Calculates the estimated time of arrival (ETA) for the download.
    """
    if progress_bar.n > 0:
        eta_seconds = (total_size - progress_bar.n) * progress_bar.format_dict.get("elapsed", 0) / progress_bar.n
        return time.strftime("%H:%M:%S", time.gmtime(eta_seconds))


def dump_metadata(file_target, metadata):
    """
    Dumps the model metadata into a JSON file.
    """
    with open(f"{file_target}.json", "w", encoding="utf8") as metafile:
        json.dump(metadata, metafile, indent=4)