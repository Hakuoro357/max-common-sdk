export interface MaxApiErrorInit {
  method: string;
  path: string;
  status: number;
  bodyText: string;
  payload?: MaxErrorPayload;
}

export interface MaxErrorPayload {
  code?: string;
  message?: string;
  details?: string | null;
}

export class MaxApiError extends Error {
  readonly method: string;
  readonly path: string;
  readonly status: number;
  readonly bodyText: string;
  readonly payload?: MaxErrorPayload;
  readonly errorCode?: string;
  readonly errorMessage?: string;
  readonly errorDetails?: string | null;

  constructor(init: MaxApiErrorInit) {
    super(init.payload?.message ?? `${init.method} ${init.path} failed with status ${init.status}`);
    this.name = "MaxApiError";
    this.method = init.method;
    this.path = init.path;
    this.status = init.status;
    this.bodyText = init.bodyText;
    this.payload = init.payload;
    this.errorCode = init.payload?.code;
    this.errorMessage = init.payload?.message;
    this.errorDetails = init.payload?.details;
  }
}

export function parseMaxErrorPayload(bodyText: string): MaxErrorPayload | undefined {
  if (!bodyText.trim()) {
    return undefined;
  }

  try {
    const parsed = JSON.parse(bodyText) as Record<string, unknown>;
    if (typeof parsed !== "object" || parsed === null) {
      return undefined;
    }

    const payload: MaxErrorPayload = {};
    if (typeof parsed.code === "string") {
      payload.code = parsed.code;
    }
    if (typeof parsed.message === "string") {
      payload.message = parsed.message;
    }
    if (typeof parsed.details === "string" || parsed.details === null) {
      payload.details = parsed.details as string | null;
    }

    return payload.code || payload.message || "details" in payload ? payload : undefined;
  } catch {
    return undefined;
  }
}
