import sys

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
DEVICE_MODEL = "PC 64bit"
SYSTEM_VERSION = "Windows 10"
APP_VERSION = "4.6"
LANG_CODE = "ru"
SYSTEM_LANG_CODE = "ru-RU"

TEMP_DIR = "temp"  # Не менять
SESSIONS_DIR = "sessions"  # Не менять

MAX_ATTEMPTS = 10   # Максимальное количество попыток активации чека

try:
    URL = sys.argv[1]
except IndexError:
    URL = input("Укажите ссылку на чек (Пример: https://t.me/tonRocketBot?start=loremipsum): ")

# ПАРОЛЬ УКАЗАТЬ ПОСЛЕ ЗАПУСКА СКРИПТА
PASSWORD = input("Введите пароль от чека (если пароля нет то просто нажмите Enter): ")
