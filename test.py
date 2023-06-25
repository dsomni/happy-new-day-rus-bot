import requests


query = "день кошачьих лапок! (Россия)"

url = "https://api.fusionbrain.ai/api/v1/text2image/run"

headers = {
    # "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary4guleaACQH8bwB6D",
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Host": "api.fusionbrain.ai",
    "Origin": "https://editor.fusionbrain.ai",
}


files = {
    "queueType": (None, "generate"),
    "query": (None, query),
    "preset": (None, 1),
    "style": (None, ""),
}


response = requests.post(url, files=files, headers=headers)

# print(response.status_code, response.content)

pocket = response.json()["result"]["pocketId"]

# pocket = "649838eff0ceab8de815ab3e"

status_url = (
    f"https://api.fusionbrain.ai/api/v1/text2image/generate/pockets/{pocket}/status"
)

import time

while True:
    status_response = requests.get(status_url)
    print(status_response.status_code, status_response.content)
    if status_response.json()["result"] == "SUCCESS":
        break
    time.sleep(5)


entities_url = (
    f"https://api.fusionbrain.ai/api/v1/text2image/generate/pockets/{pocket}/entities"
)

entities_response = requests.get(entities_url)

# print(entities_response.status_code, entities_response.content)

image_url = entities_response.json()["result"][0]["response"][0]

# print(image_url)


import base64


with open("./1.png", "wb") as image_file:
    image_file.write(base64.b64decode(image_url))
