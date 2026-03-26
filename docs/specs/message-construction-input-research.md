# Исследование `MessageConstructionRequestUpdate.input`

## 1. Вопрос

Нужно понять, можно ли безопасно типизировать поле:

- `MessageConstructionRequestUpdate.input`

или его пока нужно оставлять как `raw object`.

## 2. Что подтверждено

### Официальный TypeScript SDK MAX

В официальном `max-bot-api-client-ts` это поле уже типизировано как:

- `input: unknown`

Вывод:

- официальный TS SDK не фиксирует структуру `input`
- это выглядит как сознательное решение, а не случайный пропуск

### Официальный Go SDK MAX

В официальном `max-bot-api-client-go` update discriminator не содержит:

- `message_construction_request`
- `message_constructed`

Вывод:

- Go SDK не даёт альтернативную строгую модель `input`
- этот update family там вообще пока не доведён до полноценной поддержки

### Официальный Java SDK MAX

В официальном `max-bot-api-client-java` список `Update` subtypes также не содержит:

- `message_construction_request`
- `message_constructed`

Вывод:

- Java SDK тоже не подтверждает структуру `input`

## 3. Итоговый вывод

На текущем этапе `MessageConstructionRequestUpdate.input` **не нужно типизировать жёстко**.

Правильное текущее решение:

- оставить `input` как `raw object` в каноническом `OpenAPI`
- в generated SDK оставлять его как:
  - `unknown` в `TypeScript`
  - `dict[str, Any]` / raw object в `Python`
  - `Dictionary<string, object?>` / raw object в `C#`

## 4. Почему это решение корректно

- оно совпадает с поведением официального TS SDK
- оно не противоречит официальным Go/Java SDK
- оно не выдумывает контракт там, где MAX сам его пока не зафиксировал

## 5. Что считается достаточным основанием для будущей типизации

Типизировать `input` можно только если появится хотя бы один из сигналов:

- официальная object-doc страница MAX с формой `input`
- официальный пример payload от MAX с повторяемой структурой
- обновление официального TS SDK, где `unknown` заменён на явный тип
- обновление официальных Go/Java SDK с полноценной моделью этого update

## 6. Решение для проекта

До появления такого сигнала в проекте действует правило:

- `MessageConstructionRequestUpdate.input` считается осознанным исключением
- это поле не входит в backlog безопасной типизации
- попытки типизировать его по догадке считаются нежелательными
