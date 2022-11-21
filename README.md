# Установка:
Клонируем репозиторий   
`git clone https://github.com/Conradk10/tonRocket-captcha-solver.git`   
Создаем виртуальное окружение   
`python3 -m venv env`   
Активируем виртуальное окружение   
`source env/bin/activate`   
Устанавливаем зависимости   
`python3 -m pip install -r requirements.txt`   
Готово!   
# Запуск:
Запускаем скрипт с активированным виртуальным окружением   
`python3 main.py`
# config.py
Получение `API_ID` и `API_HASH` из `config.py`   
Для начала нужно перейти по <a href="https://my.telegram.org/apps">этой</a> или <a href=https://my.telegram.org/auth>этой</a> ссылке   
Ввести номер телефона и нажать `API development tools`   
Скопировать `App api_id` и `App api_hash`   
`TEMP_DIR` и `SESSIONS_DIR` отвечают за директории с временными файлами и файлами сессий (`*.session`)   
В переменную `URL` необходимо ввести ссылку на чек   
В переменную `PASSWORD` необходимо ввести пароль от чека
# Зависимости:
```
hikka-tl==1.24.10
loguru==0.6.0
numpy==1.23.4
opencv-python==4.6.0.66
Pillow==9.3.0
```
