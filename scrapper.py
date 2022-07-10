from random import randint, sample
import requests
from bs4 import BeautifulSoup

from utils import load_config

EMOJI = ["💝", "💛", "💯", "🎁", "🎈", "🎉", "🎊", "💐", "🌹", "🌺", "🥳", "🤪", "🤗"]


def parse_city(holiday_list: list[str]) -> tuple[list[str], list[str]]:
    try:
        idx = holiday_list.index("-")
        city = holiday_list[idx + 1 :]
        holiday_list = holiday_list[:idx]
        if city == ["США"]:
            city = ["(США🤢🤮)"]
        else:
            city[0] = "(" + city[0]
            city[-1] += ")"
        return (holiday_list, city)
    except:
        return (holiday_list, [])


def add_emoji(holiday: str) -> str:
    holiday += f"{'!' * randint(3, 6)} {''.join(sample(EMOJI, randint(5, 8), counts=[3]*len(EMOJI)))}"
    return holiday


def format_holiday(holiday: str, include_city: bool):
    holiday_list, city = parse_city(list(holiday.split()))
    if holiday_list[0].lower() == "день":
        holiday_list[0] = "С Днём"
    elif holiday_list[0].lower() == "праздник" or holiday_list[0].lower() == "празднование":
        holiday_list[0] = "С Праздником"
    else:
        holiday_list[0] = f'С Праздником "{holiday_list[0]}'
        holiday_list[-1] += '"'
    if include_city and len(city) > 0:
        holiday_list.append(f"{' '.join(city)}")
    holiday = " ".join(holiday_list)
    holiday = add_emoji(holiday)
    return holiday


def scrapper() -> list:
    config = load_config()

    url = config.get("FETCH_DOMAIN")
    if not url:
        return []
    page = requests.get(url)
    if page.status_code != 200:
        return []
    soup = BeautifulSoup(page.text, "html.parser")
    holidays_list = soup.find("ul", class_="holidays-list")
    holidays = []
    for li in holidays_list.findChildren("li", recursive=False):  # type: ignore
        holidays.append(format_holiday(li.text.strip(), config.get("INCLUDE_CITY") or False))
    return holidays


if __name__ == "__main__":
    result = scrapper()
