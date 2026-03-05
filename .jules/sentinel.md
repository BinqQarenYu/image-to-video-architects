## 2026-03-05 - Path Traversal in File Serving Endpoints
**Vulnerability:** Path traversal via user-supplied filenames in `/api/uploads`, `/api/videos`, and `/api/audio`.
**Learning:** Joining raw user input from path parameters directly with a base directory allows access to files outside the intended scope. Redundant endpoint definitions can also hide vulnerabilities if one is fixed and the other is not.
**Prevention:** Use a centralized `safe_join` utility that strips directory segments using `Path(filename).name` and validates the result before file access. Consolidate redundant routes to ensure security fixes are applied universally.
