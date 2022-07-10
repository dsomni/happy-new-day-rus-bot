import concurrent.futures as pool
from telebot import TeleBot, types
import time
from datetime import datetime
from scrapper import scrapper
from utils import load_config, save_config


configs = load_config()

DEFAULT_SLEEP_PERIOD = 60  # seconds
DEFAULT_SCRAP_TIME = 25200  # 7am GMT, seconds

bot = TeleBot(configs.get("API_TOKEN") or "")
OWNER = configs.get("OWNER") or ""

respondents = configs.get("RESPONDENTS") or []
period = int(configs.get("SLEEP_PERIOD_S") or DEFAULT_SLEEP_PERIOD)
scrap_time = int(configs.get("SCRAP_TIME_S") or DEFAULT_SCRAP_TIME)
should_scrap = False
is_busy = False
last_fetch = 0


def extract_arg(arg):
    return arg.split()[1:]


def is_owner(message):
    return str(message.chat.id) == OWNER


def check_owner(func):
    global OWNER

    def inner(message):
        if not is_owner:
            print("Permission denied")
            return

        return func(message)

    return inner


def describe(user_id):
    global respondents, configs
    try:
        respondents.remove(user_id)
        configs["RESPONDENTS"] = respondents
        save_config(configs)
        return 0
    except:
        return 1


def subscribe(user_id):
    global respondents, configs
    try:
        respondents.append(user_id)
        configs["RESPONDENTS"] = respondents
        save_config(configs)
        return 0
    except:
        return 1


def get_markup(subscribed: bool, is_owner: bool = False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if subscribed:
        markup.add(types.KeyboardButton("Отписаться"))  # type: ignore
    else:
        markup.add(types.KeyboardButton("Подписаться"))  # type: ignore
    if is_owner:
        markup.add(types.KeyboardButton("/scrap"))  # type: ignore
        markup.add(types.KeyboardButton("/get_scrap_time"))  # type: ignore
        markup.add(types.KeyboardButton("/get_sleep_period"))  # type: ignore
        markup.add(types.KeyboardButton("/stop"))  # type: ignore
    return markup


def is_subscribed(message) -> bool:
    global respondents
    user_id = str(message.chat.id)
    if user_id in respondents:
        return True
    return False


def with_markup(func):
    global OWNER

    def inner(message):

        return func(message, get_markup(is_subscribed(message), is_owner(message)))

    return inner


@bot.message_handler(commands=["start"])
@with_markup
def start(message, markup):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать!",
        reply_markup=markup,
    )


@bot.message_handler(commands=["stop"])
@check_owner
@with_markup
def stop(message, markup):

    bot.send_message(message.chat.id, "Всем удачи, всем пока!", reply_markup=markup)
    try:
        bot.stop_polling()
        bot.stop_bot()
        exit(0)
    except BaseException:
        pass
    exit(0)


@bot.message_handler(commands=["scrap"])
@check_owner
def scrap_to_channel(message):
    global should_scrap, is_busy
    is_busy = True
    should_scrap = True


@bot.message_handler(commands=["get_sleep_period"])
@check_owner
@with_markup
def get_sleep_period(message, markup):
    global period
    hours = period // 3600
    minutes = (period - hours * 3600) // 60
    seconds = period % 60
    bot.send_message(message.chat.id, f"{hours:02d}:{minutes:02d}:{seconds:02d}", reply_markup=markup)


@bot.message_handler(commands=["set_sleep_period"])
@check_owner
@with_markup
def set_sleep_period(message, markup):
    global period, configs
    try:
        time = extract_arg(message.text)[0]
        hours, minutes, seconds = map(int, time.split(":"))
        if hours < 0 or minutes < 0 or seconds < 0:
            raise BaseException
        period = hours * 60 * 60 + minutes * 60 + seconds

        configs["SLEEP_PERIOD_S"] = period
        save_config(configs)
        bot.send_message(message.chat.id, "Период сна успешно обновлено", reply_markup=markup)
    except:
        bot.reply_to(
            message,
            f"Некорректный формат времени\nОжидалось:\n\n{message.text.split()[0]} hh:mm:ss",
            reply_markup=markup,
        )


@bot.message_handler(commands=["get_scrap_time"])
@check_owner
@with_markup
def get_scrap_time(message, markup):
    # from +3 to GMT
    hours = (scrap_time // 3600 + 3) % 24
    minutes = (scrap_time - hours * 3600) // 60
    bot.send_message(message.chat.id, f"{hours:02d}:{minutes:02d}", reply_markup=markup)


@bot.message_handler(commands=["set_scrap_time"])
@check_owner
@with_markup
def set_scrap_time(message, markup):
    global scrap_time, configs
    try:
        time = extract_arg(message.text)[0]
        hours, minutes = map(int, time.split(":"))
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise BaseException
        scrap_time = hours * 60 * 60 + minutes * 60

        # from +3 to GMT
        scrap_time -= 3 * 60 * 60
        if scrap_time < 0:
            scrap_time += 24 * 60 * 60

        configs["SCRAP_TIME_S"] = scrap_time
        save_config(configs)
        bot.send_message(message.chat.id, "Время скраппинга успешно обновлено", reply_markup=markup)
    except:
        bot.reply_to(
            message, f"Некорректный формат времени\nОжидалось:\n\n{message.text.split()[0]} hh:mm", reply_markup=markup
        )


@bot.message_handler(content_types=["text"])
@with_markup
def handle_text(message, markup):
    global OWNER, respondents
    is_this_owner = is_owner(message)
    if message.text == "Отписаться":
        code = describe(str(message.chat.id))
        if code == 0:
            bot.send_message(message.chat.id, "Вы успешно отписались", reply_markup=get_markup(False, is_this_owner))
        else:
            bot.send_message(message.chat.id, "Вот блин что-то упало", reply_markup=get_markup(True, is_this_owner))
        return
    if message.text == "Подписаться":
        code = subscribe(str(message.chat.id))
        if code == 0:
            bot.send_message(message.chat.id, "Вы успешно подписались", reply_markup=get_markup(True, is_this_owner))
        else:
            bot.send_message(message.chat.id, "Вот блин что-то упало", reply_markup=get_markup(False, is_this_owner))
        return

    if not message.forward_from or str(message.chat.id) != OWNER:
        bot.send_message(message.chat.id, f"Лол, я не знаю, что ответить на '{message.text}' )))", reply_markup=markup)
        return
    user_id = str(message.forward_from.id)
    if user_id in respondents:
        describe(user_id)
        bot.send_message(
            message.chat.id,
            f"@{message.forward_from.username} успешно удалён из респондентов",
            reply_markup=get_markup(False, True),
        )
        return
    else:
        subscribe(user_id)
        bot.send_message(
            message.chat.id,
            f"@{message.forward_from.username} успешно добавлен к респондентам",
            reply_markup=get_markup(True, True),
        )
        return


def get_current_time_s() -> int:
    return int(datetime.now().timestamp())


def check_scrap_time() -> None:
    global scrap_time, should_scrap, period
    current_time = get_current_time_s()

    lower_bound = current_time - period // 2
    upper_bound = current_time + period // 2
    fetch_time = (current_time // 86400) * 86400 + scrap_time

    if lower_bound <= fetch_time < upper_bound:
        should_scrap = True


def start_msg_queue(results: list) -> None:
    global bot, is_busy
    for msg in results:
        for respondent in respondents:
            try:
                bot.send_message(respondent, str(msg))
                time.sleep(3.1)
            except:
                pass
    is_busy = False


def run_bot():
    global bot
    bot.infinity_polling()


def main():
    global channel, should_scrap, is_busy
    try:
        with pool.ThreadPoolExecutor(3) as executor:

            bot_process = executor.submit(run_bot)
            while bot_process.running():
                check_scrap_time()
                if should_scrap:
                    is_busy = True
                    should_scrap = False

                    holidays = scrapper()

                    executor.submit(start_msg_queue, holidays)
                time.sleep(period)
    except BaseException:
        exit(0)


if __name__ == "__main__":
    should_scrap = False
    main()