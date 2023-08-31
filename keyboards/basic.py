"""Contains basic keyboard builder"""
from typing import Any

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from settings import SETTINGS_MANAGER


def get_basic_markup(tg_id: int) -> types.ReplyKeyboardMarkup:
    """Returns basic keyboard markup based on the user telegram id

    Args:
        tg_id (int): user telegram id

    Returns:
        Keyboard markup
    """

    commands = []

    if SETTINGS_MANAGER.is_subscribed(tg_id):
        commands.append("ОТПИСАТЬСЯ")
    else:
        commands.append("ПОДПИСАТЬСЯ")

    commands.append("МОЙ ID")

    if SETTINGS_MANAGER.is_owner(tg_id):
        commands += [
            "/getters",
            "/setters",
            "/actions",
        ]

    builder = ReplyKeyboardBuilder()
    for command in commands:
        builder.add(types.KeyboardButton(text=command))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def get_getters_markup(tg_id: int) -> types.ReplyKeyboardMarkup:
    """Returns getters keyboard markup based on the user telegram id

    Args:
        tg_id (int): user telegram id

    Returns:
        Keyboard markup
    """

    if not SETTINGS_MANAGER.is_owner(tg_id):
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="/back"))
        return builder.as_markup(resize_keyboard=True)

    commands = [
        "/subscribers",
        "/timers",
        "/owner",
        "/soft_prompt",
        "/should_translate_prompt",
        "/image_styles",
        "/available_image_styles",
    ]

    builder = ReplyKeyboardBuilder()
    for command in commands:
        builder.add(types.KeyboardButton(text=command))
    builder.adjust(2)
    builder.row(types.KeyboardButton(text="/back"))

    return builder.as_markup(resize_keyboard=True)


def get_setters_markup(tg_id: int) -> types.ReplyKeyboardMarkup:
    """Returns setters keyboard markup based on the user telegram id

    Args:
        tg_id (int): user telegram id

    Returns:
        Keyboard markup
    """

    if not SETTINGS_MANAGER.is_owner(tg_id):
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="/back"))
        return builder.as_markup(resize_keyboard=True)

    commands = [
        "/set_owner_alias",
        "/set_scrap_timer",
        "/set_post_timer",
        "/set_clean_timer",
        "/set_soft_prompt",
        "/set_should_translate_prompt",
        "/set_image_styles",
    ]

    builder = ReplyKeyboardBuilder()
    for command in commands:
        builder.add(types.KeyboardButton(text=command))
    builder.adjust(2)
    builder.row(types.KeyboardButton(text="/back"))

    return builder.as_markup(resize_keyboard=True)


def get_actions_markup(tg_id: int) -> types.ReplyKeyboardMarkup:
    """Returns actions keyboard markup based on the user telegram id

    Args:
        tg_id (int): user telegram id

    Returns:
        Keyboard markup
    """

    if not SETTINGS_MANAGER.is_owner(tg_id):
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="/back"))
        return builder.as_markup(resize_keyboard=True)

    commands = [
        "/scrap_force",
        "/scrap",
        "/post",
        "/post_to_owner",
        "/clean",
    ]

    builder = ReplyKeyboardBuilder()
    for command in commands:
        builder.add(types.KeyboardButton(text=command))
    builder.adjust(2)
    builder.row(types.KeyboardButton(text="/back"))

    return builder.as_markup(resize_keyboard=True)
