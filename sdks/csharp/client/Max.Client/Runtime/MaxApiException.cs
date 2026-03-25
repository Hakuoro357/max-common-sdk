using System.Text.Json.Serialization;

namespace Max.Client.Runtime;

public sealed class MaxErrorPayload
{
    [JsonPropertyName("code")]
    public string? Code { get; init; }

    [JsonPropertyName("message")]
    public string? Message { get; init; }

    [JsonPropertyName("details")]
    public string? Details { get; init; }
}

public sealed class MaxApiException : Exception
{
    public string Method { get; }
    public string Path { get; }
    public int StatusCode { get; }
    public string BodyText { get; }
    public string? ErrorCode { get; }
    public string? ApiMessage { get; }
    public string? ErrorDetails { get; }
    public MaxErrorPayload? Payload { get; }

    public MaxApiException(string method, string path, int statusCode, string bodyText, MaxErrorPayload? payload = null)
        : base(payload?.Message ?? $"{method} {path} failed with status {statusCode}")
    {
        Method = method;
        Path = path;
        StatusCode = statusCode;
        BodyText = bodyText;
        Payload = payload;
        ErrorCode = payload?.Code;
        ApiMessage = payload?.Message;
        ErrorDetails = payload?.Details;
    }
}
