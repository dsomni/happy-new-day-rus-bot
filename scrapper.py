"""Contains Scrapper that scraps holidays"""

from bs4 import BeautifulSoup
import requests
from gallery import GALLERY

from holiday import Holiday
from image_generator_b64_based import FusionBrainImageGenerator
from logger import LOGGER
from storage import STORAGE


class Scrapper:
    """Scraps holidays"""

    def _scrap_holiday_titles(self) -> list[str]:
        response = requests.get(
            "https://kakoysegodnyaprazdnik.ru/", headers=self._headers, timeout=10
        )

        soup = BeautifulSoup(response.content, "html.parser")

        holiday_titles = []

        elements = list(
            soup.find("div", {"class": "listing_wr"}).findChildren(  # type: ignore
                "div", {"itemprop": "suggestedAnswer"}, recursive=False
            )
        )

        for element in LOGGER.get_tqdm(
            elements, total=len(elements), desc="Scrapping holiday titles"
        ):
            try:
                holiday_titles.append(element.find("span", {"itemprop": "text"}).text)
            except BaseException:  # pylint: disable=W0718
                pass

        return holiday_titles

    def __init__(self) -> None:
        self.image_generator = FusionBrainImageGenerator()

        self._scrap_url = "https://kakoysegodnyaprazdnik.ru/"
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }

    async def scrap(self, force: bool = False) -> list[Holiday]:
        """Scraps holiday titles and combines them with images

        Args:
            force (bool, optional): Scrap even if the data is already scrapped. Defaults to False.

        Returns:
            list[Holiday]: List of Holiday objects
        """

        if not force and STORAGE.is_today_file_exists():
            return STORAGE.get_today_data()

        holidays: list[Holiday] = []

        holiday_titles = self._scrap_holiday_titles()
        holiday_image_hashes = await self.image_generator.get_image_b64_hashes(
            holiday_titles
        )
        holiday_image_paths = GALLERY.save_images_b64(holiday_image_hashes)

        for title, image_path in zip(holiday_titles, holiday_image_paths):
            holidays.append(Holiday(title=title, image_path=image_path))

        STORAGE.save_today_data(holidays)

        return holidays
