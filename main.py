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

import asyncio
import sys

from loguru import logger

from telethon.sync import TelegramClient
from tgchequeman import exceptions, activate_multicheque, parse_url

from config import (
    API_ID, API_HASH, DEVICE_MODEL, SYSTEM_VERSION,
    APP_VERSION, LANG_CODE, SYSTEM_LANG_CODE, URL, PASSWORD,
)

from utils import get_sessions_list


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
            await activate_multicheque(
                client=client,
                bot_url=bot_url,
                password=PASSWORD
            )
        except (exceptions.ChequeFullyActivatedOrNotFound, exceptions.PasswordError) as err:
            logger.error(err)
            await client.disconnect()
            sys.exit(1)
        except (exceptions.ChequeActivated,
                exceptions.ChequeForPremiumUsersOnly,
                exceptions.CannotActivateOwnCheque) as warn:
            logger.warning(warn)
            break
        except exceptions.UnknownError as err:
            logger.error(err)
            break
        except Exception as err:
            logger.error(err)
        logger.info(f"{session}: Отключаемся...")
        await client.disconnect()
    logger.info("Сессий больше нет")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
