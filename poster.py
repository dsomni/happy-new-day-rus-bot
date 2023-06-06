"""Contains Poster that posts holidays to the bot"""
import asyncio
from tqdm import tqdm

from aiogram import Bot
from aiogram.types import BufferedInputFile

from holiday import Holiday
from keyboards.basic import get_basic_markup

from settings import SETTINGS_MANAGER
from storage import STORAGE


class Poster:
    """Posts holidays to subscribers"""

    def __init__(self, bot: Bot) -> None:
        self._bot = bot
        self._send_messages_delay_seconds: float = 0.2

    async def post(self, holidays: list[Holiday]):
        """Posts holidays to subscribers

        Args:
            holidays (list[Holiday]): list of holidays to post
        """

        for subscriber in SETTINGS_MANAGER.subscribers:
            subscriber_markup = get_basic_markup(subscriber.tg_id)
            for holiday in tqdm(
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
                        BufferedInputFile(holiday.image, filename=holiday.image_path),
                        caption=holiday.emoji_title,
                        reply_markup=subscriber_markup,
                    )

                await asyncio.sleep(self._send_messages_delay_seconds)

    async def post_from_storage(self):
        """Posts holidays taken from storage to subscribers"""

        if not STORAGE.is_today_file_exists():
            raise FileNotFoundError()

        await self.post(STORAGE.get_today_data())
