import { MaxApiError, parseMaxErrorPayload } from "./api-error.js";

export interface ClientConfig {
  baseUrl?: string;
  accessToken?: string;
  authorizationScheme?: string;
  fetch?: typeof fetch;
  defaultHeaders?: Record<string, string>;
}

export interface RequestOptions {
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

export interface ApiRequest {
  method: string;
  path: string;
  query?: Record<string, unknown>;
  body?: unknown;
  options?: RequestOptions;
}

export class BaseApiClient {
  protected readonly baseUrl: string;

  private readonly accessToken?: string;
  private readonly authorizationScheme: string;
  private readonly fetchImpl: typeof fetch;
  private readonly defaultHeaders: Record<string, string>;

  constructor(config: ClientConfig = {}) {
    this.baseUrl = config.baseUrl ?? "https://api.max.ru";
    this.accessToken = config.accessToken;
    this.authorizationScheme = config.authorizationScheme ?? "Bearer";
    this.fetchImpl = config.fetch ?? fetch;
    this.defaultHeaders = config.defaultHeaders ?? {};
  }

  protected async request<T>(request: ApiRequest): Promise<T> {
    const url = new URL(request.path, this.baseUrl);
    appendQueryParams(url, request.query);

    const headers = new Headers(this.defaultHeaders);
    if (this.accessToken) {
      headers.set("Authorization", `${this.authorizationScheme} ${this.accessToken}`);
    }

    for (const [key, value] of Object.entries(request.options?.headers ?? {})) {
      headers.set(key, value);
    }

    let body: string | undefined;
    if (request.body !== undefined) {
      if (!headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
      }

      body = JSON.stringify(request.body);
    }

    const response = await this.fetchImpl(url, {
      method: request.method,
      headers,
      signal: request.options?.signal,
      body,
    });

    if (!response.ok) {
      const bodyText = await response.text();
      const payload = parseMaxErrorPayload(bodyText);
      throw new MaxApiError({
        method: request.method,
        path: request.path,
        status: response.status,
        bodyText,
        payload,
      });
    }

    if (response.status === 204) {
      return undefined as T;
    }

    const text = await response.text();
    if (!text) {
      return undefined as T;
    }

    return JSON.parse(text) as T;
  }
}

function appendQueryParams(url: URL, query: Record<string, unknown> | undefined): void {
  if (!query) {
    return;
  }

  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) {
      continue;
    }

    if (Array.isArray(value)) {
      for (const item of value) {
        url.searchParams.append(key, serializeQueryValue(item));
      }
      continue;
    }

    url.searchParams.set(key, serializeQueryValue(value));
  }
}

function serializeQueryValue(value: unknown): string {
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  return String(value);
}
