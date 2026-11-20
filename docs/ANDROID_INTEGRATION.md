# Подключение Android-клиентов к `home-node-linux`

Документ фиксирует актуальное состояние сервера `home-node-linux` (`v0.1.0`, FastAPI + Uvicorn) и правила взаимодействия с ним для клиентов экосистемы `home-node` (`home-node-android`, `traffic-tracker-android`).

---

## 1. Архитектура и роль узла

* **`home-node-linux` (Linux/WSL, Python >= 3.10):**
  * HTTP/JSON-шлюз на базе **FastAPI** и **Uvicorn** (`src/home_node_linux/main.py`, `routes.py`, `config.py`).
  * Работает поверх пакета `core.db_connection` (`platform_meta` / Vault с шифрованием AES-GCM, без хранения паролей БД, `.env` или `vault.yaml` в репозитории).
  * Для работы с PostgreSQL используется пул соединений (`db.py` на базе `psycopg` / `psycopg_pool` с закрытием через `atexit.register(close_all_pools)`), а в роутах проверки доступности проекта — `db_connection.gateway.ping_project`.
* **Android-клиенты (`home-node-android`, `traffic-tracker-android`):**
  * работают в среде Kotlin (в том числе связка Ktor + Netty, Room, синхронизация);
  * обращаются к `home-node-linux` по сети (LAN или WireGuard);
  * не подключаются к PostgreSQL напрямую и не имеют доступа к Vault и мастер-ключу `vault.yaml`.

---

## 2. Конфигурация и безопасность

* **Хост и порт по умолчанию:**
  * `HOME_NODE_HOST` = `"0.0.0.0"`
  * `HOME_NODE_PORT` = `8090`
* **Список разрешённых проектов:**
  * `HOME_NODE_ALLOWED_PROJECTS` (по умолчанию в `config.py`: `"household,traffic_tracker"`).
  * При добавлении новых БД/проектов (например, `home-node-android` и `traffic-tracker-android`) необходимо сверить их имена в `HOME_NODE_ALLOWED_PROJECTS` и в конфигурации Vault/БД.
* **Ограничения безопасности (`SECURITY.md`):**
  * не коммитить пароли БД, `.env` и `vault.yaml`;
  * не открывать raw SQL и административные ручки без авторизации и сетевых ограничений.

---

## 3. Текущие HTTP-эндпоинты и формат ответа

Все ответы сервера оборачиваются в единую структуру:

```json
{
  "ok": true,
  "data": {},
  "error": null
}