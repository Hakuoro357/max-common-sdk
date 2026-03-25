# Спецификация будущей архитектуры multi-language SDK для MAX

## 1. Цель

Построить архитектуру SDK, в которой:

- API-контракт определяется один раз
- low-level клиенты для разных языков генерируются из общего источника
- high-level SDK остаются нативными для каждого языка
- тесты совместимости и релизы управляются централизованно

Ключевой принцип:

> Один общий контракт и одна генерационная платформа, но не одна общая реализация SDK на все языки.

## 2. Базовое решение

Архитектура должна быть `spec-first`.

Единым источником правды выступает спецификация API:

- `OpenAPI`
- `JSON Schema` для моделей и событий
- единое описание ошибок, пагинации, лимитов, webhook/update payload

На основе этой спецификации строятся:

- generated low-level clients
- документация
- contract tests
- примеры

## 3. Главный вывод

Сделать одну универсальную реализацию SDK и затем просто переносить ее на разные языки нельзя без потери качества.

Причины:

- разные async-модели
- разные HTTP-стеки
- разные сериализаторы
- разные соглашения по naming и API ergonomics
- разные механизмы middleware / interceptors / handlers
- разные экосистемы публикации пакетов

Следовательно:

- общий должен быть контракт
- общий должен быть pipeline генерации
- high-level слой должен реализовываться отдельно под каждый язык

## 4. Целевая структура monorepo

```text
max-sdk/
  api/
    openapi/
      max-bot-api.yaml
    schemas/
    examples/
    changelog/

  generators/
    core/
    templates/
      typescript/
      go/
      java/
      python/
      csharp/
      php/
      kotlin/

  runtimes/
    typescript/
    go/
    java/
    python/
    csharp/
    php/
    kotlin/

  sdks/
    typescript/
      client/
      bot/
      webhook/
    go/
      client/
      bot/
      webhook/
    java/
      client/
      bot/
      webhook/
    python/
      client/
      bot/
      webhook/
    csharp/
      client/
      bot/
      webhook/
    php/
      client/
      bot/
      webhook/
    kotlin/
      client/
      bot/
      webhook/

  tests/
    contract/
    fixtures/
    compatibility/
    e2e/

  docs/
    architecture/
    api-guidelines/
    release-process/
    migration-guides/

  tools/
    lint/
    release/
    diff/
    codegen/

  .github/
    workflows/
```

## 5. Слои архитектуры

### 5.1 `api/`

Содержит:

- спецификацию методов
- модели запросов и ответов
- webhook/update schema
- auth contract
- error model
- pagination rules
- rate limit contract
- политику версионирования API

Это единственный канонический слой, от которого должны зависеть все остальные.

### 5.2 `generators/`

Содержит:

- core generator logic
- шаблоны генерации по языкам
- правила преобразования schema -> code

Генерирует:

- DTO / models
- enums
- thin API methods
- request / response mapping
- базовые exception / error types
- docs snippets
- примеры использования

### 5.3 `runtimes/`

Содержит языко-зависимую инфраструктуру:

- HTTP transport abstraction
- auth injection
- retries / backoff
- timeout handling
- serialization hooks
- middleware / interceptor points
- logging / tracing integration points
- upload / download primitives

`runtime` не должен знать бизнес-логику ботов, только транспорт и техническую обвязку.

### 5.4 `sdks/`

Содержит пользовательский слой SDK.

Типовые модули:

- `client` — thin generated client
- `bot` — high-level framework для ботов
- `webhook` — интеграции с web frameworks

High-level слой реализуется вручную и делается idiomatic для конкретного языка.

## 6. Правила разделения generated и manual кода

### Генерируется

- модели
- методы API
- enums
- базовые ошибки
- request builders
- часть документации

### Пишется вручную

- long polling
- webhook adapters
- router / command dispatcher
- middleware pipeline
- test helpers
- mocking utilities
- интеграции с фреймворками языка

Правило:

> Генерируем то, что определяется API-контрактом. Пишем вручную то, что определяется особенностями языка и DX.

## 7. Модель пакетов

Для каждого языка рекомендуется 2 основных пакета.

### 7.1 Thin client

Назначение:

- прямой доступ к Bot API
- минимальная логика
- стабильная и предсказуемая поверхность API

Примеры:

- `@max/client`
- `Max.BotApi`
- `max-bot-client`

### 7.2 High-level SDK

Назначение:

- разработка ботов и интеграций с хорошим DX
- polling
- webhook
- handlers
- middleware

Примеры:

- `@max/bot-sdk`
- `Max.BotSdk`
- `max-bot-sdk`

## 8. Контракт совместимости

Для всех языков должны быть единые conformance checks:

- одинаковые fixtures запросов и ответов
- одинаковая обработка ошибок
- одинаковая сериализация ключевых структур
- одинаковое поведение pagination и retries там, где оно стандартизовано

Набор тестов:

- `contract tests`
- `golden fixtures`
- `compatibility tests`
- `e2e tests` против sandbox/mock server

## 9. CI/CD pipeline

При изменении API pipeline должен выполнять:

1. validate schema
2. построить API diff
3. проверить backward compatibility
4. сгенерировать клиенты по языкам
5. запустить contract tests
6. запустить language-specific tests
7. собрать документацию
8. опубликовать пакеты

Важно:

- генерация должна быть детерминированной
- generated diff должен быть читаемым
- каждый пакет публикуется независимо

## 10. Версионирование

Нельзя жестко связывать версию API и версии всех SDK-пакетов одной цифрой.

Нужно разделить:

- `API version`
- `Generator version`
- `SDK package version` для каждого языка

Принципы:

- breaking change в API требует major change на уровне API
- незначительные улучшения конкретного SDK не должны блокировать релизы других SDK
- generator может обновляться независимо, если не ломает публичный контракт

## 11. Точки расширения

Каждый SDK должен иметь стабильные extension points:

- custom HTTP client
- custom retry policy
- logger hook
- tracer hook
- middleware chain
- serializer options
- webhook verification hook
- file storage abstraction

Это нужно, чтобы SDK можно было встраивать в enterprise и high-load сценарии без форков.

## 12. Ограничения и принципы качества

Обязательные требования:

- generated code не редактируется вручную
- public API SDK должен быть idiomatic для языка
- документы и примеры генерируются или проверяются автоматически
- high-level слой не должен дублировать transport logic
- runtime слой не должен содержать bot-specific поведения

## 13. Рекомендуемый roadmap

### Этап 1

- нормализовать `OpenAPI`
- описать schema governance
- ввести API diff и compatibility checks

### Этап 2

- собрать единый codegen pipeline
- привести существующие SDK к модели `generated client + manual sdk`

### Этап 3

- выпустить официальный `Python`
- выпустить `C#`
- выпустить `PHP`

### Этап 4

- добавить `Kotlin`
- затем рассмотреть `Rust`

## 14. Приоритет языков

Новые официальные SDK целесообразно запускать в таком порядке:

1. `C#`
2. `PHP`
3. `Kotlin`
4. `Rust`

Основание:

- `C#` важен для enterprise и интеграционных команд
- `PHP` закрывает крупный пласт веб-интеграций и legacy backend
- `Kotlin` усиливает современный JVM-сегмент
- `Rust` полезен, но не является первым по охвату

## 15. Итоговая формулировка

Будущая платформа SDK для MAX должна строиться не как набор независимых вручную написанных библиотек, а как единая `spec-first` система:

- один API-контракт
- один генерационный pipeline
- общий набор compatibility tests
- отдельные idiomatic SDK по языкам

Это позволит одновременно:

- быстрее расширять список языков
- удерживать совместимость
- уменьшить стоимость поддержки
- не терять качество developer experience в каждом конкретном языке
