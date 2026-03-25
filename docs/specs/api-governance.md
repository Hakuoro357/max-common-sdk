# Спецификация API governance для SDK-платформы MAX

## 1. Цель

Определить правила управления API-контрактом MAX, чтобы:

- API оставался единым источником правды для всех SDK
- изменения проходили предсказуемо и контролируемо
- breaking changes не появлялись случайно
- команда могла масштабировать SDK по языкам без расхождения контрактов

## 2. Основной принцип

API governance должен строиться вокруг правила:

> Любое изменение API сначала оформляется как изменение контракта, и только потом попадает в SDK, документацию и релизы.

Это означает:

- контракт первичен
- реализация вторична
- документация и SDK не могут быть авторитетнее схемы

## 3. Область действия

Governance распространяется на:

- endpoints
- request/response schema
- auth model
- webhook/update payload
- pagination
- error model
- rate limiting contract
- file upload/download contract
- versioning policy

## 4. Канонический источник правды

Каноническим источником правды является набор спецификаций:

- `OpenAPI`
- связанные `JSON Schema`, если они нужны для расширения модели

Любые derived artifacts:

- SDK
- docs
- примеры
- fixtures
- mocks

должны строиться из этого канонического источника.

## 5. Изменения API

Каждое изменение должно классифицироваться до начала реализации.

Категории:

- `additive`
- `behavioral`
- `deprecated`
- `breaking`

### `additive`

Примеры:

- новый endpoint
- новое необязательное поле
- новое enum-значение там, где это допустимо политикой клиента

### `behavioral`

Примеры:

- изменение семантики ошибки
- изменение retry expectations
- изменение rate-limit поведения

### `deprecated`

Примеры:

- поле или endpoint помечается как устаревший
- добавляется replacement path

### `breaking`

Примеры:

- удаление endpoint
- изменение типа поля
- перевод optional поля в required
- удаление enum значения
- смена несовместимого поведения ответа

## 6. Обязательный change flow

Любое изменение контракта должно проходить такой путь:

1. сформулировать change request
2. описать use case и impact
3. классифицировать изменение
4. обновить API spec
5. прогнать schema validation
6. построить API diff
7. оценить backward compatibility
8. обновить generated artifacts
9. обновить docs и examples
10. только после этого выпускать SDK changes

## 7. Правила backward compatibility

По умолчанию контракт должен сохранять backward compatibility.

Нельзя без major-перехода:

- удалять поля
- менять типы полей
- менять required/optional semantics в сторону ужесточения
- менять структуру error payload
- менять структуру webhook payload несовместимым образом

Допустимо:

- добавлять новые необязательные поля
- добавлять новые endpoints
- добавлять новые non-breaking response sections

## 8. Deprecation policy

Перед удалением публичного элемента должен быть этап deprecation.

Каждая деприкация должна содержать:

- отметку `deprecated`
- причину
- replacement path
- дату или версию планового удаления
- migration note

Удаление без deprecation допустимо только для security-critical случаев.

## 9. Ownership

У API governance должен быть явный владелец.

Минимальная модель:

- `API owner`
- `SDK platform owner`
- `language owners`

Решения по контракту принимает не отдельный SDK maintainer, а API owner или утвержденный governance group.

## 10. Review requirements

Изменение API не может приниматься без review.

Минимальные проверки:

- product correctness
- protocol correctness
- backward compatibility
- impact on codegen
- impact on existing SDKs
- impact on docs/examples

Если изменение нельзя уверенно классифицировать, оно не должно попадать в основной контракт без дополнительного review.

## 11. Требования к схеме

Схема API должна быть:

- полной
- валидной
- однозначной
- пригодной для code generation
- пригодной для diff analysis

Нельзя оставлять в канонической схеме:

- неописанные типы
- неоднозначные nullable semantics
- "магические" поля без описания
- нестабильные naming patterns

## 12. Naming rules

Governance должен включать правила именования:

- endpoint naming
- field naming
- enum naming
- error code naming
- event type naming

Имена должны быть стабильными и машинно-обрабатываемыми.

Нельзя допускать, чтобы разные части API называли одну и ту же сущность по-разному.

## 13. Error governance

Ошибки должны быть частью контракта, а не побочным эффектом реализации.

Нужно фиксировать:

- error code
- HTTP status или transport mapping
- message contract, если он стабилен
- retryability
- client action expectations

Это особенно важно для multi-language SDK, потому что error handling должен быть консистентным.

## 14. Webhook и event governance

Webhook/update события должны иметь такой же уровень управления, как и request/response API.

Нужно фиксировать:

- event type
- payload schema
- optional/required fields
- sequencing expectations
- compatibility rules при добавлении новых полей

## 15. Schema lifecycle

Для схемы нужен жизненный цикл:

- draft
- approved
- released
- deprecated
- removed

Только `approved` и `released` могут использоваться как источник генерации для production SDK.

## 16. Automation и проверки

Governance должен быть подкреплен автоматикой:

- schema validation
- API diff generation
- breaking change detection
- docs sync check
- generated artifacts sync check
- contract test execution

Если правило нельзя проверить автоматически, его нужно по возможности формализовать до автоматизируемого вида.

## 17. Связь с релизной моделью

API governance управляет тем, что можно менять.

Release model управляет тем, как изменения публикуются.

Support matrix управляет тем, где изменения уже доступны.

Roadmap управляет тем, в каком порядке развивается экосистема.

## 18. Артефакты governance

Минимальный набор артефактов:

- canonical API spec
- API change log
- deprecation registry
- compatibility rules
- naming conventions
- ownership registry

## 19. Definition of Done для изменения API

Изменение API считается завершенным только если:

- обновлен контракт
- change классифицирован
- compatibility проверена
- docs обновлены
- generated artifacts обновлены
- impact на SDK понятен
- support matrix при необходимости скорректирована

## 20. Итог

API governance для MAX должен быть не набором договоренностей "на словах", а формализованной системой правил и проверок.

Ключевой принцип:

> Нельзя менять API напрямую через реализацию; API сначала проходит governance, потом становится основой для SDK и релизов.
