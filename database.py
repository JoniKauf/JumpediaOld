"""
A wrapper module for a database of jumps. A database is a dictionary of
jump names with jump stats.
"""


import json

import json
from typing import cast

ElementStat = dict[str, str | list[str]]
Database = dict[str, ElementStat]

json_fp = "data/jumps/jump_data.json"
with open(json_fp) as f:
    DATABASE: Database = cast(Database, json.load(f))

# REQUIRES JSON TO ONLY HAVE JUMP NAME KEYS AS LOWER CASE!!
# Specifically exists to speed up expensive operations like the list command
def _get_jump_fast(jump_name_lower: str) -> ElementStat:
    return DATABASE.get(jump_name_lower, None)

def get_jump(jump_name: str) -> ElementStat:
    return _get_jump_fast(jump_name.lower())

def jump_exists(jump_name: str) -> bool:
    return jump_name.lower() in DATABASE.keys()