## 2025-05-22 - Path Traversal in File Serving Endpoints
**Vulnerability:** The application was vulnerable to path traversal because it used user-provided filenames directly to construct file paths for serving uploads, videos, and audio. An attacker could use `../` sequences to read arbitrary files on the server (e.g., `/api/uploads/..%2Fserver.py`).

**Learning:** Using `pathlib.Path` with the `/` operator does not automatically prevent path traversal if the right-hand side contains traversal segments like `..`. Simply checking `path.exists()` is also insufficient as it will return true for the traversed path.

**Prevention:** Always sanitize user-provided filenames by extracting only the base name using `Path(filename).name`. Implement a centralized `safe_join` utility that enforces this pattern and explicitly blocks invalid names like `.` or `..` to ensure files are only served from the intended directories.
