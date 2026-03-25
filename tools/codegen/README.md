# Codegen Tools

Здесь живет минимальный bootstrap codegen-пайплайна.

Сейчас реализовано:

1. загрузка `OpenAPI`
2. извлечение базового `IR`
3. сохранение `IR` в `JSON`

## Быстрый старт

```powershell
python tools/codegen/bootstrap_ir.py --input api/openapi/max-bot-api.yaml --output tools/codegen/out/max-bot-api.ir.json
```

## Что входит в текущий IR

- метаданные API
- список операций
- список схем
- агрегированная статистика

## Следующий шаг

После этого bootstrap-слоя можно добавлять:

- normalization layer
- полноценный `IR`
- render templates
- language emitters
