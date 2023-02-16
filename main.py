#
#     d88P     d88P          888b    888          888
#      d88P   d88P           8888b   888          888
#       d88P d88P            88888b  888          888
#        d88888P    888888   888Y88b 888  .d88b.  888888
#        d88888P    888888   888 Y88b888 d8P  Y8b 888
#       d88P d88P            888  Y88888 88888888 888
#      d88P   d88P           888   Y8888 Y8b.     Y88b.
#     d88P     d88P          88.8    Y888  "Y8888   "Y888
#
#                      © Copyright 2023
#                    https://x-net.pp.ua
#                 https://github.com/Conradk10
#
#                 Licensed under the GNU GPLv3
#          https://www.gnu.org/licenses/agpl-3.0.html
#

import re
import sys
import asyncio

from loguru import logger

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import KeyboardButtonUrl, KeyboardButtonCallback

from config import (
    API_ID,
    API_HASH,
    DEVICE_MODEL,
    SYSTEM_VERSION,
    APP_VERSION,
    LANG_CODE,
    SYSTEM_LANG_CODE,
    URL,
    TEMP_DIR,
    PASSWORD,
    MAX_ATTEMPTS
)

from utils import get_sessions_list, parse_url, get_buttons_emoji


class Pattern:
    received = r'💰 Вы получили|💰 You received'
    activated = r'Этот мульти-чек уже активирован.|This multi-cheque already activated.'
    check_not_found = r'Мульти-чек не найден.|Multi-cheque not found.'
    activated_or_not_found = r'Этот мульти-чек уже активирован.|This multi-cheque already activated.|' \
                             r'Мульти-чек не найден.|Multi-cheque not found.'
    check_activated = r'Вы уже активировали данный мульти-чек.|You already activated this multi-cheque.'
    need_sub = r'Вам необходимо подписаться на следующие ресурсы чтобы активировать данный чек:|' \
               r'You need to subscribe to following resources to activate this cheque:'
    need_pass = r'Введите пароль для мульти-чека.|Enter password for multi-cheque.'
    need_premium = r'Этот чек только для пользователей с Telegram Premium.|' \
                   r'This cheque only for users with Telegram Premium.'


async def main():
    sessions = get_sessions_list()
    logger.info(f"Загружено сессий: {len(sessions)} шт.\n")
    logger.info(f"{', '.join(sessions)}")
    bot_url = parse_url(URL)
    logger.info(bot_url)
    if PASSWORD == "":
        logger.warning("Пароль не указан, могут возникнуть ошибки")
    for session in sessions:
        logger.info(f"Подключаемся через сессию {session}")
        client = TelegramClient(
            session=session,
            api_id=API_ID,
            api_hash=API_HASH,
            device_model=DEVICE_MODEL,
            system_version=SYSTEM_VERSION,
            app_version=APP_VERSION,
            lang_code=LANG_CODE,
            system_lang_code=SYSTEM_LANG_CODE
        )
        await client.start()
        logger.info(f"{session}: Подключено!")
        try:
            async with client.conversation(bot_url['bot']) as conv:
                attemp = 0
                while attemp < MAX_ATTEMPTS:
                    # Отправляем сообщение боту и получаем ответ
                    await conv.send_message(f'/{bot_url["command"]} {bot_url["args"]}')
                    message = await conv.get_response()
                    await asyncio.sleep(.5)
                    logger.info(f'Получено сообщение: {message.message}')
                    # Если чек полностью активирован или не существует
                    if re.search(Pattern.activated_or_not_found, message.message):
                        logger.warning('Чек полностью активирован или не существует')
                        sys.exit(0)
                    # Если чек активирован
                    if re.search(Pattern.check_activated, message.message):
                        logger.warning('Вы уже активировали этот чек')
                        break
                    # Если чек только для премиумов
                    if re.search(Pattern.need_premium, message.message):
                        logger.warning('Этот чек только для пользователей Telegram Premium')
                        break
                    # Если нужно подписаться на каналы
                    if re.search(Pattern.need_sub, message.message):
                        i = 0
                        for _ in message.reply_markup.rows:
                            for button in message.reply_markup.rows[i].buttons:
                                if button.text.startswith('❌') or button.text.startswith('🔎'):
                                    if isinstance(button, KeyboardButtonUrl):
                                        url = button.url
                                        if 't.me/joinchat/' in url:
                                            url = url.split('joinchat/')[1]
                                            await client(ImportChatInviteRequest(url))
                                        else:
                                            url = url.split('t.me/')[1]
                                            try:
                                                await client(JoinChannelRequest(url))
                                            except Exception as err:
                                                logger.error(err)
                                                logger.warning('Отправили заявку на вступление в канал')
                                        logger.info(f'Подписались на канал по ссылке: {url}')
                                        await asyncio.sleep(1)
                                    elif isinstance(button, KeyboardButtonCallback):
                                        await message.click(i)
                            i += 1
                    # Если получили капчу
                    if message.photo:
                        await message.download_media(f"{TEMP_DIR}/original.jpg")
                        btns = []
                        i = 0
                        for _ in message.reply_markup.rows:
                            for button in message.reply_markup.rows[i].buttons:
                                btns.append(button.text)
                            i += 1
                        _emoji = get_buttons_emoji(btns)
                        await message.click(btns.index(_emoji))
                        message = await conv.get_response()
                        logger.info(f"Нажали кнопку '{_emoji}'")
                    # Если получили запрос на ввод пароля
                    if re.search(Pattern.need_pass, message.message):
                        await conv.send_message(PASSWORD)
                        logger.info(f"Ввели пароль {PASSWORD}")
                    # Если получили вознаграждение
                    if re.search(Pattern.received, message.message):
                        logger.info(f'Получено сообщение: {message.message}')
                        break
                    attemp += 1
                    if attemp >= 6:
                        logger.warning('Что-то пошло не так... Переходим к следующей сессии')
                        break
        except Exception as err:
            logger.warning(f'Что-то пошло не так ({err})... Переходим к следующей сессии')
        logger.info(f"{session}: Отключаемся...")
        await client.disconnect()
    logger.info("Сессий больше нет")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
