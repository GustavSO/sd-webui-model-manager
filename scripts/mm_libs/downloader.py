import re
import requests
import gradio as gr
import json
from .model import Model
from .debug import d_print
from tqdm import tqdm
from pathlib import Path

civit_api = "https://civitai.com/api/v1/models/"
civit_pattern = "(?<=^https:\/\/civitai.com\/models\/)[\d]+|^[\d]+$"

def fetch(model_url) -> list[Model]:
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

    model_data = r.json()
    model_list = []
    for model_version in model_data["modelVersions"]:
        model_list = model_list + [Model(model_data, model_version)]
        
    return model_list

def download_model(file_target, model: Model, image):
    d_print("Requesting download from CivitAI")

    r_model = requests.get(model.download_url, stream=True)
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