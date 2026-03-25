# Codegen Tools

Здесь живет минимальный bootstrap codegen-пайплайна.

Сейчас реализовано:

1. загрузка `OpenAPI`
2. normalization layer
3. сборка базового `IR`
4. валидация формы `IR`
5. сохранение `IR` в `JSON`
6. первый renderer для `TypeScript client stub`
7. второй renderer для `Python client stub`
8. generator manifest по языкам и покрытию операций

## Быстрый старт

```powershell
python tools/codegen/bootstrap_ir.py --input api/openapi/max-bot-api.yaml --output tools/codegen/out/max-bot-api.ir.json
python tools/codegen/render_typescript_client.py --input tools/codegen/out/max-bot-api.ir.json --output sdks/typescript/client/generated/index.ts
python tools/codegen/render_python_client.py --input tools/codegen/out/max-bot-api.ir.json --output sdks/python/client/src/max_client/generated/client.py
python tools/codegen/build_generator_manifest.py --input tools/codegen/out/max-bot-api.ir.json --output tools/codegen/out/generator-manifest.json
```

## Что входит в текущий IR

- метаданные API
- сервисы
- список операций
- список схем
- агрегированная статистика

## Ключевые файлы

- [bootstrap_ir.py](C:\pro\max\tools\codegen\bootstrap_ir.py)
- [render_typescript_client.py](C:\pro\max\tools\codegen\render_typescript_client.py)
- [render_python_client.py](C:\pro\max\tools\codegen\render_python_client.py)
- [build_generator_manifest.py](C:\pro\max\tools\codegen\build_generator_manifest.py)
- [ir-schema.json](C:\pro\max\tools\codegen\ir-schema.json)
- [normalize.py](C:\pro\max\tools\codegen\lib\normalize.py)
- [ir_builder.py](C:\pro\max\tools\codegen\lib\ir_builder.py)
- [validate.py](C:\pro\max\tools\codegen\lib\validate.py)
- [typescript_client.py](C:\pro\max\tools\codegen\lib\renderers\typescript_client.py)
- [python_client.py](C:\pro\max\tools\codegen\lib\renderers\python_client.py)
- [manifest.py](C:\pro\max\tools\codegen\lib\manifest.py)

## Следующий шаг

После этого bootstrap-слоя можно добавлять:

- полноценный `IR`
- другие renderers
- language-specific package layout
- compile/lint checks для generated SDK
