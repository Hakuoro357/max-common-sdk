# Спецификация моделирования маршрутов OpenAPI для MAX SDK

## 1. Цель

Зафиксировать, как описывать реальные HTTP-маршруты MAX API в каноническом `OpenAPI`, если:

- у API есть конфликтующие templated paths
- один и тот же wire-path обслуживает разные семантики
- прямое описание маршрута ломает `OpenAPI`-валидность или codegen

Ключевая задача:

> Канонический контракт должен оставаться валидным и пригодным для генерации, даже если реальный HTTP API допускает неоднозначные маршруты.

## 2. Проблема

В MAX API встречается паттерн:

- `GET /chats/{chat_id}`
- `GET /chats/{chat_link}`

На wire-уровне это разные сценарии.

Для `OpenAPI` это один и тот же templated path:

- `/chats/{something}`

Такой контракт:

- неоднозначен
- плохо подходит для codegen
- не даёт стабильной surface area для multi-language SDK

## 3. Базовый принцип

В каноническом `OpenAPI` приоритет у:

1. однозначности
2. валидности схемы
3. пригодности для генерации
4. стабильности SDK surface

Точное совпадение с wire-path важно, но не ценой сломанного контракта.

## 4. Принятая модель

Для конфликтующих маршрутов вводится разделение:

- `spec path`
- `wire path`

### `spec path`

Это путь, который хранится в каноническом `OpenAPI`.

Он обязан быть:

- уникальным
- однозначным
- пригодным для codegen

### `wire path`

Это реальный HTTP path, который должен уйти в сеть.

Он может совпадать со `spec path`, а может отличаться.

## 5. Правило для ambiguous templated routes

Если два публичных метода конфликтуют на уровне `OpenAPI`, каноническая схема должна использовать **spec-safe alias path**.

Пример:

- метод `getChatById`
  - `spec path`: `/chats/{chat_id}`
  - `wire path`: `/chats/{chat_id}`
- метод `getChatByLink`
  - `spec path`: `/chats/by-link/{chat_link}`
  - `wire path`: `/chats/{chat_link}`

То есть:

- в контракте путь делается явным и уникальным
- в runtime сохраняется реальный сетевой путь

## 6. Vendor extension

Для хранения реального сетевого маршрута вводится vendor extension:

- `x-max-wire-path`

Пример:

```yaml
/chats/by-link/{chat_link}:
  get:
    operationId: getChatByLink
    x-max-wire-path: /chats/{chat_link}
```

Если extension отсутствует, runtime должен использовать обычный `path` из `OpenAPI`.

## 7. Требования к codegen

Generator pipeline должен работать так:

1. читать `spec path` как канонический путь схемы
2. читать `x-max-wire-path`, если он есть
3. сохранять оба значения в `IR`
4. генерировать SDK methods по `operationId`
5. использовать `wire path` в runtime-вызове
6. использовать `spec path` для:
   - diff analysis
   - route uniqueness
   - contract tests
   - документации по структуре API

## 8. Naming rules для alias paths

Alias path должен:

- быть детерминированным
- быть понятным человеку
- не зависеть от конкретного языка SDK

Рекомендуемые шаблоны:

- `/resource/by-id/{id}` только если исходный путь реально неочевиден
- `/resource/by-link/{link}`
- `/resource/by-username/{username}`
- `/resource/by-slug/{slug}`
- `/resource/by-code/{code}`

Нельзя использовать:

- случайные технические префиксы
- внутренние сокращения
- нестабильные alias-имена

## 9. Правила документации

В спецификациях и SDK docs нужно различать:

- `canonical spec path`
- `actual wire path`

Если они различаются, это должно быть явно отмечено.

Важно:

- для codegen и governance главным считается `spec path`
- для transport/runtime главным считается `wire path`

## 10. Что запрещено

Нельзя:

- хранить в каноническом `OpenAPI` два конфликтующих templated path
- решать неоднозначность на уровне языка SDK вручную, без отражения в контракте
- прятать wire-path override только в runtime-коде
- допускать, чтобы разные языки по-разному интерпретировали один и тот же alias path

## 11. Decision for MAX

Для MAX принимается правило:

> Если реальный API содержит ambiguous templated route, в `OpenAPI` используется spec-safe alias path с обязательным `x-max-wire-path`.

Первый практический кейс:

- `getChatByLink`

Целевое описание:

- `spec path`: `/chats/by-link/{chat_link}`
- `wire path`: `/chats/{chat_link}`

## 12. Impact

Такой подход даёт:

- валидный `OpenAPI`
- стабильный `IR`
- детерминированный codegen
- возможность покрыть реальный API без потери совместимости

Компромисс один:

- канонический путь в схеме иногда будет отличаться от wire-path

Этот компромисс считается допустимым и правильным для multi-language SDK платформы.
