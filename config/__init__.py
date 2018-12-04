import json


def config():
    with open("config.txt", "r") as config_f:
        config = json.loads(config_f.read())
    return config
