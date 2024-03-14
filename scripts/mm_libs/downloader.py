import re
import requests
import gradio as gr
import json
from .model import Model
from .debug import d_print
from tqdm import tqdm
from pathlib import Path
from modules.shared import opts

civit_api = "https://civitai.com/api/v1/models/"
civit_pattern = "(?<=^https:\/\/civitai.com\/models\/)[\d]+|^[\d]+$"

def fetch(model_url) -> list[Model]:
    # Check if API key is present
    if not opts.mm_supress_API_warnings and not opts.mm_civitai_api_key:
        warning = "No API key set. Some models may require authentication to download, please add your API key to the settings. This warning can be supressed in the settings"
        gr.Warning(warning), d_print(warning)

    url = re.search(civit_pattern, model_url)

    if not url:
        warning = "Invalid Input"
        gr.Warning(warning), d_print(warning)
        return

    r = requests.get(civit_api + url[0])

    if not r.ok:
        warning = "Couldn't contact CivitAI API, try again"
        gr.Warning(warning), d_print(warning), d_print(r.status_code)
        return

    try:
        model_data = r.json()
    except json.JSONDecodeError:
        error = "Couldn't decode CivitAI API response, try again. Servers might be down"
        gr.Warning(error), d_print(error)
        return

    model_list = []
    for model_version in model_data["modelVersions"]:
        model_list = model_list + [Model(model_data, model_version)]

    return model_list

def download_model(file_target, model: Model, image):
    d_print("Requesting download from CivitAI")
    
    # Read more about their API Key authentication here: https://education.civitai.com/civitais-guide-to-downloading-via-api/
    r_model = requests.get(model.download_url, headers={"Authorization": f"Bearer {opts.mm_civitai_api_key}"}, stream=True)

    d_print(f"Response Status Code: {r_model.status_code}")

    if r_model.status_code == 401:
        error = "Required authentication failed, please add your Civitai API key in the settings or ensure it is correct"
        gr.Warning(error), d_print(error) # TODO: Should be a error/exception instead of warning
        return
    
    # Retrive file format from the Content-Disposition header
    file_format = r_model.headers["Content-Disposition"].split(".")[-1].strip('"')

    if not r_model.ok:
        warning = "Couldn't contact CivitAI API, try again"
        gr.Warning(warning), d_print(warning), d_print(r_model.status_code)
        return

    r_img = requests.get(image, allow_redirects=True)

    save_file(f"{file_target}.{file_format}", r_model)
    save_file(f"{file_target}.jpeg", r_img)
   
    if  model.type in ("LORA", "LoCon"):
        dump_metadata(file_target, model.metadata)
    d_print("Download Complete")
    return

def save_file(file: str, request: requests.Response):
    total = int(request.headers.get("content-length", 0))
    if Path(file).exists():
        d_print("File already exists, skipping")
        return
    with open(file, "wb") as modelfile, tqdm(
        desc=file.split("\\")[-1],
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in request.iter_content(chunk_size=1024*64):
            size = modelfile.write(chunk)
            bar.update(size)

def dump_metadata(file, metadata):
    with open(f"{file}.json", "w", encoding="utf8") as metafile:
        json.dump(metadata, metafile, indent=4)