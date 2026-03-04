## 2025-05-14 - [Flat-File Path Sanitization Pattern]
**Vulnerability:** Path Traversal via user-controlled filenames in API endpoints serving or processing local files.
**Learning:** In applications using a flat file structure for uploads and generated assets, the `Path(filename).name` property provides an elegant and robust defense by stripping all directory navigation segments (e.g., `../`, `/etc/`) before path joining. This is more resilient than manual string replacement.
**Prevention:** Use the `safe_join` utility for all file system operations involving user-provided strings. Always validate that the resulting sanitized name is not empty or equal to current/parent directory markers.

## 2025-05-14 - [User-Controlled Proxy SSRF]
**Vulnerability:** Server-Side Request Forgery (SSRF) through customizable service endpoints (e.g., local Ollama instance).
**Learning:** Allowing users to specify custom API endpoints (like `X-Ollama-Endpoint`) creates an SSRF vector where the server can be used to scan internal networks or access cloud metadata services (169.254.169.254).
**Prevention:** Implement `is_safe_url` validation for all user-provided endpoints to block private, link-local, and loopback IP ranges, while explicitly allowing `localhost` only if the service is intended to be run alongside the backend.
