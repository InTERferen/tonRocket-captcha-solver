import os
import sys
import cv2
import errno
import numpy

from loguru import logger
from PIL import Image, ImageFont, ImageDraw

from config import TEMP_DIR, SESSIONS_DIR

# Шрифт для отрисовки emoji
if sys.platform == "darwin":
    font_size = 109
else:
    font_size = 137
fnt = ImageFont.truetype("AppleColorEmoji.ttf", size=font_size, layout_engine=ImageFont.Layout.RAQM)


def parse_url(url: str) -> dict:
    result = {}
    try:
        result = {
            "bot": url.split('t.me/')[1].split('?')[0],
            "command": url.split('t.me/')[1].split('?')[1].split('=')[0],
            "args": url.split('t.me/')[1].split('?')[1].split('=')[1]
        }
    except Exception as err:
        logger.error(err)
        logger.error('Ссылка в конфиге введена неверно!')
        exit(1)
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
            raise


def get_sessions_list() -> list:
    check_sessions_folder()

    result = []
    for path in os.listdir(SESSIONS_DIR):
        if os.path.isfile(os.path.join(SESSIONS_DIR, path)):
            if path.endswith(".session"):
                result.append(SESSIONS_DIR + "/" + path)
    if not len(result):
        logger.error("Ни одной сесси не найдено")
        raise

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
