# План добивки оставшихся raw-object схем

## 1. Остаток после этапа markup/buttons

После этапа `inline keyboard + markup` в контракте остались следующие raw-object места:

- `Chat.dialog_with_user`
- `Chat.pinned_message`
- `ShareAttachment.payload`
- `MessageConstructionRequestUpdate.input`

## 2. Что типизируем на этом этапе

### `Chat.dialog_with_user`

Переводим в явный тип:

- `UserWithPhoto`

Основание:

- в официальной документации `Chat` это поле описано как `object UserWithPhoto`

### `Chat.pinned_message`

Переводим в явный тип:

- `Message`

Основание:

- в официальной документации `Chat` это поле описано как `object Message`

### `ShareAttachment.payload`

Переводим в явный тип:

- `ShareAttachmentPayload`

Минимальная безопасная форма для этого этапа:

- `token: string | null`
- `url: string | null`

Основание:

- в официальной JS-документации MAX `ShareAttachment` создаётся через `url` и `token`

Важно:

- это инженерный вывод по публичной документации SDK, а не прямое описание отдельного object page

## 3. Что пока не типизируем

### `MessageConstructionRequestUpdate.input`

Пока оставляем `raw object`.

Причина:

- в публичной документации MAX на текущем этапе не найдено стабильного формального описания структуры `input`
- форсировать форму без надёжного контракта сейчас рискованнее, чем оставить `raw`

## 4. Ограничения этапа

На этом этапе не делаем:

- `oneOf` для construction input
- произвольные deep dynamic models без официального object-contract
- новый runtime или новый язык

## 5. Definition of Done

Этап считается завершённым, если:

- `Chat.dialog_with_user` больше не raw
- `Chat.pinned_message` больше не raw
- `ShareAttachment.payload` больше не raw
- `MessageConstructionRequestUpdate.input` остаётся явно задокументированным исключением
- `run_pipeline.py --verify` остаётся зелёным
