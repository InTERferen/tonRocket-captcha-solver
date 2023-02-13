## 📦 tonRocket captcha solver
<img src="https://i.imgur.com/f6Jb6qA.jpg"></img>  

<div align="center">

  <a href="https://img.shields.io/github/repo-size/Conradk10/tonRocket-captcha-solver" alt="GitHub repo size"><img src="https://img.shields.io/github/repo-size/Conradk10/tonRocket-captcha-solver" /></a>
  <a href="https://img.shields.io/github/issues/Conradk10/tonRocket-captcha-solver" alt="GitHub issues"><img src="https://img.shields.io/github/issues/Conradk10/tonRocket-captcha-solver" /></a>
  <a href="https://img.shields.io/github/license/Conradk10/tonRocket-captcha-solver" alt="GitHub"><img src="https://img.shields.io/github/license/Conradk10/tonRocket-captcha-solver" /></a>

</div>

- Скрипт предназначен для автоматизированной активации чеков из Telegram бота @tonRocketBot с множества аккаунтов  
## 💡 Обосенности:
- Поддерживает неограниченное количество сессий
- Поддерживает ввода пароля от чека
- Автоматическое прохождение капчи с подпиской на каналы/группы
- Автоматическое прохождение капчи с emoji
## 🛠 Установка:
1. Клонируем репозиторий   
`git clone https://github.com/Conradk10/tonRocket-captcha-solver.git`   
2. Переходим в директорию  
`cd tonRocket-captcha-solver`  
3. Создаем виртуальное окружение   
`python3 -m venv env`   
4. Активируем виртуальное окружение   
`source env/bin/activate`   
5. Устанавливаем зависимости   
`python3 -m pip install -r requirements.txt`
## ⚙️ config.py
- Получение `API_ID` и `API_HASH` из `config.py`   
1. Для начала нужно перейти по <a href="https://my.telegram.org/apps">этой</a> или <a href=https://my.telegram.org/auth>этой</a> ссылке   
2. Ввести номер телефона и нажать `API development tools`   
3. Создать приложение заполнив данные на свое усмотрение (если не создано ранее)  
4. Скопировать `App api_id` и `App api_hash` и заменить в файле `config.py` соответствующие переменные новыми значениями
- `TEMP_DIR` и `SESSIONS_DIR` отвечают за директории с временными файлами и файлами сессий (`*.session`)   
- В переменную `PASSWORD` необходимо ввести пароль от чека (если необходимо)
## ▶️ Запуск:
Запускаем скрипта осуществляем с активированным виртуальным окружением с помощью команды   
`python3 main.py [ссылка на чек (Пример: https://t.me/tonRocketBot?start=loremipsum)]`  
Либо с указанием ссылки в ходе выполнения скрипта  
`python3 main.py`
## 📝 Зависимости:
```
hikka-tl==1.24.10
loguru==0.6.0
numpy==1.23.4
opencv-python==4.6.0.66
Pillow==9.3.0
```
