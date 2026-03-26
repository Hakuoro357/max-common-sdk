# План повышения точности схем markup и buttons

## 1. Цель этапа

Убрать грубые `object` и `Dictionary<string, object?>` из моделей, связанных с:

- `InlineKeyboardAttachmentRequestPayload.buttons`
- `InlineKeyboardAttachmentPayload.buttons`
- `MarkupElement`

И заменить их на явные схемы, которые уже поддерживаются текущим `IR` и текущими renderer'ами.

## 2. Что меняем

### Inline keyboard

Добавляем явные схемы для структуры кнопок:

- `InlineKeyboardButton`
- `InlineKeyboardButtonAction`
- `InlineKeyboardRow`
- `InlineKeyboard`

После этого поля `buttons` в request/response payload больше не должны быть `type: object`.

Целевая форма:

- `InlineKeyboard` = массив строк клавиатуры
- `InlineKeyboardRow` = массив кнопок
- `InlineKeyboardButton` = объект кнопки
- `InlineKeyboardButtonAction` = объект действия кнопки

## 3. Что уточняем в Markup

`MarkupElement` сейчас плоский и слишком общий.

На этом этапе:

- оставляем его как один объект
- но делаем тип поля `type` перечислением
- фиксируем известные optional-поля отдельно

Без `oneOf` по variant'ам markup, чтобы не перегружать этап.

## 4. Ограничения этапа

На этом этапе не делаем:

- `oneOf` для `MarkupElement`
- произвольные callback payload models
- сложную типизацию произвольных dynamic map-объектов вне keyboard

## 5. Правило совместимости

Изменения должны:

- не ломать `run_pipeline.py --verify`
- не требовать нового языка или нового runtime
- оставаться совместимыми с текущим `IR`

## 6. Definition of Done

Этап завершён, если:

- в `OpenAPI` у `buttons` больше нет голого `object`
- generated `TypeScript`, `Python`, `C#` получают явные модели keyboard
- `MarkupElement.type` становится enum
- пайплайн и тесты остаются зелёными
