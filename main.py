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
    PASSWORD
)
from utils import get_sessions_list, parse_url, get_buttons_emoji

check_activated = ['Вы уже активировали данный мульти-чек.', 'You already activated this multi-cheque.']
activated = ['Этот мульти-чек уже активирован.', 'This multi-cheque already activated.']
need_sub = ['Вам необходимо подписаться на следующие ресурсы чтобы активировать данный чек:',
            'You need to subscribe to following resources to activate this cheque:']
need_pass = ['Введите пароль для мульти-чека.', 'Enter password for multi-cheque.']
check_not_found = ['Мульти-чек не найден.', 'Multi-cheque not found.']
received = ['💰 Вы получили', '💰 You received']


async def main():
    sessions = get_sessions_list()
    logger.info(f"Сессии: {sessions}")
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
        logger.info(f"{session}: Подключено!")

        class message:
            message = ""
        i = 0
        await client.start()
        try:
            async with client.conversation(bot_url['bot']) as conv:
                await asyncio.sleep(0.5)
                while received[0] not in message.message or received[1] not in message.message or i < 10:
                    exitFlag = False
                    await conv.send_message(f'/{bot_url["command"]} {bot_url["args"]}')
                    message = await conv.get_response()
                    logger.info(f'Получено сообщение: {message.message}')
                    # Если чек активирован или не существует
                    if message.message in check_activated or message.message in check_not_found or \
                            message.message in activated:
                        logger.warning(f'Получено сообщение: {message.message}')
                        exitFlag = True
                    else:
                        pass
                    # Если нужно подписаться на каналы
                    if message.message in need_sub:
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
                        for row in message.reply_markup.rows:
                            for button in message.reply_markup.rows[i].buttons:
                                btns.append(button.text)
                            i += 1
                        _emoji = get_buttons_emoji(btns)
                        await message.click(btns.index(_emoji))
                        message = await conv.get_response()
                        logger.info(f"Нажали кнопку '{_emoji}'")
                    # Если получили ввод пароля
                    if need_pass[0] in message.message or need_pass[1] in message.message:
                        await conv.send_message(PASSWORD)
                        logger.info(f"Ввели пароль {PASSWORD}")
                    # Если получили
                    if received[0] in message.message or received[1] in message.message:
                        logger.info(f'Получено сообщение: {message.message}')
                        exitFlag = True
                    i += 1
                    if i >= 6:
                        logger.warning('Что-то пошло не так... Переходим к следующей сессии')
                        exitFlag = True
                    if exitFlag:
                        conv.cancel()
        except asyncio.exceptions.CancelledError:
            logger.warning('Что-то пошло не так... Переходим к следующей сессии')

        logger.info(f"{session}: Отключаемся...")
        await client.disconnect()
    logger.info("Сессий больше нет")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
