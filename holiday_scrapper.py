import os
from typing import Optional
from bs4 import BeautifulSoup
from date import DATE_TIME_INFO
from time import sleep
import requests
from datetime import datetime


from holiday_provider import (
    HolidayCalendarProvider,
    HolidayProvider,
    NationalTodayProvider,
    RussianProvider,
)
from logger import LOGGER

# from datetime import datetime


class HolidayScrapper:
    """Holiday data scrapper implementation"""

    _sep = "~"
    _inner_sep = ";"
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

        self.providers: list[HolidayProvider] = [
            RussianProvider(
                include_birthday=False, exclude=[self._sep, self._inner_sep]
            ),
            # NationalTodayProvider(exclude=[self._sep, self._inner_sep]),
            HolidayCalendarProvider(exclude=[self._sep, self._inner_sep]),
        ]

    def _read_from_disk(self, date: Optional[datetime] = None) -> list[tuple[str, str]]:
        day = DATE_TIME_INFO.get_datetime_now().day - 1
        if date is not None:
            day = date.day - 1
        filename = self._get_filename(date)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > day:
                    results = []
                    for holiday in lines[day].split(self._sep):
                        title, desc = holiday.split(self._inner_sep)
                        results.append((title, desc))
                    return results
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
    ) -> list[tuple[str, str]]:
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

            day_holidays = []
            for provider in self.providers:
                day_holidays += [
                    self._inner_sep.join(hs)
                    for hs in provider.scrap_holidays(date_time)
                ]
            month_holidays.append(self._sep.join(day_holidays) + "\n")

        return month_holidays


HOLIDAY_SCRAPPER = HolidayScrapper()
