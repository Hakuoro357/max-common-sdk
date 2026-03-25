export interface MaxApiErrorInit {
  method: string;
  path: string;
  status: number;
  bodyText: string;
}

export class MaxApiError extends Error {
  readonly method: string;
  readonly path: string;
  readonly status: number;
  readonly bodyText: string;

  constructor(init: MaxApiErrorInit) {
    super(`${init.method} ${init.path} failed with status ${init.status}`);
    this.name = "MaxApiError";
    this.method = init.method;
    this.path = init.path;
    this.status = init.status;
    this.bodyText = init.bodyText;
  }
}
