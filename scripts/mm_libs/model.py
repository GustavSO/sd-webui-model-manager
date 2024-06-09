import math

from modules.shared import opts

# TODO: Add a "recommended strength" field to the metadata
# Could also expand with additional data like EPOCHS, Reviews, etc.

# Main tags used by Civitai taken from their website
main_civitai_tags = [
    "character",
    "style",
    "celebrity",
    "concept",
    "clothing",
    "base model",
    "poses",
    "background",
    "tool",
    "buildings",
    "vehicle",
    "objects",
    "animal",
    "action",
    "assets",
]



class Model(object):
    def __init__(self, data, model_version):
        self.name = data["name"]
        self.creator = data["creator"]["username"]
        self.version = model_version["name"]
        self.images = get_images(model_version["images"])
        self.selected_image = (  # This is so stupid, fix this with some js somehow or something
            self.images[0][0] if self.images else None
        )
        self.download_url = model_version["downloadUrl"]
        self.type = data["type"]
        self.size = convert_size(model_version["files"][0]["sizeKB"]*1024)
        self.main_tag = get_main_tag(data["tags"])
        self.metadata = {
            "description": "",
            "sd version": model_version["baseModel"],
            "activation text": (
                get_trigger_words(model_version["trainedWords"])
                if "trainedWords" in model_version
                else ""
            ),
            "preferred weight": 0,
            # Stores the model url both in the notes, visible in the UI, but also in a model url field for easy access.
            "notes": f"https://civitai.com/models/{data['id']}?modelVersionId={model_version['id']}",
            "model url": f"https://civitai.com/models/{data['id']}?modelVersionId={model_version['id']}"
        }
        print(f"Main Tag: {self.main_tag}\n")

    def __str__(self):
        return f"{self.name} {self.version} ({self.creator})"


# TODO: Look into why the trigger words aren't cleaned up properly (single spacing and comma)
def get_trigger_words(words):
    if words:
        cleaned_words = [word.rstrip(" ,") for word in words]
        return ", ".join(cleaned_words) + ", "
    else:
        return ""

def get_main_tag(tags):
    for tag in tags:
        if tag in main_civitai_tags:
            return tag

    return "None"

def convert_size(size):
    if size == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return "%s %s" % (s, size_name[i])

def get_images(image_json):
    # Make sure to only load the amount specified in the settings
    amount = opts.mm_image_amount
    image_json = image_json[:amount] if amount > 0 else image_json

    if opts.mm_allow_NSFW:
        return [(i["url"], i["url"]) for i in image_json]
    else:
        return [(i["url"], i["url"]) for i in image_json if i["nsfw"] == "None"]