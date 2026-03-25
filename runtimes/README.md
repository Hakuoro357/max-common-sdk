# Runtimes

В этой папке будут runtime-слои по языкам.

Runtime отвечает за:

- HTTP transport
- auth injection
- retries
- serialization hooks
- logging/tracing integration points

Runtime не должен содержать high-level bot logic.
