"""Contains Scrapper that scraps holidays"""

from gallery import GALLERY

from holiday import Holiday
from holiday_scrapper import HolidayScrapper
from image_generator_model_based import HuggingFaceImageGenerator

from storage import STORAGE


class Scrapper:
    """Scraps holidays"""

    def __init__(self) -> None:
        self.image_generator = HuggingFaceImageGenerator()
        self.holiday_scrapper = HolidayScrapper()

    async def scrap(self, force: bool = False, limit: int = 0) -> list[Holiday]:
        """Scraps holiday titles and combines them with images

        Args:
            force (bool, optional): Scrap even if the data is already scrapped. Defaults to False.
            limit (int, optional): Limit scrap data number. If set to0, then scrap all data.
            Defaults to 0.

        Returns:
            list[Holiday]: List of Holiday objects
        """

        if not force and STORAGE.is_today_file_exists():
            return STORAGE.get_today_data()

        holidays: list[Holiday] = []

        holiday_titles = self.holiday_scrapper.get_holidays(force=force)
        if limit > 0:
            holiday_titles = holiday_titles[:limit]

        holiday_image_hashes = self.image_generator.get_image_b64_hashes(holiday_titles)

        holiday_image_paths = GALLERY.save_images_b64(holiday_image_hashes)

        for title, image_path in zip(holiday_titles, holiday_image_paths):
            holidays.append(Holiday(title=title, image_path=image_path))

        STORAGE.save_today_data(holidays)

        return holidays
