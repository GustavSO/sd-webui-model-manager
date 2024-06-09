import time
import gradio as gr
import browser_cookie3
import os

from scripts.mm_libs.debug import *
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By

from .downloader import fetch
from .model import Model

from modules import shared



models_list: list[list[Model]] = []

civitai_driver = None

def create_civitai_session():
    global civitai_driver

    os.environ['GH_TOKEN'] = shared.opts.mm_github_token
    
    if os.environ.get("GH_TOKEN") is None:
        raise Exception("GH_TOKEN environment variable is not set. Please set it to use this feature")
    
    d_message("Creating Civitai Session using Selenium...")

    # Is this needed?
    options = FirefoxOptions()

    url = "https://civitai.com/user/notifications"

    civitai_driver = webdriver.Firefox(options=options, service=FirefoxService(GeckoDriverManager().install()))
    civitai_driver.get(url)

    # Gets cookies from Browser
    cookiejar = browser_cookie3.load(domain_name="civitai.com")

    for cookie in cookiejar:
        civitai_driver.add_cookie({"name": cookie.name, "value": cookie.value})
    
    civitai_driver.refresh()
    civitai_driver.switch_to.window(civitai_driver.current_window_handle)


# Use the get models?ids=48139&ids=25995 api, example:
# https://civitai.com/api/v1/models?ids=48139&ids=25995
def get_page_source() -> list[list[Model]]:
    global civitai_driver
    
    if civitai_driver is None:
        raise Exception("Civitai Session not created. Please create it first using 'Create Civitai Session' button")
    
    d_message("Fetching models from Civitai...")
    notifications = civitai_driver.find_elements(By.CSS_SELECTOR, "a.mantine-Text-root.mantine-1nqtos1")
    scaped_models = []
    model_ids = []
    for notification in notifications:
        if "articles" in notification.get_attribute("href"):
            d_message("unsupported format or model type. Skipping...")
            continue
        d_message(f"Fetching model info for: {notification.get_attribute('href')}")
        model_ids.append(notification.get_attribute("href").split("/")[-1])
        scaped_models.append(fetch(notification.get_attribute("href")))
        time.sleep(1)
    d_message(f"Finished fetching models!. Found {len(model_ids)} models supported models")
    return scaped_models