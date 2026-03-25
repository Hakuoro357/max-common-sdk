using System.Net.Http;

namespace Max.Client.Runtime;

public sealed class ApiRequest
{
    public required HttpMethod Method { get; init; }
    public required string Path { get; init; }
    public Dictionary<string, object?>? Query { get; init; }
    public object? Body { get; init; }
    public RequestOptions? Options { get; init; }
}
