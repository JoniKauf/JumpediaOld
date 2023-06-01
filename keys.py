import json
from os import path

FILE_NAME = "J:\Temp\keys.json"

def load():
    if not path.isfile(FILE_NAME) or not FILE_NAME.endswith(".json"):
        raise ValueError("expected a valid path to a file ending in .json")
    
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def get(key: str, default=None) -> str:
    return load().get(key, default)