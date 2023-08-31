"""Contains Scheduler for timer jobs management"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from aiogram import Bot

from poster import Poster
from scrapper import Scrapper
from settings import SETTINGS_MANAGER
from storage import STORAGE
from date import DATE_TIME_INFO
from gallery import GALLERY


class Scheduler:
    """Scheduler for timer jobs management"""

    def _add_scrap_job(self):
        self.scrap_job = self.scheduler.add_job(
            self.scrap_wrapper,
            CronTrigger(
                hour=SETTINGS_MANAGER.scrap_timer.hours,
                minute=SETTINGS_MANAGER.scrap_timer.minutes,
                timezone=self._tz,
            ),
        )

    def _add_post_job(self):
        self.post_job = self.scheduler.add_job(
            self.post_wrapper,
            CronTrigger(
                hour=SETTINGS_MANAGER.post_timer.hours,
                minute=SETTINGS_MANAGER.post_timer.minutes,
                timezone=self._tz,
            ),
        )

    def _add_clean_job(self):
        self.clean_job = self.scheduler.add_job(
            self.clean_wrapper,
            IntervalTrigger(
                days=SETTINGS_MANAGER.clean_timer.days,
                timezone=self._tz,
            ),
        )

    def __init__(self) -> None:
        self._tz = DATE_TIME_INFO.tz

        self.scheduler = AsyncIOScheduler(
            timezone=self._tz,
        )

        self._add_scrap_job()
        self._add_post_job()
        self._add_clean_job()

    async def scrap_wrapper(self, force: bool = False):
        """Wrapper over Scrapper function

        Args:
            force (bool, optional): Scrap even if the data is already scrapped. Defaults to False.
        """
        await self.scrapper.scrap(force=force)

    async def post_wrapper(self):
        """Wrapper over Poster function post"""
        if not STORAGE.is_today_file_exists():
            await self.scrap_wrapper()

        await self.poster.post()

    async def post_to_owner_wrapper(self):
        """Wrapper over Poster function post_to_owner"""
        if not STORAGE.is_today_file_exists():
            await self.scrap_wrapper()

        await self.poster.post_to_owner()

    def clean_wrapper(self):
        """Wrapper over clean() functions"""
        STORAGE.clean()
        GALLERY.clean()

    def restart_scrap_job(self):
        """Restarts scrap job"""
        self.scheduler.remove_job(self.scrap_job.id)
        self._add_scrap_job()

    def restart_post_job(self):
        """Restarts post job"""
        self.scheduler.remove_job(self.post_job.id)
        self._add_post_job()

    def restart_clean_job(self):
        """Restarts clean job"""
        self.scheduler.remove_job(self.clean_job.id)
        self._add_clean_job()

    def start(self, bot: Bot):
        """Starts the scheduler"""
        self._bot = bot

        self.scrapper = Scrapper()
        self.poster = Poster(bot=self._bot)
        self.scheduler.start()


SCHEDULER = Scheduler()
