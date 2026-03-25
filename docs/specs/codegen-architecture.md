# Спецификация архитектуры code generation для multi-language SDK MAX

## 1. Цель

Определить архитектуру codegen-платформы, которая:

- генерирует low-level SDK из одного API-контракта
- минимизирует ручную работу при добавлении нового языка
- дает предсказуемый и стабильный generated code
- не мешает создавать idiomatic high-level SDK вручную

## 2. Принцип

Codegen-платформа должна строиться вокруг одного канонического входа:

- `OpenAPI` для методов и transport contract
- `JSON Schema` для моделей и событий, если нужно расширение поверх OpenAPI

Выходом являются:

- language-specific models
- API clients
- базовые errors
- docs snippets
- fixtures и часть test scaffolding

## 3. Архитектурная схема

```text
API Spec
  -> normalization
  -> intermediate representation (IR)
  -> language template renderer
  -> generated source code
  -> package assembly
```

Главная идея: не рендерить шаблоны напрямую из сырого `OpenAPI`, а сначала приводить его к внутреннему `IR`.

## 4. Этапы pipeline

### 4.1 Parse

Вход:

- `openapi.yaml`
- дополнительные schema files

На этом этапе:

- валидируется схема
- разрешаются `$ref`
- проверяется полнота описания

### 4.2 Normalize

На этом этапе:

- унифицируются имена
- нормализуются enums
- выделяются common error shapes
- нормализуются nullable / optional semantics
- стабилизируется порядок полей и методов

Цель — избавиться от неоднозначностей входной схемы.

### 4.3 IR build

Нужен внутренний `Intermediate Representation`, содержащий:

- services / endpoints
- operations
- request models
- response models
- enums
- errors
- pagination contract
- file upload/download contract
- webhook/update models

`IR` должен быть независим от конкретного языка.

### 4.4 Render

Для каждого языка подключается отдельный renderer/template set.

Он отвечает за:

- naming rules
- import organization
- package/module structure
- async model mapping
- error hierarchy mapping
- doc comment style

### 4.5 Post-process

После рендера:

- форматирование
- lint/compile check
- deterministic file ordering
- package metadata generation

## 5. Что должно генерироваться

### Обязательно

- DTO/models
- enums
- API methods
- request/response types
- error types базового уровня
- serialization glue

### Допустимо генерировать частично

- docs examples
- test fixtures wrappers
- simple request builders

### Не рекомендуется генерировать

- bot router
- middleware framework
- long polling orchestration
- webhook framework adapters
- developer ergonomics layer

Эти части должны жить в manual SDK.

## 6. Структура генератора

Рекомендуемая структура:

```text
generators/
  core/
    parser/
    normalizer/
    ir/
    diff/
    validations/

  templates/
    typescript/
    go/
    java/
    python/
    csharp/
    php/
    kotlin/

  emitters/
    docs/
    fixtures/
    metadata/
```

## 7. Требования к IR

`IR` должен быть:

- стабильным
- сериализуемым
- пригодным для snapshot diff
- удобным для тестирования

Если `IR` нестабилен, generated diff станет шумным и релизы будут плохо ревьюиться.

## 8. Требования к шаблонам

Шаблоны должны быть:

- тонкими
- предсказуемыми
- без сложной бизнес-логики

Сложная логика должна жить в `normalizer` и `IR builder`, а не в шаблонах.

Правило:

> Чем умнее шаблон, тем труднее поддержка нового языка.

## 9. Детерминизм

Codegen обязан быть детерминированным.

Повторный запуск без изменений входа должен давать тот же результат побайтно или максимально близко к этому.

Для этого нужны:

- стабильная сортировка
- единые naming rules
- фиксированный порядок imports
- фиксированный порядок полей
- контролируемое форматирование

## 10. Strategy для новых языков

Добавление нового языка должно требовать:

1. runtime layer
2. template set
3. package metadata emitter
4. language-specific tests

Не должно требоваться:

- переписывать parser
- менять spec
- дублировать business rules генерации

## 11. Тестирование генератора

Нужны 4 типа тестов:

### 11.1 Parser tests

Проверяют корректный разбор входной схемы.

### 11.2 IR snapshot tests

Проверяют стабильность внутреннего представления.

### 11.3 Golden generation tests

Сравнивают generated output с эталоном.

### 11.4 Compile tests

Проверяют, что generated code действительно собирается в целевом языке.

## 12. API diff и влияние на codegen

При изменении схемы pipeline должен строить diff:

- added endpoints
- removed endpoints
- field type changes
- required/optional changes
- enum changes

Этот diff нужен не только для API review, но и для понимания, какой generated code обязан измениться.

## 13. Граница между generated и manual кодом

Generated код должен попадать только в:

- `client`
- `models`
- `errors`
- `serialization`

Manual код должен жить отдельно и не редактироваться генератором.

Нельзя смешивать generated и manual код в одном и том же файле.

## 14. Расширяемость

Генератор должен предусматривать:

- custom naming overrides
- operation grouping overrides
- language-specific reserved words handling
- optional feature flags
- doc generation hooks

Но эти расширения не должны ломать базовый deterministic flow.

## 15. Итог

Архитектура codegen для MAX должна быть устроена как конвейер:

- `spec -> normalize -> IR -> render -> verify -> publish`

Главная цель — сделать добавление нового языка дешевым, а generated SDK — стабильным, понятным и пригодным для автоматического релиза.
