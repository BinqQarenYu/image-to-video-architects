## 2025-05-15 - [Path Traversal and SSRF Mitigation in FastAPI Backend]
**Vulnerability:** Path traversal in asset-serving endpoints and SSRF risk in image generation from remote URLs.
**Learning:** Using `Path(filename).name` is a robust way to sanitize user-provided filenames. SSRF protection via DNS resolution and IP range validation is effective but needs to be careful with TOCTOU (Time-of-Check to Time-of-Use). FFmpeg concat demuxer requires specific escaping for single quotes and backslashes in its list files.
**Prevention:** Always sanitize filenames before joining with local paths. Validate external URLs before fetching. Use `asyncio.to_thread` for blocking IO/DNS tasks in async environments.
