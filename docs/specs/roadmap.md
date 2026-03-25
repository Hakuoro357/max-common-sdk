# Спецификация roadmap для multi-language SDK платформы MAX

## 1. Цель

Определить поэтапный план развития SDK-платформы MAX, чтобы:

- перейти от разрозненных SDK к единой `spec-first` модели
- снизить стоимость поддержки языков
- ускорить выпуск новых SDK
- выровнять качество developer experience и release process

## 2. Общие принципы roadmap

Roadmap должен строиться вокруг следующих правил:

- сначала контракт, потом генерация
- сначала платформа, потом масштабирование по языкам
- сначала `thin client`, потом `high-level SDK`
- сначала качество и зрелость текущих языков, а не расширение матрицы

## 3. Целевое состояние

К концу roadmap платформа должна иметь:

- единый API contract
- единый codegen pipeline
- единый release model
- support matrix с ownership и статусами
- зрелый набор SDK для зафиксированного scope языков

## 3.1 Зафиксированный scope

Для текущего проекта принято ограничение:

- новые языки не запускаются
- roadmap ограничен языками:
  - `TypeScript`
  - `Python`
  - `C#`

Все следующие этапы roadmap должны интерпретироваться только внутри этого scope.

## 4. Этап 0. Audit и нормализация текущего состояния

### Цель

Понять текущее состояние SDK, репозиториев и API-описания.

### Результаты этапа

- список существующих SDK и пакетов
- карта feature coverage по языкам
- список расхождений между docs, code и реальным API
- список ручных участков, которые можно перевести на codegen
- список API-мест, где схема неполная или неоднозначная

### Артефакты

- audit report
- initial support matrix
- gap list по API schema

## 5. Этап 1. Contract foundation

### Цель

Сделать API-контракт единственным источником правды.

### Работы

- нормализовать `OpenAPI`
- формализовать schema governance
- описать naming rules
- описать error model
- описать pagination / upload / webhook contract
- ввести API diff и compatibility checks

### Definition of Done

- все основные методы описаны в канонической схеме
- схема валидируется автоматически
- breaking changes детектируются автоматически

## 6. Этап 2. Codegen platform foundation

### Цель

Построить генерационную платформу, способную производить stable low-level clients.

### Работы

- реализовать parser
- реализовать normalization layer
- реализовать `IR`
- реализовать template/render pipeline
- реализовать deterministic output rules
- добавить golden tests и compile checks

### Definition of Done

- генерация воспроизводима
- generated code проходит compile/tests
- добавление нового языка не требует менять parser или spec

## 7. Этап 3. Platform alignment существующих SDK

### Цель

Привести текущие SDK к общей архитектуре.

### Работы

- отделить generated client от manual SDK
- унифицировать runtime responsibilities
- убрать смешение generated/manual кода
- выровнять package naming
- выровнять release metadata и package status

### Языки первого выравнивания

- TypeScript
- Python
- C#

### Definition of Done

- у каждого языка есть явный `client` слой
- high-level слой не дублирует transport logic
- support matrix отражает реальное состояние

## 8. Этап 4. Углубление существующих SDK

### Цель

Повысить качество и зрелость текущих first-party SDK без расширения языковой матрицы.

### Работы

- выровнять `TypeScript`, `Python`, `C#` по API coverage
- улучшить schema fidelity
- усилить contract tests и release gates
- улучшить runtime behavior и error mapping
- определить owner и release policy для каждого из трех языков

### Definition of Done

- все три SDK имеют прозрачный статус в support matrix
- публикация и генерация идут через единый pipeline
- документация отражает только зафиксированный scope языков

## 9. Этап 5. High-level SDK maturity

### Цель

Перейти от thin client платформы к более зрелому DX поверх существующих языков.

### Подход

Для текущих языков постепенно добавляются:

- high-level `bot-sdk`
- webhook adapters
- testing utilities
- examples и framework integrations

### Definition of Done

- для существующих языков появляется слой выше thin client
- DX улучшается без расширения support matrix

## 10. Этап 6. Ecosystem maturity

### Цель

Перейти от набора SDK к зрелой платформе.

### Работы

- support matrix automation
- docs generation из metadata
- migration guides
- deprecation workflow
- framework adapters
- examples gallery
- sandbox/e2e infrastructure

### Definition of Done

- status SDK прозрачен
- release notes стандартизованы
- docs и packages синхронизированы автоматически

## 11. Приоритеты по времени

### Short term

- audit
- contract normalization
- codegen foundation

### Medium term

- alignment существующих SDK
- schema fidelity
- runtime maturity
- high-level DX для существующих языков

### Long term

- ecosystem maturity automation

## 12. Зависимости между этапами

Критические зависимости:

- без нормального API contract нельзя строить качественный codegen
- без codegen platform дорого поддерживать даже зафиксированный набор языков
- без support matrix невозможно прозрачно управлять статусами
- без release model нельзя стабильно публиковать multi-language SDK

## 13. Риски

Основные риски:

- неполный или неканоничный API spec
- попытка сразу писать high-level SDK без thin client foundation
- смешение generated и manual кода
- отсутствие owner у текущих языков
- отсутствие явного deprecation process

## 14. Метрики успеха

Roadmap можно считать успешным, если:

- качество существующих SDK заметно выросло
- доля generated low-level кода выросла
- число расхождений между docs и SDK снизилось
- релизы по трем языкам стали независимыми и предсказуемыми
- support matrix отражает реальность без ручной сверки по репозиториям

## 15. Связанные спецификации

Этот roadmap опирается на следующие документы:

- [sdk-architecture-spec.md](C:\pro\max\docs\specs\sdk-architecture-spec.md)
- [release-model.md](C:\pro\max\docs\specs\release-model.md)
- [codegen-architecture.md](C:\pro\max\docs\specs\codegen-architecture.md)
- [support-matrix.md](C:\pro\max\docs\specs\support-matrix.md)

## 16. Итог

Roadmap для MAX SDK должен идти от платформенного основания к зрелости зафиксированного набора SDK.

Ключевой принцип:

> Сначала единая инженерная система SDK, потом углубление качества существующих языков.
