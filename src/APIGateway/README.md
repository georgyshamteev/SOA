# API Gateway

## Описание

API Gateway является центральным компонентом, который принимает все входящие HTTP-запросы от клиента (в нашем случае несуществующий UI) и перенаправляет их к соответствующим сервисам системы. Это позволяет унифицировать точку входа в систему и управлять всеми внешними запросами в одном месте.

## Зоны ответственности

- Прием и проверка всех входящих запросов от клиента.
- Прокси-сервер для пересылки запросов к соответствующим микросервисам (UserService, PostsService, StatisticsService).
- Обработка ошибок и возврат соответствующих ответов клиенту.

## Границы сервиса

- Не хранит данные пользователей или бизнес-логику.
- Не занимается обработкой бизнес-данных, кроме маршрутизации запросов.
- Должен обеспечивать высокую доступность и масштабируемость для обработки большого числа запросов.