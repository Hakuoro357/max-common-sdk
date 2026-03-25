# MAX Common SDK

Монорепозиторий для будущей multi-language SDK-платформы MAX.

## Что уже есть

- RFC-пакет в [docs/specs/rfc-index.md](C:\pro\max\docs\specs\rfc-index.md)
- базовый scaffold платформы
- точка входа для API-контракта
- machine-readable support matrix

## Структура

```text
api/          канонический API-контракт
docs/specs/   RFC и архитектурные спецификации
generators/   code generation platform
runtimes/     языковые runtime-слои
sdks/         generated client и manual SDK по языкам
tests/        contract, compatibility и e2e тесты
tools/        служебные инструменты платформы
```

## Следующие шаги

1. Заполнить `api/openapi/max-bot-api.yaml`
2. Описать `IR` для codegen
3. Собрать минимальный pipeline генерации
4. Завести первый runtime и первый generated client
