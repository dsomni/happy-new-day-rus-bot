from bs4 import BeautifulSoup
import time
import sys
import requests
from datetime import datetime
import random
import grequests

from logger import LOGGER


def timeout_get(*args, **kwargs):

    def trace_function(frame, event, arg):
        if time.time() - start > 5:
            raise Exception("Timed out!")

        return trace_function

    start = time.time()
    sys.settrace(trace_function)

    try:
        res = requests.get(*args, **kwargs, timeout=5)
    except:
        raise
    finally:
        sys.settrace(None)
    return res


class HolidayProvider:
    """Holiday provider case class"""

    _headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }
    _request_delay = 0.1

    def __init__(self, exclude: list[str]) -> None:
        self.exclude = exclude

    def remove_unwanted(self, text: str):
        final_text = text
        for exc in self.exclude:
            final_text = final_text.replace(exc, "")
        return final_text

    def _prepare_pairs(self, pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return [(self.remove_unwanted(t), self.remove_unwanted(d)) for t, d in pairs]

    def prepare_pairs(self, pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return self._prepare_pairs(pairs)

    def scrap_holidays(self, date: datetime) -> list[tuple[str, str]]:
        raise NotImplementedError


class ForeignHolidayProviderHolidayProvider(HolidayProvider):
    """Holiday provider case class"""

    def _translate_batch(self, texts: list[str], label: str = "") -> list[str]:

        true_indices = []
        for i, t in enumerate(texts):
            if len(t) > 0:
                true_indices.append(i)

        rs = [
            grequests.get(
                "https://translate.google.com/m",
                params={
                    "tl": "ru",
                    "sl": "auto",
                    "q": t.replace("«", "'").replace("»", "'"),
                },
                timeout=5,
            )
            for t in texts
            if len(t) > 0
        ]

        iterator = grequests.imap_enumerated(rs, size=20)
        translations = [*texts]

        for idx, r in LOGGER.get_tqdm(
            iterator, total=len(rs), desc=f"Translating {label}"
        ):
            try:

                soup = BeautifulSoup(r.text, "html.parser")
                element = soup.find("div", {"class": "t0"})
                if not element:
                    element = soup.find("div", {"class": "result-container"})
                if not element:
                    continue

                translations[true_indices[idx]] = element.get_text(strip=True)
            except BaseException:
                continue
        return translations

    def _translate(self, holidays: list[tuple[str, str]]) -> list[tuple[str, str]]:
        batch_t, batch_d = list(zip(*holidays))

        return list(
            zip(
                self._translate_batch(batch_t, label="titles"),
                self._translate_batch(batch_d, label="descriptions"),
            )
        )

    def prepare_pairs(self, pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return self._prepare_pairs(self._translate(pairs))


class RussianProvider(HolidayProvider):
    """https://www.calend.ru/"""

    def __init__(
        self,
        include_name_day: bool = True,
        include_birthday: bool = True,
        exclude: list[str] = [],
    ) -> None:
        super().__init__(exclude)
        self.include_name_day = include_name_day
        self.include_birthday = include_birthday

    def _scrap_name_days(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        holiday_titles = []

        block_div = soup.find("div", {"class": "block nameDay"})
        if block_div is not None:
            elements = list(
                block_div.findChildren(  # type: ignore
                    "span", {"class": "caption"}, recursive=True
                )
            )
            for element in LOGGER.get_tqdm(
                elements, total=len(elements), desc="Scrapping name days"
            ):
                try:
                    name = element.find("a").text
                    desc = element.find("p").text
                    holiday_titles.append((f"Именины — {name}", desc))
                except BaseException:  # pylint: disable=W0718
                    pass
        return holiday_titles

    def _scrap_birthdays(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        holiday_titles = []

        block_div = soup.find("div", {"class": "block persons"})
        if block_div is not None:
            elements = list(
                block_div.findChildren(  # type: ignore
                    "div", {"class": "caption"}, recursive=True
                )
            )
            for element in LOGGER.get_tqdm(
                elements,
                total=len(elements),
                desc="Scrapping persons",
                leave=False,
            ):
                try:
                    person_element = element.find("span", {"class": "title"})
                    desc = person_element.find("span").text

                    anchor = person_element.find("a")
                    link = anchor["href"]
                    name = anchor.text
                    time.sleep(self._request_delay)

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
                    death = "настоящее время"
                    if len(dates) > 1:
                        death = dates[2].text.strip()

                    holiday_titles.append((f"{name} ({birth} — {death})", desc))

                except BaseException:  # pylint: disable=W0718
                    pass
        return holiday_titles

    def scrap_holidays(self, date: datetime) -> list[tuple[str, str]]:
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

        LOGGER.log(f"RussianProvider\nScrapping holiday titles {day}.{month:02}.{year}")

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
                    holiday_titles.append((element.find("a").text, ""))
                except BaseException:  # pylint: disable=W0718
                    pass

        # Именины
        if self.include_name_day:
            holiday_titles += self._scrap_name_days(soup)

        # Персоны
        if self.include_birthday:
            holiday_titles += self._scrap_birthdays(soup)

        return self.prepare_pairs(holiday_titles)


class NationalTodayProvider(ForeignHolidayProviderHolidayProvider):
    """https://nationaltoday.com/"""

    def scrap_holidays(self, date: datetime) -> list[tuple[str, str]]:
        year = date.year
        month = date.strftime("%B").lower()
        day = date.day

        response = requests.get(
            f"https://nationaltoday.com/{month}-{day}-holidays/",
            headers=self._headers,
            timeout=2,
        )

        if not response.ok:
            return []

        LOGGER.log(
            f"NationalTodayProvider\nScrapping holiday titles {day}.{month:02}.{year}"
        )

        soup = BeautifulSoup(response.content, "html.parser")

        holiday_titles = []

        soup = BeautifulSoup(response.content, "html.parser")
        wrapper_div = soup.find("div", {"class": "what-is-container"})
        elements = list(
            wrapper_div.findChildren("div", {"class": "title-box"}, recursive=True)  # type: ignore
        )
        for element in LOGGER.get_tqdm(
            elements,
            total=len(elements),
            desc="Scrapping holiday titles",
        ):
            try:
                title = element.findChild("h3", {"class": "holiday-title"}).text
                desc_element = element.findChild("p", {"class": "excerpt"})
                description = desc_element.text if desc_element else ""
                holiday_titles.append((title, description))
            except BaseException:  # pylint: disable=W0718
                pass

        return self.prepare_pairs(holiday_titles)


class HolidayCalendarProvider(ForeignHolidayProviderHolidayProvider):
    """https://nationaltoday.com/"""

    def __init__(
        self,
        month_random: int = 5,
        include_history: bool = True,
        include_holidays: bool = True,
        exclude: list[str] = [],
    ) -> None:
        super().__init__(exclude)
        self.month_random = month_random
        self.include_history = include_history
        self.include_holidays = include_holidays

    def _scrap_month_holidays(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        holiday_titles = []
        wrapper_div = soup.find("div", {"class": "month-holidays"})
        if wrapper_div is None:
            return []
        elements = list(
            wrapper_div.findChildren("div", {"class": "card"}, recursive=True)  # type: ignore
        )
        for element in LOGGER.get_tqdm(
            elements,
            total=len(elements),
            desc="Scrapping holiday titles",
        ):
            try:

                title = element.findChild("h3").text
                desc_element = element.findChild("div", {"class": "day-text"})
                description = desc_element.text if desc_element else ""
                holiday_titles.append((title, description))
            except BaseException:  # pylint: disable=W0718
                pass
        return holiday_titles

    def _scrap_day_holidays(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        holiday_titles = []
        wrapper_div = soup.find("div", {"class": "day-holidays"})
        if wrapper_div is None:
            return []
        elements = list(
            wrapper_div.findChildren("div", {"class": "card"}, recursive=True)  # type: ignore
        )
        for element in LOGGER.get_tqdm(
            elements,
            total=len(elements),
            desc="Scrapping holiday titles",
        ):
            try:

                title = element.findChild("h3").text
                desc_element = element.findChild("div", {"class": "day-text"})
                description = desc_element.text if desc_element else ""
                holiday_titles.append((title, description))
            except BaseException:  # pylint: disable=W0718
                pass
        return holiday_titles

    def _scrap_history(self, soup: BeautifulSoup) -> list[tuple[str, str]]:
        holiday_titles = []

        history_sp = BeautifulSoup(
            soup.find("div", {"class": "historical-events"})
            .findChild("p", recursive=True)
            .text,
            "html.parser",
        )
        if history_sp is None:
            return []

        elements = list(history_sp.findChildren("div", {"class": "timeline-item"}, recursive=True))  # type: ignore
        for element in LOGGER.get_tqdm(
            elements,
            total=len(elements),
            desc="Scrapping history events",
        ):
            try:
                date = element.findChild("div", {"class": "timeline-date-text"}).text
                title_element, desc_element = element.findChildren(
                    "div", {"class": "timeline-text"}
                )
                title = title_element.text if title_element else ""
                description = desc_element.text if desc_element else ""
                holiday_titles.append((f"{title} ({date})", description))
            except BaseException:  # pylint: disable=W0718
                pass

        return holiday_titles

    def scrap_holidays(self, date: datetime) -> list[tuple[str, str]]:
        year = date.year
        month = date.strftime("%B").lower()
        day = date.day

        # response = requests.get(
        #     f"https://www.holidaycalendar.io/day/{month}-{day}-holidays/",
        #     headers=self._headers,
        #     timeout=2,
        # )

        response = timeout_get(
            f"https://www.holidaycalendar.io/day/{month}-{day}-holidays/",
            headers=self._headers,
        )

        if response is None:
            return []

        if not response.ok:
            return []

        LOGGER.log(
            f"HolidayCalendarProvider\nScrapping holiday titles {day}.{month:02}.{year}"
        )

        holiday_titles = []

        soup = BeautifulSoup(response.content, "html.parser")

        if self.include_holidays:
            holiday_titles += self._scrap_day_holidays(soup)

        if self.month_random > 0:
            month_holidays = self._scrap_month_holidays(soup)
            if len(month_holidays) > 0:
                random.shuffle(month_holidays)

            holiday_titles += month_holidays[
                : min(self.month_random, len(month_holidays))
            ]

        if self.include_history:
            holiday_titles += self._scrap_history(soup)

        return self.prepare_pairs(holiday_titles)
