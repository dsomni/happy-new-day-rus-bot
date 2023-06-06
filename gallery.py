"""Contains Gallery implementations"""
import os
import shutil
import requests

from tqdm import tqdm

from date import DATE_TIME_INFO


class Gallery:
    """Persistent image storage implementation"""

    @staticmethod
    def _soft_mkdir(path: str):
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)

    def _generate_today_folder_name(self) -> str:
        return DATE_TIME_INFO.get_datetime_now_formatted("%d-%m-%y")

    def _create_today_folder(self):
        Gallery._soft_mkdir(
            os.path.join(
                self.path,
                self._generate_today_folder_name(),
            )
        )

    def _generate_image_filename(self, image_idx: int) -> str:
        return f"{image_idx}.{self.extension}"

    def _generate_image_path(self, image_idx: int) -> str:
        return os.path.join(
            self.path,
            self._generate_today_folder_name(),
            self._generate_image_filename(image_idx),
        )

    def _save_image(self, image_idx: int, image_url: str) -> str:
        image_path = self._generate_image_path(image_idx)

        try:
            response = requests.get(image_url, timeout=10)
            with open(image_path, "wb") as image_file:
                image_file.write(response.content)
        except BaseException:  # pylint: disable=W0718
            return ""

        return image_path

    def __init__(self, folder: str = "gallery", extension: str = "png") -> None:
        self.folder = folder
        self.extension = extension
        self.path = os.path.join(".", self.folder)
        Gallery._soft_mkdir(self.path)

    def is_image_exist(self, path: str) -> bool:
        """Checks existence of the image

        Args:
            path (str): image path

        Returns:
            bool: True is exists, otherwise False
        """

        return os.path.exists(path) and os.path.isfile(path)

    def save_images(self, urls: list[str], start_idx: int = 0) -> list[str]:
        """Saves images to the disk

        Args:
            urls (list[str]): list of images urls
            start_idx (int): index of the first image. Defaults to 0

        Returns:
            list[str]: paths of saved images
        """
        self._create_today_folder()
        image_paths = []
        for i, image_url in tqdm(
            enumerate(urls), total=len(urls), desc="Saving images"
        ):
            image_paths.append(self._save_image(i + start_idx, image_url))

        return image_paths

    def read_image(self, image_path: str):
        """Reads images from disk

        Args:
            image_path (str): path to image

        Returns:
            Image if it exists, otherwise None
        """
        if not self.is_image_exist(image_path):
            return None

        image = None
        with open(image_path, "rb") as image_file:
            image = image_file.read()

        return image

    def read_images(self, image_paths: list[str]):
        """Reads images from disk

        Args:

        Returns:
            List of images. Not existing images are replaced with None
        """

        images = []

        for image_path in tqdm(image_paths, desc="Reading images"):
            images.append(self.read_image(image_path))

        return images

    def clean(self):
        """Cleans all te data except today's ones"""

        today_folder_name = self._generate_today_folder_name()

        for filename in os.listdir(self.path):
            if filename == today_folder_name:
                continue
            path_to_folder = os.path.join(self.path, filename)
            if os.path.isdir(path_to_folder):
                shutil.rmtree(path_to_folder)


GALLERY = Gallery()
