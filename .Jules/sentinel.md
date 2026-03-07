## 2025-05-15 - [SSRF and Path Traversal Mitigations]
**Vulnerability:** The application was vulnerable to Path Traversal in file serving endpoints and SSRF via configurable AI endpoints (Ollama) and image download URLs.
**Learning:** Standard FastAPI/Starlette `FileResponse` and manual path joining `directory / filename` are unsafe if `filename` is user-controlled. Also, allowing user-provided endpoints for services like Ollama requires strict URL validation to prevent internal network scanning.
**Prevention:** Always sanitize filenames using `Path(filename).name` before joining with directories. Implement an `is_safe_url` utility to block private IP ranges and non-http(s) schemes for any external requests or configurable service endpoints.
