class Model(object):
    def __init__(self, data):
        self.name = data["name"]
        self.creator = data["creator"]["username"]
        self.version = data["modelVersions"][0]["name"]
        self.image = data["modelVersions"][0]["images"][0]["url"]
        self.download_url = data["modelVersions"][0]["downloadUrl"]
        self.type = data["type"]
        self.base_model = data["modelVersions"][0]["baseModel"] # Repeat storage in case of Lora, as it is also stored in it's metadata key

class Lora(Model):
    def __init__(self, data):
        super().__init__(data)
        self.metadata = {
            "description": "",
            "sd version": data["modelVersions"][0]["baseModel"],
            "activation text": ", ".join(data["modelVersions"][0]["trainedWords"]) + ", " if data["modelVersions"][0]["trainedWords"] else "" ,
            "preferred weight": 0,
            "notes": f"https://civitai.com/models/{data['id']}"
        }
