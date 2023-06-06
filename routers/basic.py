"""Contains basic handlers"""

from aiogram import Router
from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.filters import Text

from settings import SETTINGS_MANAGER
from date import DATE_TIME_INFO

from keyboards.basic import get_basic_markup


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """/start command handler

    Args:
        message (types.Message): message object
    """

    owner = SETTINGS_MANAGER.owner
    post_timer = SETTINGS_MANAGER.post_timer

    greetings = [
        "Привет!\n",
        f"Меня создал @{owner.tg_alias} для поднятия настроения\n",
        f"Нажми на кнопку ПОДПИСАТЬСЯ, и каждый день примерно в {post_timer.hours}:{post_timer.minutes} ({DATE_TIME_INFO.timezone_region}) я буду поздравлять тебя с актуальными праздниками!!!",
    ]

    await message.answer("\n".join(greetings), reply_markup=get_basic_markup(message.from_user.id))  # type: ignore


@router.message(Command("back"))
async def cmd_back(message: types.Message):
    """/id command handler

    Args:
        message (types.Message):object
    """

    await message.answer("Назад", reply_markup=get_basic_markup(message.from_user.id))  # type: ignore


@router.message(Command("id"))
async def cmd_id(message: types.Message):
    """/id command handler

    Args:
        message (types.Message):object
    """

    await message.answer(message.from_user.id, reply_markup=get_basic_markup(message.from_user.id))  # type: ignore


@router.message(Text("МОЙ ID"))
async def text_id(message: types.Message):
    """text id request handler

    Args:
        message (types.Message):object
    """

    await message.answer(message.from_user.id, reply_markup=get_basic_markup(message.from_user.id))  # type: ignore


@router.message(F.text)
async def text_handler(message: types.Message):
    """/start command handler

    Args:
        message (types.Message): message object
    """

    await message.reply(
        "Я не знаю, что ответить на это ))0)\nОчень остроумно, просто слов нет", reply_markup=get_basic_markup(message.from_user.id)  # type: ignore
    )
