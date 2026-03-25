namespace Max.Client.Runtime;

public sealed class MaxApiException : Exception
{
    public string Method { get; }
    public string Path { get; }
    public int StatusCode { get; }
    public string BodyText { get; }

    public MaxApiException(string method, string path, int statusCode, string bodyText)
        : base($"{method} {path} failed with status {statusCode}")
    {
        Method = method;
        Path = path;
        StatusCode = statusCode;
        BodyText = bodyText;
    }
}
