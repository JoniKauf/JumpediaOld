import requests
import json
import keys
import time

KEY = keys.get("PASTEE_KEY")

def create(content: str, beforeLink: str):

    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': KEY
    }
    
    data = {
        'description': 'My test paste',
        'sections': [
            {
                'name': 'Jumpedia results:',
                'contents': content
            }
        ]
    }
    
    t = time.time()
    response = requests.post('https://api.paste.ee/v1/pastes', data=json.dumps(data), headers=headers)
    print("API request -> Elapsed time: {:.3f} seconds".format(time.time() - t))

    if response.status_code == 201:
        return f"{beforeLink}\n{response.json()['link']}"
    else:
        return f"Couldn't access pastee API... (status_code: {response.status_code})"