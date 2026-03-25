# CSharp Client

Generated thin client for MAX Bot API.

Текущий generated entrypoint:

- [MaxBotApiClient.g.cs](C:\pro\max\sdks\csharp\client\Max.Client\Generated\MaxBotApiClient.g.cs)

Генерация:

```powershell
python tools/codegen/render_csharp_client.py --input tools/codegen/out/max-bot-api.ir.json --output sdks/csharp/client/Max.Client/Generated/MaxBotApiClient.g.cs
```

Сборка:

```powershell
dotnet build sdks/csharp/client/Max.Client/Max.Client.csproj
```
