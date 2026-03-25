# RFC Index для SDK-платформы MAX

## Назначение

Этот документ является входной точкой в набор RFC по будущей multi-language SDK-платформе MAX.

Цель пакета:

- зафиксировать целевую архитектуру
- определить правила управления API
- описать codegen-платформу
- определить модель релизов
- зафиксировать поддержку языков
- задать поэтапный roadmap

## Состав RFC Pack

### 1. Базовая архитектура

- [sdk-architecture-spec.md](C:\pro\max\docs\specs\sdk-architecture-spec.md)

Что описывает:

- общую `spec-first` архитектуру
- разделение на `api`, `generators`, `runtimes`, `sdks`, `tests`
- границу между общим контрактом и языко-зависимыми реализациями

### 2. API Governance

- [api-governance.md](C:\pro\max\docs\specs\api-governance.md)

Что описывает:

- правила изменения API-контракта
- backward compatibility
- deprecation process
- ownership и review model

### 3. Code Generation

- [codegen-architecture.md](C:\pro\max\docs\specs\codegen-architecture.md)

Что описывает:

- pipeline `spec -> normalize -> IR -> render -> verify`
- архитектуру генератора
- требования к детерминизму
- правила разделения generated и manual кода

### 4. Release Model

- [release-model.md](C:\pro\max\docs\specs\release-model.md)

Что описывает:

- versioning model
- release gates
- compatibility rules
- публикацию SDK-пакетов по языкам

### 5. Support Matrix

- [support-matrix.md](C:\pro\max\docs\specs\support-matrix.md)

Что описывает:

- список языков
- статусы зрелости
- приоритеты развития
- ownership и coverage model

### 6. Roadmap

- [roadmap.md](C:\pro\max\docs\specs\roadmap.md)

Что описывает:

- поэтапный план развития платформы
- порядок внедрения codegen и governance
- приоритет запуска новых языков

## Рекомендуемый порядок чтения

1. [sdk-architecture-spec.md](C:\pro\max\docs\specs\sdk-architecture-spec.md)
2. [api-governance.md](C:\pro\max\docs\specs\api-governance.md)
3. [codegen-architecture.md](C:\pro\max\docs\specs\codegen-architecture.md)
4. [release-model.md](C:\pro\max\docs\specs\release-model.md)
5. [support-matrix.md](C:\pro\max\docs\specs\support-matrix.md)
6. [roadmap.md](C:\pro\max\docs\specs\roadmap.md)

## Как использовать пакет

Для стратегического обсуждения:

- начинать с `sdk-architecture-spec.md`
- затем переходить к `roadmap.md`

Для платформенной реализации:

- начинать с `api-governance.md`
- затем `codegen-architecture.md`
- затем `release-model.md`

Для управления экосистемой:

- использовать `support-matrix.md`
- сверять её с `roadmap.md`

## Итог

`rfc-index.md` связывает все текущие спецификации в единый пакет проектных решений по SDK-платформе MAX.
