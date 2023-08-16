import re
import requests
import gradio as gr
import json
from . import model
from tqdm import tqdm

current_model = None

civit_api = "https://civitai.com/api/v1/models/"
civit_pattern = "(?<=^https:\/\/civitai.com\/models\/)[\d]+|^[\d]+$"


def fetch(model_url):
    url = re.search(civit_pattern, model_url)

    if not url:
        warning = "Model Manager: Invalid input"
        gr.Warning(warning), print(warning)
        return

    r = requests.get(civit_api + url[0])
    if not r.ok:
        warning = "Model Manager: Couldn't contact CivitAI API, try again"
        gr.Warning(warning), print(warning)
        return

    model_data = r.json()

    update_current_model(model_data)
    return (current_model, get_images(model_data["modelVersions"][0]["images"]))

def update_current_model(data):
    global current_model
    match data["type"]:
        case "LORA":
            current_model = model.Lora(data)
        case _:
            current_model = model.Model(data)


def get_images(image_json):
    return [(i["url"], i["url"]) for i in image_json]


def download(file_target):
    print("Model Manager: Starting Download")

    r_model = requests.get(current_model.download_url, stream=True)
    # Retrive file format from the Content-Disposition header
    file_format = r_model.headers["Content-Disposition"].split(".")[-1].strip('"')

    if not r_model.ok:
        warning = "Model Manager: Couldn't contact CivitAI API, try again"
        gr.Warning(warning), print(warning)
        return

    r_img = requests.get(current_model.image, allow_redirects=True)

    save_file(f"{file_target}.{file_format}", r_model)
    save_file(f"{file_target}.jpeg", r_img)

    if isinstance(current_model, model.Lora):
        dump_metadata(file_target, current_model.metadata)
    print("Model Manager: Download Complete")
    return

def save_file(file: str, request: requests.Response):
    total = int(request.headers.get("content-length", 0))
    with open(file, "wb") as modelfile, tqdm(
        desc=file.split("\\")[-1],
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in request.iter_content(chunk_size=1024):
            size = modelfile.write(chunk)
            bar.update(size)

def dump_metadata(file, metadata):
    with open(f"{file}.json", "w", encoding="utf8") as metafile:
        json.dump(metadata, metafile, indent=4)