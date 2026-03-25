using System.Net.Http;

namespace Max.Client.Runtime;

public sealed class ClientConfig
{
    public string BaseUrl { get; init; } = "https://api.max.ru";
    public string? AccessToken { get; init; }
    public string AuthorizationScheme { get; init; } = "Bearer";
    public HttpClient? HttpClient { get; init; }
    public Dictionary<string, string>? DefaultHeaders { get; init; }
}
