
import json

def create():
    with open("data/jump_data.json") as f:
        jump_data = json.load(f)

    DATABASE: dict[str, dict[str, str | list[str]]] = {}
    for d in jump_data:
        if "ftp" in d:
            d.extend(d.pop("ftp"))
        DATABASE[d.pop("name")] = d
    with open("data/jump_data.json", "w") as f:
        json.dump(DATABASE, f)