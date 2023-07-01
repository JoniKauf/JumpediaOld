"""
A wrapper module for the pastee API. It is mainly used for the 'list' command.
"""


import requests
import json
import secret
import time

KEY = secret.get_key("PASTEE_KEY")

def create(content: str, beforeLink: str = None) -> str:

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': KEY
    }
    
    data = {
        'description': 'A very cool table of Jumpedia information!',
        'sections': [
            {
                'name': 'Jumpedia results:',
                'contents': content
            }
        ]
    }
    
    response = requests.post('https://api.paste.ee/v1/pastes', data=json.dumps(data), headers=headers)

    if response.status_code == 201:
        return f"{beforeLink if beforeLink else ''}\n{response.json()['link']}".strip()
    else:
        return f"Couldn't access pastee API... (status_code: {response.status_code})\nTry again later!"