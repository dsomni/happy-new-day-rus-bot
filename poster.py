"""Contains Poster that posts holidays to the bot"""
import asyncio
from typing import List

from aiogram import Bot
from aiogram.types import BufferedInputFile

from holiday import Holiday
from keyboards.basic import get_basic_markup
from logger import LOGGER

from settings import SETTINGS_MANAGER, PostReceivers
from storage import STORAGE


class Poster:
    """Posts holidays to subscribers"""

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._send_messages_delay_seconds: float = 0.2

    async def _post(
        self,
        holidays: List[Holiday],
        receivers: List[PostReceivers],
    ):
        """Posts holidays to subscribers

        Args:
            holidays (list[Holiday]): list of holidays to post
            receivers (list[Subscriber]): list of receivers to post to
        """
        for subscriber in receivers:
            subscriber_markup = get_basic_markup(subscriber.tg_id)
            try:
                for holiday in LOGGER.get_tqdm(
                    holidays,
                    total=len(holidays),
                    desc=f"Posting holidays to @{subscriber.tg_alias}",
                ):
                    if holiday.image is None:
                        await self._bot.send_message(
                            subscriber.tg_id,
                            holiday.emoji_title,
                            reply_markup=subscriber_markup,
                        )
                    else:
                        await self._bot.send_photo(
                            subscriber.tg_id,
                            BufferedInputFile(
                                holiday.image, filename=holiday.image_path
                            ),
                            caption=holiday.emoji_title,
                            reply_markup=subscriber_markup,
                        )

                    await asyncio.sleep(self._send_messages_delay_seconds)
            except BaseException:  # pylint: disable=W0718
                continue

    async def post(self):
        """Posts holidays taken from storage to subscribers"""

        if not STORAGE.is_today_file_exists():
            raise FileNotFoundError()

        await self._post(
            STORAGE.get_today_data(), SETTINGS_MANAGER.get_subscribers_as_receivers()
        )

    async def post_to_owner(self):
        """Posts holidays taken from storage to subscribers"""

        if not STORAGE.is_today_file_exists():
            raise FileNotFoundError()

        await self._post(
            STORAGE.get_today_data(), [SETTINGS_MANAGER.get_owner_as_receiver()]
        )
