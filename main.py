"""Contains main functionality """

import grequests

import asyncio
import logging

from aiogram import Bot, Dispatcher

from routers import actions, dev_actions, basic, getters, setters, subscription

from local_secrets import SECRETS_MANAGER
from scheduler import SCHEDULER


logging.basicConfig(level=logging.FATAL)
bot = Bot(token=SECRETS_MANAGER.get_bot_token())
dp = Dispatcher()


async def main():
    """Main function"""
    dp.include_routers(
        setters.router,
        getters.router,
        actions.router,
        dev_actions.router,
        subscription.router,
        basic.router,
    )
    SCHEDULER.start(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
