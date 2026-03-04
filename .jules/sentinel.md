## 2026-03-04 - [SSRF vulnerability in Ollama endpoint]
**Vulnerability:** The application allows users to specify a custom Ollama endpoint via a request header (`X-Ollama-Endpoint`). This endpoint is then used in a server-side POST request without validation, allowing a malicious user to make requests to internal services or cloud metadata endpoints (SSRF).
**Learning:** Providing flexibility for local/custom AI endpoints can introduce SSRF risks if the input is not validated against internal IP ranges.
**Prevention:** Always validate user-provided URLs. Block access to sensitive internal IP ranges (e.g., 169.254.169.254) and only allow safe schemes (http/https).
