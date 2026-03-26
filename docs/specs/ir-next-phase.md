# Спецификация следующего этапа развития IR для MAX SDK

## 1. Цель

Определить следующий этап развития `IR`, чтобы codegen-платформа смогла корректно представлять сложные схемы MAX API без деградации в `object` / `unknown`.

Ключевая задача:

> Научить `IR` выражать сложные типы, которые уже есть в контракте или понадобятся для точной модели `attachments`, `updates` и `markup`.

## 2. Почему это нужно

Сейчас текущий pipeline уже умеет:

- операции
- простые object schema
- arrays
- enums
- nullable
- `wire path` override

Но он всё ещё теряет точность там, где нужны:

- `oneOf`
- discriminated unions
- map/dictionary types
- более точные event/update variants

Из-за этого часть реальных моделей MAX SDK пока вынужденно сведена к:

- `object`
- `unknown`
- упрощённым flatten-представлениям

## 3. Scope этапа

На этом этапе нужно расширить только платформенный слой:

- `normalize`
- `IR`
- renderer contracts
- tests

На этом этапе не делаем:

- новые языки
- high-level SDK
- новую продуктовую функциональность поверх клиента

## 4. Что должен уметь новый IR

### 4.1 `oneOf`

Нужна поддержка union-моделей:

- attachment variants
- update variants
- button variants

Минимальные требования:

- хранить список вариантов
- хранить discriminator, если он есть
- сохранять порядок вариантов детерминированно

### 4.2 Discriminator

Нужна явная модель discriminator-поля:

- имя поля
- mapping variant -> schema
- fallback behavior, если mapping неполный

Это критично для:

- `AttachmentRequest`
- `Attachment`
- `Update`

### 4.3 Map types

Нужна поддержка словарей / объектов с произвольными ключами.

Примеры:

- `participants`
- `photos`

Минимальная модель:

- `key_type`
- `value_type`
- nullable semantics

### 4.4 Unknown / raw payload

Нужен явный тип для raw-полей, а не неявное сваливание в `object`.

Примеры:

- `input: unknown`
- payload-поля, которые пока не разложены по точной схеме

## 5. Изменения в normalize layer

Normalize layer должен начать выделять:

- `node_kind`
- `one_of`
- `discriminator`
- `additional_properties`
- `raw_object`

Правило:

> Нормализация должна делать сложность входной схемы явной, а не скрывать её в обобщённый `type: object`.

## 6. Изменения в IR schema

В `IR` должны появиться новые конструкции:

- `kind: scalar | object | array | enum | ref | union | map | raw`
- `variants` для union
- `discriminator`
- `map_value`
- `nullable`

При этом `IR` должен остаться:

- сериализуемым
- стабильным
- удобным для snapshot diff

## 7. Требования к renderer layer

Renderer'ы для `TypeScript`, `Python`, `C#` должны получить единые правила:

- как рендерить `union`
- как рендерить `map`
- как рендерить discriminator-aware модели
- как делать fallback, если язык не поддерживает точную форму без шума

Правило:

> Renderer не должен угадывать структуру сложного типа; всё необходимое должно уже быть выражено в `IR`.

## 8. Минимальный целевой эффект

После этого этапа платформа должна уметь выразить без грубых заглушек:

- attachment variants
- request attachment variants
- update variants
- map-поля вроде `photos`
- map-поля вроде `participants`

## 9. Не-цели этапа

В этот этап не входят:

- runtime polymorphic deserialization во всех языках до production-grade уровня
- high-level bot abstractions
- feature-rich manual SDK layer

Сначала нужно сделать выразительный `IR`, и только потом доводить language-specific ergonomics.

## 10. Definition of Done

Этап считается завершённым, если:

- `IR` умеет `union`, `map` и discriminator
- normalizer сохраняет эту информацию детерминированно
- renderer tests покрывают новые конструкции
- `run_pipeline.py --verify` остаётся зелёным
- можно убрать часть текущих `unknown` / `object` fallback из схем attachments и updates

## 11. Следующий шаг после этого

После завершения этого этапа можно делать уже прикладной слой:

- точные attachment models
- точные update models
- более строгий generated DX в `TypeScript`, `Python`, `C#`
