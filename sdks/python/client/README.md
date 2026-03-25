# Python Client

Generated thin client for MAX Bot API.

Текущий generated entrypoint:

- [client.py](C:\pro\max\sdks\python\client\src\max_client\generated\client.py)

Генерация:

```powershell
python tools/codegen/render_python_client.py --input tools/codegen/out/max-bot-api.ir.json --output sdks/python/client/src/max_client/generated/client.py
```

Проверка:

```powershell
python -m unittest tests.codegen.test_python_renderer
python -m compileall sdks/python/client/src
```
