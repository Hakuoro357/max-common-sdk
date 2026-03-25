# Codegen Tools

Здесь живет минимальный bootstrap codegen-пайплайна.

Сейчас реализовано:

1. загрузка `OpenAPI`
2. normalization layer
3. сборка базового `IR`
4. валидация формы `IR`
5. сохранение `IR` в `JSON`

## Быстрый старт

```powershell
python tools/codegen/bootstrap_ir.py --input api/openapi/max-bot-api.yaml --output tools/codegen/out/max-bot-api.ir.json
```

## Что входит в текущий IR

- метаданные API
- сервисы
- список операций
- список схем
- агрегированная статистика

## Ключевые файлы

- [bootstrap_ir.py](C:\pro\max\tools\codegen\bootstrap_ir.py)
- [ir-schema.json](C:\pro\max\tools\codegen\ir-schema.json)
- [normalize.py](C:\pro\max\tools\codegen\lib\normalize.py)
- [ir_builder.py](C:\pro\max\tools\codegen\lib\ir_builder.py)
- [validate.py](C:\pro\max\tools\codegen\lib\validate.py)

## Следующий шаг

После этого bootstrap-слоя можно добавлять:

- normalization layer
- полноценный `IR`
- render templates
- language emitters
