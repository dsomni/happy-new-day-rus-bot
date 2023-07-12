"""Contains the SettingsManager class instances"""
from typing import Optional
import os
import json


from date import DATE_TIME_INFO


class Owner:
    """Bot owner"""

    def __init__(
        self,
        tg_id: int,  # pylint: disable=C0103
        tg_alias: str,
    ) -> None:
        self.tg_id = tg_id  # pylint: disable=C0103
        self.tg_alias = tg_alias

    def as_dict(self) -> dict:
        """Represents the class instance as dict

        Returns:
            dict
        """
        return {"tg_id": self.tg_id, "tg_alias": self.tg_alias}


class Subscriber(Owner):
    """Bot subscriber"""

    def __init__(
        self,
        tg_id: int,  # pylint: disable=C0103
        tg_alias: str,
        subscribe_date: Optional[str] = None,
    ) -> None:
        super().__init__(tg_id, tg_alias)

        if subscribe_date is None:
            self.subscribe_date = DATE_TIME_INFO.get_datetime_now_formatted(
                "%d.%m.%y %H:%M:%S"
            )
        else:
            self.subscribe_date = subscribe_date

    def as_dict(self) -> dict:
        supper_dict = super().as_dict()
        supper_dict.update({"subscribe_date": self.subscribe_date})
        return supper_dict


class CronTimer:
    """Cron timer information"""

    def __init__(self, hours: int, minutes: int) -> None:
        self.hours = hours
        self.minutes = minutes

    def as_dict(self) -> dict:
        """Represents the class instance as dict

        Returns:
            dict
        """
        return {"hours": self.hours, "minutes": self.minutes}


class IntervalTimer:
    """Interval timer information"""

    def __init__(self, days: int) -> None:
        self.days = days

    def as_dict(self) -> dict:
        """Represents the class instance as dict

        Returns:
            dict
        """
        return {"days": self.days}


class SettingsManager:
    """Bot settings manager"""

    def _pack_timers(self):
        self.scrap_timer = CronTimer(
            hours=self._settings["scrap_timer"]["hours"],
            minutes=self._settings["scrap_timer"]["minutes"],
        )

        self.post_timer = CronTimer(
            hours=self._settings["post_timer"]["hours"],
            minutes=self._settings["post_timer"]["minutes"],
        )

        self.clean_timer = IntervalTimer(days=self._settings["clean_timer"]["days"])

    def _unpack_timers(self) -> dict:
        return {
            "scrap_timer": self.scrap_timer.as_dict(),
            "post_timer": self.post_timer.as_dict(),
            "clean_timer": self.clean_timer.as_dict(),
        }

    def _pack_owner(self):
        self.owner = Owner(
            tg_id=self._settings["owner"]["tg_id"],
            tg_alias=self._settings["owner"]["tg_alias"],
        )

    def _unpack_owner(self) -> dict:
        return {
            "owner": self.owner.as_dict(),
        }

    def _pack_subscribers(self):
        self.subscribers = [
            Subscriber(
                tg_id=subscriber["tg_id"],
                tg_alias=subscriber["tg_alias"],
                subscribe_date=subscriber["subscribe_date"],
            )
            for subscriber in self._settings["subscribers"]
        ]

    def _unpack_subscribers(self) -> dict:
        return {
            "subscribers": [subscriber.as_dict() for subscriber in self.subscribers],
        }

    def _unpack_all(self) -> dict:
        total_unpack = {}
        total_unpack.update(self._unpack_timers())
        total_unpack.update(self._unpack_owner())
        total_unpack.update(self._unpack_subscribers())
        total_unpack.update({"image_soft_prompt": self.image_soft_prompt})
        total_unpack.update({"should_translate_prompt": self.should_translate_prompt})
        return total_unpack

    def _load_settings(self):
        with open(self._path, encoding="utf8") as json_file:
            self._settings: dict = json.load(json_file)
            json_file.close()

    def _save_settings(self):
        self._settings.update(self._unpack_all())
        with open(self._path, "w", encoding="utf8") as json_file:
            json.dump(self._settings, json_file, indent=2)
            json_file.close()

    def _update_settings(self, key: str, value):
        self._settings.update({key: value})
        self._save_settings()

    def __str__(self) -> str:
        return str(list(self._settings.items()))

    def __repr__(self) -> str:
        return str(list(self._settings.items()))

    def __init__(self, path: str = os.path.join(".", "settings.json")) -> None:
        self._path = path
        self._load_settings()

        self.image_soft_prompt = self._settings["image_soft_prompt"]
        self.should_translate_prompt = self._settings["should_translate_prompt"]

        self._pack_timers()
        self._pack_owner()
        self._pack_subscribers()

    def is_subscribed(self, tg_id: int) -> bool:
        """Checks whether user is subscribed or not

        Args:
            tg_id (int): user telegram id

        Returns:
            bool: is user subscribed
        """
        subscribers_set = set([subscriber.tg_id for subscriber in self.subscribers])
        return tg_id in subscribers_set

    def subscribe_user(self, tg_id: int, tg_alias: str):
        """Subscribe the user to the bot

        Args:
            tg_id (int): user telegram id
            tg_alias (str): user telegram alias
        """
        if self.is_subscribed(tg_id):
            return

        self.subscribers.append(Subscriber(tg_id=tg_id, tg_alias=tg_alias))
        self._save_settings()

    def unsubscribe_user(self, tg_id: int):
        """Unsubscribe the user from the bot

        Args:
            tg_id (int): user telegram id
            tg_alias (str): user telegram alias
        """
        if not self.is_subscribed(tg_id):
            return

        rest_subscribers = []
        for subscriber in self.subscribers:
            if subscriber.tg_id == tg_id:
                continue
            rest_subscribers.append(subscriber)

        self.subscribers = rest_subscribers  # pylint: disable=W0201
        self._save_settings()

    def is_owner(self, tg_id: int) -> bool:
        """Checks whether user is owner of bot or not

        Args:
            tg_id (int): user telegram id

        Returns:
            bool: is user owner
        """
        return self.owner.tg_id == tg_id

    def set_owner_alias(self, tg_alias: str):
        """Sets new telegram alias to the bot owner

        Args:
            tg_alias (str): new alias
        """

        self.owner.tg_alias = tg_alias
        self._save_settings()

    def set_scrap_timer(self, hours: int, minutes: int):
        """Sets new scrap timer settings

        Args:
            hours (int): hours to scrap
            minutes (int): minutes to scrap
        """
        self.scrap_timer.hours = hours  # pylint: disable=W0201
        self.scrap_timer.minutes = minutes  # pylint: disable=W0201
        self._save_settings()

    def set_post_timer(self, hours: int, minutes: int):
        """Sets new post timer settings

        Args:
            hours (int): hours to scrap
            minutes (int): minutes to scrap
        """
        self.post_timer.hours = hours  # pylint: disable=W0201
        self.post_timer.minutes = minutes  # pylint: disable=W0201
        self._save_settings()

    def set_clean_timer(self, days: int):
        """Sets new clean timer settings

        Args:
            days (int): interval in days
        """
        self.clean_timer.days = days  # pylint: disable=W0201
        self._save_settings()

    def set_image_soft_prompt(self, prompt: str):
        """Sets new image soft prompt

        Args:
            prompt (str): new prompt
        """
        self.image_soft_prompt = prompt
        self._save_settings()

    def set_should_translate_prompt(self, should_translate_prompt: bool):
        """Sets new should_translate_prompt value

        Args:
            should_translate_prompt (bool): new should_translate_prompt value
        """
        self.should_translate_prompt = should_translate_prompt
        self._save_settings()


SETTINGS_MANAGER = SettingsManager()
