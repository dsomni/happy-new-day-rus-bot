import json

config_path = "./config.json"


def load_config() -> dict:
    with open(config_path) as jsonFile:
        config = json.load(jsonFile)
        jsonFile.close()
    return config


def save_config(config: dict):
    with open(config_path, "w") as jsonFile:
        json.dump(config, jsonFile)
        jsonFile.close()
