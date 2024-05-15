import sys

API_ID = 21341908
API_HASH = "17e56b43ce562386d027ff2b69d2240f"
DEVICE_MODEL = "PC 64bit"
SYSTEM_VERSION = "Windows 10"
APP_VERSION = "4.6"
LANG_CODE = "ru"
SYSTEM_LANG_CODE = "ru-RU"

try:
    URL = sys.argv[1]
except IndexError:
    URL = input("Укажите ссылку на чек (Пример: https://t.me/tonRocketBot?start=loremipsum): ")

# ПАРОЛЬ УКАЗАТЬ ПОСЛЕ ЗАПУСКА СКРИПТА
PASSWORD = input("Введите пароль от чека (если пароля нет то просто нажмите Enter): ")
