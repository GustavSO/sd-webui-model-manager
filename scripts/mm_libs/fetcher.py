import re
import requests
import json

from .model import Model
from .debug import d_debug, d_info, d_message, d_warn
from modules.shared import opts

civit_api = "https://civitai.com/api/v1/models/"
civitai_model_id_version_pattern = r"https:\/\/civitai.com\/models\/(\d+)(?:\?modelVersionId=(\d+))?"

def fetch(model_url) -> list[Model]:
    """
    Fetches model data from CivitAI API based on the model URL or ID.
    Returns a list of Model instances and the index of a specific version if provided.
    """

    d_debug(f"Fetching model data from CivitAI API: {model_url}")
    check_api_key()

    model_id, version_number = url_to_id_version(model_url)
    if model_id is None:
        d_warn("Invalid URL or ID. Please enter a valid CivitAI model URL or ID.")
        return None, None

    full_url = civit_api + model_id
    model_data = get_model_data(full_url)
    if model_data is None:
        return None, None

    model_list, index = process_model_versions(model_data, version_number)
    return model_list, index


def check_api_key():
    """Checks if the API key is set and warns if not."""
    if not opts.mm_supress_API_warnings and not opts.mm_civitai_api_key:
        d_info("No API key set. Some models may require authentication to download.")

def get_model_data(model_url):
    """Performs the API request to get model data."""
    response = requests.get(model_url)

    if response.status_code == 404:
        d_warn("Model not found. Please check the model URL or ID."), d_message(f"Error: {response.status_code} - {response.text}. Sometimes the model isn't available through the API. In that case, a manual download is needed. Sorry")
        return None

    if not response.ok:
        d_warn("Couldn't contact CivitAI API, try again."), d_message(f"Error: {response.status_code} - {response.text}")
        return None
    try:
        return response.json()
    except json.JSONDecodeError:
        d_warn("Couldn't decode CivitAI API response, try again."), d_message(f"Error: {response.status_code} - {response.text}")
        return None

def process_model_versions(model_data, version_number):
    """
    Processes model versions from the API response.
    Returns a list of Model instances and the index of a specific version if provided.
    """
    index = 0
    if version_number:
        index = find_version_index(model_data["modelVersions"], version_number)

    model_list = [Model(model_data, version) for version in model_data["modelVersions"]]
    return model_list, index

def find_version_index(model_versions, version_number):
    """Finds the index of a specific model version."""
    for version in model_versions:
        if version["id"] == int(version_number):
            d_debug(f"Version number found: {version_number}, index: {version['index']}")
            return version["index"]
    return 0


def url_to_id_version(url) -> tuple[str, str]:
    '''Extracts the model ID and version number from a Civitai URL or a standalone number.'''

    if url.isdigit():
        return url, None
    
    match = re.search(civitai_model_id_version_pattern, url)
    if match:
        model_id, version_number = match.groups()
        return model_id, version_number

    return None, None
