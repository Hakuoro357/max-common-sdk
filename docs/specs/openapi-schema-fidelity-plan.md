# План повышения точности схем OpenAPI для MAX SDK

## 1. Текущее состояние

По публичным операциям официальный `max-bot-api-client-ts` уже покрыт в каноническом `OpenAPI`.

Покрытые группы:

- `bots`
- `chats`
- `messages`
- `subscriptions`
- `uploads`

Следующий основной пробел — не операции, а точность моделей.

## 2. Цель этапа

Сделать контракт ближе к реальным типам MAX SDK без поломки текущего codegen pipeline.

Ключевой принцип:

> Сначала доводим схемы до максимально точного безопасного подмножества `OpenAPI`, которое уже умеет переваривать текущий генератор.

## 3. Что именно нужно улучшить

### `Chat`

Добавить или уточнить:

- `participants`
- `dialog_with_user`
- `pinned_message`

### `PhotoAttachmentRequestPayload`

Добавить:

- `photos`

### `AttachmentRequest`

Уточнить payload-поля под реальные request attachment types:

- `buttons`
- `contact_id`
- `vcf_info`
- `vcf_phone`
- `code`
- `photos`

### `Attachment`

Уточнить response attachment-поля:

- `thumbnail`
- `duration`
- `tam_info`

### `Message`

Проверить nullable/optional semantics для:

- `sender`
- `link`
- `stat`
- `constructor`

### `Update`

Добавить поля из реальных update payload:

- `user_locale`
- `inviter_id`
- `admin_id`
- `is_channel`
- `session_id`
- `start_payload`

## 4. Ограничения текущего этапа

На этом этапе не делаем:

- полноценный `oneOf`
- discriminated unions
- map/object schema с произвольными ключами
- глубокую типизацию `input: unknown`

Причина:

- текущий `IR` и renderer'ы это пока не поддерживают

## 5. Правило этапа

Если точная модель требует возможностей, которых нет в текущем generator stack, применяется fallback:

- либо упрощённый `object`
- либо безопасное flattening-представление
- либо перенос в следующий этап генератора

## 6. Definition of Done

Этап считается завершённым, если:

- `OpenAPI` обогащён безопасными реальными полями
- `IR` и generated SDK не ломаются
- `run_pipeline.py --verify` остаётся зелёным
- diff остаётся читаемым

## 7. Следующий этап после этого

После повышения точности схем можно идти в следующий инфраструктурный шаг:

- расширение `IR` под `oneOf`
- discriminated unions для attachments и updates
- более точный codegen для multi-language SDK
