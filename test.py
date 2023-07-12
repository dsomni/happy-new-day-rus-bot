import json
import random
import sys
import requests

query = "День пожилых людей! (Россия)"

url = "https://api.fusionbrain.ai/web/api/v1/text2image/run?model_id=1"

headers = {
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Host": "api.fusionbrain.ai",
    "Origin": "https://editor.fusionbrain.ai",
}

styles = [
    "",
    "ANIME",
    "UHD",
    "CYBERPUNK",
    "KANDINSKY",
    "AIVAZOVSKY",
    # "MALEVICH",
    # "PICASSO",
    # "GONCHAROVA",
    "CLASSICISM",
    "RENAISSANCE",
    "OILPAINTING",
    # "PENCILDRAWING",
    "DIGITALPAINTING",
    "MEDIEVALPAINTING",
    "SOVIETCARTOON",
    "RENDER",
    # "CARTOON",
    "STUDIOPHOTO",
    "PORTRAITPHOTO",
    "KHOKHLOMA",
    # "CRISTMAS",
]

dumped = json.dumps(
    {
        "type": "GENERATE",
        "generateParams": {"query": "День пожилых людей"},
        "width": 512,
        "height": 512,
        "style": "",
    }
)


files = {
    "params": ("blob", dumped, "application/json"),
}


response = requests.post(url, files=files, headers=headers)

# print(response.status_code, response.content)

answer_uuid = response.json()["uuid"]

status_url = f"https://api.fusionbrain.ai/web/api/v1/text2image/status/{answer_uuid}"

import time

answer_response = None

while True:
    answer_response = requests.get(status_url)
    # print(status_response.status_code, status_response.content)
    if answer_response.json()["status"] == "DONE":
        break
    time.sleep(5)

if answer_response is None:
    print(":((((((((((((((")
    sys.exit()

image_base64 = answer_response.json()["images"][0]

import base64


with open("./1.png", "wb") as image_file:
    image_file.write(base64.b64decode(image_base64))
