import modules.scripts as scripts
from pathlib import Path
import json


settings_file = Path(scripts.basedir(), "settings.json")

settings = {
    "auto_paste": True,
    "allow_NSFW": False,
}

def save_settings():
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)
    
def load_settings():
    global settings
    # Only happens on first run, or if the settings file is deleted
    if not settings_file.exists():
        save_settings()
    else:
        with open(settings_file, "r") as f:
            settings = json.load(f)


def change_settings(auto_paste, allow_nsfw):
    global settings
    settings["auto_paste"] = auto_paste
    settings["allow_NSFW"] = allow_nsfw
    save_settings()