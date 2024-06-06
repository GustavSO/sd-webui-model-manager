import math
import re
import time
import requests
import gradio as gr
import json

from .model import Model, convert_size
from .debug import d_info, d_print, d_warn
from tqdm import tqdm
from pathlib import Path
from modules.shared import opts

civit_api = "https://civitai.com/api/v1/models/"
civit_api_alt = "https://civitai.com/api/v1/model-versions/"
civit_pattern = "(?<=^https:\/\/civitai.com\/models\/)[\d]+|^[\d]+$"


# Fetches model data from CivitAI API.
# Returns a list of Model objects used to display the model info in the Card components
# TODO: Add support for retrieving sub models directly
# TODO: Clean up the code, it's a mess
def fetch(model_url) -> list[Model]:
    # Check if API key is present
    if not opts.mm_supress_API_warnings and not opts.mm_civitai_api_key:
        info = "No API key set. Some models may require authentication to download, please add your API key to the settings. This warning can be supressed in the settings"
        d_info(info)

    url = re.search(civit_pattern, model_url)

    if not url:
        d_warn(
            "Invalid URL, please enter a valid CivitAI model URL or ID. Example: https://civitai.com/models/1234 or 1234"
        )
        return

    r = requests.get(civit_api + url[0])

    if not r.ok:
        d_warn("Couldn't contact CivitAI API, try again")
        return

    try:
        model_data = r.json()
    except json.JSONDecodeError:
        d_warn("Couldn't decode CivitAI API response, try again. Servers might be down")
        d_print(f"Error: {r.status_code} - {r.text}")
        return

    model_list = []
    for model_version in model_data["modelVersions"]:
        model_list = model_list + [Model(model_data, model_version)]

    return model_list


def download_model(file_target, model: Model, image, progress):
    d_print("Requesting download from CivitAI")

    # Read more about their API Key authentication here: https://education.civitai.com/civitais-guide-to-downloading-via-api/
    r_model = requests.get(
        model.download_url,
        headers={"Authorization": f"Bearer {opts.mm_civitai_api_key}"},
        stream=True,
    )

    d_print(f"Response Status Code: {r_model.status_code}")

    if r_model.status_code == 401:
        error = "Required authentication failed, please add your Civitai API key in the settings or ensure it is correct"
        gr.Warning(error)
        return

    # Retrive file format from the Content-Disposition header
    file_format = r_model.headers["Content-Disposition"].split(".")[-1].strip('"')

    if not r_model.ok:
        warning = "Couldn't contact CivitAI API, try again"
        error = f"Error: {r_model.status_code} - {r_model.text}"
        d_warn(warning), d_print(error)
        return

    save_file(f"{file_target}.{file_format}", r_model, progress)

    if image:
        r_img = requests.get(image, allow_redirects=True)
        save_file(f"{file_target}.jpeg", r_img, progress)

    if model.type in ("LORA", "LoCon", "DoRA"):
        dump_metadata(file_target, model.metadata)

    d_info("Download Complete")


def save_file(file: str, request: requests.Response, progress):
    total = int(request.headers.get("content-length", 0))
    
    if Path(file).exists():
        d_warn(
            "A file with the same name already exists, skipping download. File: " + file
        )
        return

    with open(file, "wb") as modelfile, tqdm(
        desc=file.split("\\")[-1],
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in request.iter_content(chunk_size=1024 * 64):
            size = modelfile.write(chunk)

            downloaded_size = convert_size((bar.n + size))
            total_size = convert_size(total)
            speed = (
                f"Speed: {convert_size(bar.format_dict['rate'])}/s"
                if bar.format_dict["rate"]
                else "N/A"
            )

            if bar.n > 0:
                eta = (total - bar.n) * bar.format_dict.get("elapsed", 0) / bar.n
                formatted_eta = "ETA: " + time.strftime("%H:%M:%S", time.gmtime(eta))
            else:
                formatted_eta = "ETA: N/A"

            description = f"{bar.desc} - {downloaded_size}/{total_size} - {speed} - {formatted_eta}"
            progress((bar.n + size) / total, desc=description)
            bar.update(size)


def dump_metadata(file, metadata):
    with open(f"{file}.json", "w", encoding="utf8") as metafile:
        json.dump(metadata, metafile, indent=4)

