import os
import re
import sys
import cv2
import errno
import numpy
import asyncio

from loguru import logger
from PIL import Image, ImageFont, ImageDraw

from telethon.client.telegramclient import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import KeyboardButtonUrl, KeyboardButtonCallback

TEMP_DIR = "temp"  # Не менять
SESSIONS_DIR = "sessions"  # Не менять
MAX_ATTEMPTS = 10   # Максимальное количество попыток активации чека


class Pattern:
    """
    Этот класс содержит набор шаблонов регулярных выражений, которые используются в различных частях программы
    """
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


# Шрифт для отрисовки emoji
if sys.platform == "darwin":
    font_size = 109
else:
    font_size = 137
fnt = ImageFont.truetype("AppleColorEmoji.ttf", size=font_size, layout_engine=ImageFont.Layout.RAQM)


async def activate_multicheque(client: TelegramClient, bot_url: dict, password: str):
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
                await conv.send_message(password)
                logger.info(f"Ввели пароль {password}")
            # Если получили вознаграждение
            if re.search(Pattern.received, message.message):
                logger.info(f'Получено сообщение: {message.message}')
                break
            attemp += 1
            if attemp >= 6:
                logger.warning('Что-то пошло не так... Переходим к следующей сессии')
                break


def parse_url(url: str) -> dict:
    try:
        result = {
            "bot": url.split('t.me/')[1].split('?')[0],
            "command": url.split('t.me/')[1].split('?')[1].split('=')[0],
            "args": url.split('t.me/')[1].split('?')[1].split('=')[1]
        }
    except Exception as err:
        logger.error(err)
        logger.error('Ссылка в конфиге введена неверно!')
        sys.exit(1)
    return result


def check_sessions_folder():
    try:
        os.mkdir(SESSIONS_DIR)
        logger.info('Директория для сессий создана')
    except OSError as e:
        if e.errno == errno.EEXIST:
            logger.warning('Директория для сессий уже существует. Пропускаем...')
        else:
            logger.error('Не могу создать дерикторию для сессий')
            raise Exception


def get_sessions_list() -> list:
    check_sessions_folder()

    result = []
    for path in os.listdir(SESSIONS_DIR):
        if os.path.isfile(os.path.join(SESSIONS_DIR, path)):
            if path.endswith(".session"):
                result.append(SESSIONS_DIR + "/" + path)
    if not result:
        logger.error("Ни одной сесси не найдено")
        raise Exception

    return result


def check_temp_folder():
    try:
        os.mkdir(TEMP_DIR)
        logger.info('Директория для временных файлов создана')
    except OSError as e:
        if e.errno == errno.EEXIST:
            logger.warning('Директория для временных файлов уже существует. Пропускаем...')
        else:
            logger.error('Не могу создать дерикторию для временных файлов')
            raise


def get_buttons_emoji(emojis: list[str]) -> str:
    """Возвращает строку с наиболее вероятным ответом emoji

    :param image: Принимает Image из PILLOW оригинальной картинки
    :param emojis: Принимает список emoji из кнопок
    :return: Возвращает строку с наиболее вероятным ответом emoji
    """
    check_temp_folder()
    image = Image.open(f"{TEMP_DIR}/original.jpg")
    original = cv2.imread(f"{TEMP_DIR}/original.jpg")
    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    original_color = recognize_color(image)
    i = 0
    _mse = 9999999
    _emoji = ""
    for emoji in emojis:
        image = generate_emoji_image(emoji, original_color)
        image.save(f"{TEMP_DIR}/{i}.jpg")
        different = cv2.imread(f"{TEMP_DIR}/{i}.jpg")
        different = cv2.cvtColor(different, cv2.COLOR_BGR2GRAY)
        mse = eval_mse(original, different)
        if mse < _mse:
            _mse = eval_mse(original, different)
            _emoji = emoji
        i += 1
    logger.info(f'Распознаны эмоджи: {_emoji} (mse: {_mse})')
    return _emoji


def eval_mse(imageA, imageB) -> numpy.ndarray:
    logger.info(f'Сравниваю изображения')
    err = numpy.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err


def recognize_color(imgae: Image) -> tuple:
    logger.info(f'Получаю фоновый цвет оригинального изображения')
    pix = imgae.load()
    return pix[1, 1]


def generate_emoji_image(emoji_text: str, color: tuple) -> Image:
    logger.info(f'Генерирую изображение с текстом "{emoji_text}" и цветом "{color}"')
    text = emoji_text.split(" ")
    ORIGINAL_SIZE = (472, 283)
    SIZE = (472 * 2, 283 * 2)
    W, H = SIZE
    image = Image.new('RGB', SIZE, color)
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), " ".join(text), font=fnt)
    draw.text(((W - w) / 2 + 94, (H - h) / 2 - 1), text[0], font=fnt, fill='black', embedded_color=True)
    draw.text(((W - w) / 2 + (w / 2 - 68), (H - h) / 2 - 1), text[1], font=fnt, fill='black', embedded_color=True)
    draw.text(((W - w) / 2 + (w - 229), (H - h) / 2 - 1), text[2], font=fnt, fill='black', embedded_color=True)
    image = image.resize(ORIGINAL_SIZE)
    logger.info(f'Изображение с текстом "{emoji_text}" и цветом "{color} сгенерировано')
    return image
