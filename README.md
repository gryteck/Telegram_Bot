# Telegram_Bot

Асинхронный Telegram Бот AKIRA для знакомств (с системой администрирования и поддержкой)
<h5> Стек технологий: Telegram API (aiogram), PostgreSQL (sqlalchemy, asyncpg), Redis (aioredis), Docker Compose</h5>

- Взаимодействие с Telegram через асинхронную библиотеку `aiogram`
- Взаимодействие с `PostgreSQL` происходит асинхронно в [crud.py](services/matchbot/db/crud.py) с помощью библиотеки `sqlalchemy`
- В качестве NoSQL используется `Redis` для оптимизации SQL запросов в [].
- Сборка в контейнеры прописана в [docker-compose.yaml](docker-compose.yaml)
- Уже запущен в прод и развернут на сервере, [можно тестить](https://t.me/akira_matchbot=start?ref).


Структура взаимодействия элементов системы:
![alt text](photos/system_diagram.png)

В качестве Frontend выступает приложение Telegram, которое принимает сообщения в качестве комманд от пользователей. Backend взаимодействует с Frontend по API из асинхронной библиотеки aiogram. В качестве бд выступают PgSQL и Redis (используется для хранения информации о состоянии пользователя и промежуточных данных для оптимизации запросов к PgSQL).

Idef0 диаграмма бота:

![alt text](photos/idef0.png)


Конечный автомат системы:

![alt text](photos/state_machine.png)


Схема таблиц в [models.py](services/matchbot/db/models.py):

![alt text](photos/tables.png)