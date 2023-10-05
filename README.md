# Telegram_Bot

Асинхронный Telegram Бот AKIRA для знакомств (с системой администрирования и поддержкой)
<h5> [ Aiogram, PostgreSQL, Redis, Docker Compose ] </h5>


Система состоит из Frontend, Backend, PgSQL и Redis.
- Взаимодействие с бд происходит в [schema.py](services/matchbot/db/schema.py) с помощью библиотеки `psycopg`
- Взаимодействие с Telegram через асинхронную библиотеку `aiogram`
- Сборка в контейнеры прописана в [docker-compose.yaml](docker-compose.yaml)
- Уже запущен в прод на VM, [можно тестить](https://t.me/akira_matchbot=start?ref).
- В качестве NoSQL используется `Redis` для оптимизации SQL запросов.

Структура взаимодейтсивя элементов системы:
![alt text](photos/system_diagram.png)

В качестве Frontend выступает приложение Telegram, которое принимает сообщения в качестве комманд от пользователей. Backend взаимодействует с Frontend по API из асинхронной библиотеки aiogram. В качестве бд выступают PgSQL и Redis (используется для хранения информации о состоянии пользователя и промежуточных данных для оптимизации запросов к PgSQL).

Idef0 диаграмма бота:

![alt text](photos/idef0.png)


Конечный автомат системы:

![alt text](photos/state_machine.png)


Схема таблиц в [бд](services/matchbot/db/schema.py):

![alt text](photos/tables.png)