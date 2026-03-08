## 2025-05-15 - [Path Traversal and SSRF Protection]
**Vulnerability:** Found multiple path traversal points in asset-serving endpoints and SSRF risk in the Ollama endpoint.
**Learning:** FastAPI's `FileResponse` and manual path construction using user-supplied filenames can easily lead to path traversal if not sanitized with `Path(filename).name`. Synchronous DNS resolution in SSRF checks can block the event loop in high-concurrency environments.
**Prevention:** Always use `Path(filename).name` to strip directory components from user-supplied filenames. Implement SSRF protection using the `ipaddress` module and ensure DNS resolution is non-blocking by using `asyncio.to_thread`.
