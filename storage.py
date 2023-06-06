"""Contains storage implementations"""
import os
import csv

from holiday import Holiday
from date import DATE_TIME_INFO


class Storage:
    """Persistent storage implementation"""

    def _generate_today_filename(self) -> str:
        return DATE_TIME_INFO.get_datetime_now_formatted("%d-%m-%y")

    def _get_today_file_path(self) -> str:
        return f"{os.path.join(self.path, self._generate_today_filename())}.csv"

    def __init__(self, folder: str = "storage") -> None:
        self.folder = folder
        self.path = os.path.join(".", self.folder)

        self.csv_delimiter = ","

        if not (os.path.exists(self.path) and os.path.isdir(self.path)):
            os.mkdir(self.path)

    def is_today_file_exists(self) -> bool:
        """Checks if the file for today exists or not

        Returns:
            bool: True is exists, otherwise False
        """
        today_file_path = self._get_today_file_path()
        return os.path.exists(today_file_path) and os.path.isfile(today_file_path)

    def remove_today_file(self):
        """Removes file corresponded to today"""
        if self.is_today_file_exists():
            os.remove(self._get_today_file_path())

    def get_today_data(self) -> list[Holiday]:
        """Reads file corresponding to today

        Returns:
            list[Holiday]: List of (holiday, image path) pairs
        """
        data: list[Holiday] = []
        if not self.is_today_file_exists():
            raise FileNotFoundError
        with open(
            self._get_today_file_path(), "r", newline="", encoding="utf-8"
        ) as f:  # pylint: disable=C0103
            reader = csv.reader(f, delimiter=self.csv_delimiter)
            for row in reader:
                if len(row) == 0:
                    continue
                data.append(Holiday(*row))

        return data

    def save_today_data(self, data: list[Holiday], rewrite: bool = True):
        """Saves data corresponding to today

        Args:
            rewrite (bool, optional): Should rewrite file if exists. Defaults to True.
            data (list[Holiday]): List of (holiday, image path) pairs
        """
        if self.is_today_file_exists() and rewrite:
            self.remove_today_file()

        with open(
            self._get_today_file_path(), "w", newline="", encoding="utf-8"
        ) as f:  # pylint: disable=C0103
            csv.writer(f, delimiter=self.csv_delimiter).writerows(
                [holiday.as_tuple() for holiday in data]
            )

    def clean(self):
        """Cleans all te data except today's one"""

        today_filename = self._generate_today_filename()

        for file in os.listdir(self.path):
            file_name, file_extension = os.path.splitext(file)
            if file_name == today_filename:
                continue
            path_to_file = os.path.join(self.path, file)
            if file_extension == ".csv" and os.path.isfile(path_to_file):
                os.remove(path_to_file)


STORAGE = Storage()
