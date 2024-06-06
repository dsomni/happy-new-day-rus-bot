import requests
import os
from typing import Optional
from bs4 import BeautifulSoup
from date import DATE_TIME_INFO
from time import sleep
from datetime import datetime
import sys

_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
}

# d = datetime.now()
# print()

# response = requests.get(
#     f"https://nationaltoday.com/{d.strftime('%B').lower()}-{d.day}-holidays/",
#     headers=_headers,
#     timeout=2,
# )
# print(response.status_code)

# soup = BeautifulSoup(response.content, "html.parser")
# block_div = soup.find("div", {"class": "what-is-container"})
# elements = list(
#     block_div.findChildren("div", {"class": "title-box"}, recursive=True)  # type: ignore
# )
# for el in elements:
#     print(el.findChild("h3", {"class": "holiday-title"}).text)
#     desc = el.findChild("p", {"class": "excerpt"})
#     print(desc.text if desc else "")
#     print()
# sys.exit()


response = requests.get(
    "https://www.holidaycalendar.io/day/june-5-holidays",
    headers=_headers,
    timeout=2,
)
print(response.status_code)

soup = BeautifulSoup(response.content, "html.parser")
# block_div = soup.find("div", {"class": "day-holidays"})
# block_div = soup.find("div", {"class": "month-holidays"})


# elements = list(block_div.findChildren("div", {"class": "card"}, recursive=True))  # type: ignore
# for el in elements:
#     print(el.findChild("h3").text)
#     desc = el.findChild("div", {"class": "day-text"})
#     print(desc.text if desc else "")
#     print()


block_div = soup.find("div", {"class": "historical-events"})
sp2 = BeautifulSoup(block_div.findChild("p", recursive=True).text, "html.parser")


elements = list(sp2.findChildren("div", {"class": "timeline-item"}, recursive=True))  # type: ignore
print(elements)
for el in elements:
    print(el.findChild("div", {"class": "timeline-date-text"}).text)
    title, desc = el.findChildren("div", {"class": "timeline-text"})
    print(title.text if desc else "")
    print(desc.text if desc else "")
    print()
sys.exit()
