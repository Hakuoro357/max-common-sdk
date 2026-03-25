using System.Collections;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Max.Client.Runtime;

public abstract class BaseApiClient
{
    private readonly string _baseUrl;
    private readonly string? _accessToken;
    private readonly string _authorizationScheme;
    private readonly HttpClient _httpClient;
    private readonly Dictionary<string, string> _defaultHeaders;
    private readonly JsonSerializerOptions _jsonOptions;

    protected BaseApiClient(ClientConfig? config = null)
    {
        config ??= new ClientConfig();
        _baseUrl = config.BaseUrl;
        _accessToken = config.AccessToken;
        _authorizationScheme = config.AuthorizationScheme;
        _httpClient = config.HttpClient ?? new HttpClient();
        _defaultHeaders = config.DefaultHeaders ?? new Dictionary<string, string>();
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = null,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        };
        _jsonOptions.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.CamelCase));
    }

    protected async Task<T?> SendAsync<T>(ApiRequest request, CancellationToken cancellationToken = default)
    {
        var uri = BuildUri(request.Path, request.Query);
        using var httpRequest = new HttpRequestMessage(request.Method, uri);

        foreach (var pair in _defaultHeaders)
        {
            httpRequest.Headers.TryAddWithoutValidation(pair.Key, pair.Value);
        }

        if (!string.IsNullOrWhiteSpace(_accessToken))
        {
            httpRequest.Headers.TryAddWithoutValidation("Authorization", $"{_authorizationScheme} {_accessToken}");
        }

        if (request.Options?.Headers is not null)
        {
            foreach (var pair in request.Options.Headers)
            {
                httpRequest.Headers.TryAddWithoutValidation(pair.Key, pair.Value);
            }
        }

        if (request.Body is not null)
        {
            var json = JsonSerializer.Serialize(request.Body, _jsonOptions);
            httpRequest.Content = new StringContent(json, Encoding.UTF8, "application/json");
        }

        using var response = await _httpClient.SendAsync(httpRequest, cancellationToken);
        var payload = await response.Content.ReadAsStringAsync(cancellationToken);

        if (!response.IsSuccessStatusCode)
        {
            throw new MaxApiException(request.Method.Method, request.Path, (int)response.StatusCode, payload);
        }

        if (string.IsNullOrWhiteSpace(payload))
        {
            return default;
        }

        return JsonSerializer.Deserialize<T>(payload, _jsonOptions);
    }

    private Uri BuildUri(string path, Dictionary<string, object?>? query)
    {
        var builder = new StringBuilder();
        builder.Append(_baseUrl.TrimEnd('/'));
        builder.Append(path);

        var queryString = BuildQueryString(query);
        if (!string.IsNullOrEmpty(queryString))
        {
            builder.Append('?');
            builder.Append(queryString);
        }

        return new Uri(builder.ToString(), UriKind.Absolute);
    }

    private static string BuildQueryString(Dictionary<string, object?>? query)
    {
        if (query is null || query.Count == 0)
        {
            return string.Empty;
        }

        var parts = new List<string>();
        foreach (var pair in query)
        {
            if (pair.Value is null)
            {
                continue;
            }

            if (pair.Value is IEnumerable enumerable && pair.Value is not string)
            {
                foreach (var item in enumerable)
                {
                    if (item is not null)
                    {
                        parts.Add($"{Uri.EscapeDataString(pair.Key)}={Uri.EscapeDataString(SerializeQueryValue(item))}");
                    }
                }

                continue;
            }

            parts.Add($"{Uri.EscapeDataString(pair.Key)}={Uri.EscapeDataString(SerializeQueryValue(pair.Value))}");
        }

        return string.Join("&", parts);
    }

    private static string SerializeQueryValue(object value)
    {
        if (value is bool boolValue)
        {
            return boolValue ? "true" : "false";
        }

        if (value.GetType().IsEnum)
        {
            var raw = value.ToString() ?? string.Empty;
            return string.IsNullOrEmpty(raw) ? raw : char.ToLowerInvariant(raw[0]) + raw[1..];
        }

        return value.ToString() ?? string.Empty;
    }
}
