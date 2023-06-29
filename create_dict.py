import json

# Just a file to fix outdated jump_data files, not in use by bot itself
def create():
    with open("data/jumps/jump_data.json") as f:
        jump_data = json.load(f)

    DATABASE: dict[str, dict[str, str | list[str]]] = {}
    for d in jump_data:
        if "ftp" in d:
            d.extend(d.pop("ftp"))
        DATABASE[d.pop("name")] = d
    with open("data/jumps/jump_data.json", "w") as f:
        json.dump(DATABASE, f)