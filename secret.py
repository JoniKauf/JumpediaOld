"""
Module to manage the 'secret.json' file, which is not uploaded to github and is in a
different folder on the server. These secrets contain tokens and other sensitive data.
"""

import json
from os import path

FILE_PATH = "J:\Temp\secret.json"

def load() -> str | dict | list:
    if not path.isfile(FILE_PATH) or not FILE_PATH.endswith(".json"):
        raise ValueError("secret.json to start the bot could not be found")
    
    with open(FILE_PATH, "r") as f:
        return json.load(f)

def get_key(key: str, default=None) -> str:
    return load().get(key, default)