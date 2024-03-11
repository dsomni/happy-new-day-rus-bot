import os
from typing import Optional
from bs4 import BeautifulSoup
from date import DATE_TIME_INFO
from time import sleep
import requests
from datetime import datetime


from logger import LOGGER

# from datetime import datetime


class HolidayScrapper:
    """Holiday data scrapper implementation"""

    _sep = "~"
    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }
    _request_delay = 0.1

    @staticmethod
    def _soft_mkdir(path: str):
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)

    def _get_filename(self, date: Optional[datetime] = None) -> str:
        if date is None:
            today = DATE_TIME_INFO.get_datetime_now()
        else:
            today = date
        return os.path.join(self.path, f"{today.month:02}_{today.year}.txt")

    def __init__(self, folder: str = "holiday_storage") -> None:

        self.folder = folder
        self.path = os.path.join(".", self.folder)
        HolidayScrapper._soft_mkdir(self.path)

    def _read_from_disk(self, date: Optional[datetime] = None) -> list[str]:
        day = DATE_TIME_INFO.get_datetime_now().day - 1
        if date is not None:
            day = date.day - 1
        filename = self._get_filename(date)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > day:
                    return lines[day].split(self._sep)
        except FileNotFoundError:
            LOGGER.log(f"File with holidays not found. Filename {filename}", "Error")
        return []

    def _save_to_disk(self, month_holidays: list[str], date: Optional[datetime]):
        filename = self._get_filename(date)
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.writelines(month_holidays)
        except FileNotFoundError:
            LOGGER.log(f"File with holidays not found. Filename {filename}", "Error")

    def get_holidays(
        self, force: bool = False, date: Optional[datetime] = None
    ) -> list[str]:
        filename = self._get_filename(date)

        if not force and os.path.exists(filename):
            return self._read_from_disk(date)

        month_holidays = self._scrap_month_holidays(date)
        self._save_to_disk(month_holidays, date)

        return self._read_from_disk(date)

    def _scrap_year_holidays(self, year: Optional[int] = None):
        scrap_year = DATE_TIME_INFO.get_datetime_now().year
        if year is not None:
            scrap_year = year

        for month in range(1, 13):
            date_time = datetime(year=scrap_year, month=month, day=1)
            month_holidays = self._scrap_month_holidays(date_time)
            self._save_to_disk(month_holidays, date=date_time)

    def _scrap_month_holidays(self, _date: Optional[datetime] = None) -> list[str]:
        month_holidays = []
        date = DATE_TIME_INFO.get_datetime_now()
        if _date is not None:
            date = _date

        for day in range(1, 32):
            try:
                date_time = datetime(year=date.year, month=date.month, day=day)
            except ValueError:
                break

            month_holidays.append(
                self._sep.join(self._scrap_holidays(date_time)) + "\n"
            )

        return month_holidays

    def _scrap_holidays(self, _date: Optional[datetime] = None) -> list[str]:
        date = DATE_TIME_INFO.get_datetime_now()
        if _date is not None:
            date = _date
        year = date.year
        month = date.month
        day = date.day

        response = requests.get(
            f"https://www.calend.ru/day/{year}-{month}-{day}/",
            headers=self._headers,
            timeout=2,
        )

        if not response.ok:
            return []

        LOGGER.log(f"Scrapping holiday titles {day}.{month:02}.{year}")

        soup = BeautifulSoup(response.content, "html.parser")

        holiday_titles = []

        for block in ["holidays", "thisDay", "knownDates"]:
            block_div = soup.find("div", {"class": f"block {block}"})
            if block_div is None:
                continue
            elements = list(
                block_div.findChildren(  # type: ignore
                    "span", {"class": "title"}, recursive=True
                )
            )

            for element in LOGGER.get_tqdm(
                elements,
                total=len(elements),
                desc=f"Scrapping [{block}] holiday titles {day}.{month:02}.{year}",
                leave=False,
            ):
                try:
                    holiday_titles.append(element.find("a").text)
                except BaseException:  # pylint: disable=W0718
                    pass

        # Именины
        block = "block nameDay"
        block_div = soup.find("div", {"class": f"{block}"})
        if block_div is not None:
            elements = list(
                block_div.findChildren(  # type: ignore
                    "span", {"class": "caption"}, recursive=True
                )
            )
            for element in LOGGER.get_tqdm(
                elements,
                total=len(elements),
                desc=f"Scrapping [{block}] holiday titles {day}.{month:02}.{year}",
                leave=False,
            ):
                try:
                    name = element.find("a").text
                    desc = element.find("p").text
                    holiday_titles.append(f"Именины — {name} ({desc})")
                except BaseException:  # pylint: disable=W0718
                    pass

        # Персоны
        block = "persons"
        block_div = soup.find("div", {"class": f"block {block}"})
        if block_div is not None:
            elements = list(
                block_div.findChildren(  # type: ignore
                    "div", {"class": "caption"}, recursive=True
                )
            )
            for element in LOGGER.get_tqdm(
                elements,
                total=len(elements),
                desc=f"Scrapping [{block}] holiday titles {day}.{month:02}.{year}",
                leave=False,
            ):
                try:
                    person_element = element.find("span", {"class": "title"})
                    desc = person_element.find("span").text

                    anchor = person_element.find("a")
                    link = anchor["href"]
                    name = anchor.text
                    sleep(self._request_delay)
                    person_response = requests.get(
                        link,
                        headers=self._headers,
                        timeout=2,
                    )
                    person_soup = BeautifulSoup(person_response.content, "html.parser")

                    dates = person_soup.find("ul", {"class": "personDates"}).findChildren(  # type: ignore
                        "span", {"class": "personDate"}, recursive=True
                    )
                    birth = dates[0].text.strip()
                    if len(dates) > 1:
                        death = dates[2].text.strip()
                    death = "настоящее время"

                    holiday_titles.append(f"{name} ({birth} — {death}), {desc}")

                except BaseException:  # pylint: disable=W0718
                    pass

        return holiday_titles


HOLIDAY_SCRAPPER = HolidayScrapper()
