import math

class Model(object):
    def __init__(self, data):
        self.name = data["name"]
        self.creator = data["creator"]["username"]
        self.version = data["modelVersions"][0]["name"]
        self.image = data["modelVersions"][0]["images"][0]["url"]
        self.download_url = data["modelVersions"][0]["downloadUrl"]
        self.type = data["type"]
        self.base_model = data["modelVersions"][0]["baseModel"] # Remove this an just refer to the same value stored in the metadata key
        self.size = convert_size(data["modelVersions"][0]["files"][0]["sizeKB"])
        self.metadata = {
            "description": "",
            "sd version": data["modelVersions"][0]["baseModel"],
            "activation text": get_trigger_words(data["modelVersions"][0]["trainedWords"]),
            "preferred weight": 0,
            "notes": f"https://civitai.com/models/{data['id']}",
        }


def get_trigger_words(words):
    if words:
        return ", ".join(words) + "," # TODO: Ending commas are a personal preference. Create a toggle in settings (low priority)
    else:
        return "" 

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
