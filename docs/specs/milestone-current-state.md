# Текущий milestone SDK-платформы MAX

## 1. Что уже собрано

На текущем этапе в репозитории уже зафиксированы:

- канонический `OpenAPI` контракт
- нормализатор `OpenAPI -> IR`
- генерация SDK из `IR`
- generated clients для:
  - `TypeScript`
  - `Python`
  - `C#`
- единый pipeline:
  - `python tools/codegen/run_pipeline.py --verify`
- CI-проверка generated артефактов

## 2. Что уже типизировано

В контракте и генерации уже покрыты:

- основные bot/chat/message/update операции
- `AttachmentRequest` как union
- `Attachment` как union
- `Update` как union
- `InlineKeyboard`
- `MarkupElementType`
- `Chat.dialog_with_user`
- `Chat.pinned_message`
- `ShareAttachment.payload`

## 3. Что считается осознанным исключением

Сейчас в проекте есть один главный сознательно нетипизированный участок:

- `MessageConstructionRequestUpdate.input`

Причина:

- официальные источники MAX пока не фиксируют его стабильную форму
- официальный TypeScript SDK сам оставляет это поле как `unknown`

Отдельная фиксация исследования:

- [message-construction-input-research.md](C:\pro\max\docs\specs\message-construction-input-research.md)

## 4. Что считается текущей стабильной точкой

Текущая стабильная точка проекта определяется так:

- новые языки не добавляются
- основная матрица языков заморожена на:
  - `TypeScript`
  - `Python`
  - `C#`
- генератор и контракт развиваются в сторону качества, а не расширения языковой матрицы

## 5. Что дальше не обязательно, но возможно

После этого milestone можно идти в один из трёх сценариев:

- точечная polish-доработка существующих SDK
- formal cleanup и release baseline
- новый этап generator ergonomics без расширения product scope

## 6. Решение milestone

Этот milestone считается завершённым, если:

- specs зафиксированы
- generated SDK синхронизированы с контрактом
- `run_pipeline.py --verify` зелёный
- все оставшиеся неточности либо устранены, либо формально записаны как исключения
