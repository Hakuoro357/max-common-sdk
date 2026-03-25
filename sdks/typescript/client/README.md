# TypeScript Client

Generated thin client for MAX Bot API.

Текущий generated entrypoint:

- [generated/index.ts](C:\pro\max\sdks\typescript\client\generated\index.ts)

Генерация:

```powershell
python tools/codegen/render_typescript_client.py --input tools/codegen/out/max-bot-api.ir.json --output sdks/typescript/client/generated/index.ts
```

Проверка типов:

```powershell
npm.cmd install
npm.cmd run check
```

Сборка:

```powershell
npm.cmd run build
```

Конфигурация клиента:

```ts
import { MaxBotApiClient } from "@max/client";

const client = new MaxBotApiClient({
  baseUrl: "https://api.max.ru",
  accessToken: process.env.MAX_BOT_TOKEN,
});
```
