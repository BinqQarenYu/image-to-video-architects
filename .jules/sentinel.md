## 2025-05-15 - Hardening File serving against Path Traversal
**Vulnerability:** Path traversal in file-serving endpoints (/api/uploads, /api/videos, /api/audio).
**Learning:** Using simple string concatenation or manual joining of user input to base directories without sanitization allows attackers to access arbitrary files on the system using '../' sequences.
**Prevention:** Implement a centralized `safe_join` utility that uses `pathlib.Path(filename).name` to strip any directory components from user-provided filenames, and reject empty or relative directory markers ('.', '..'). Apply this utility to all endpoints that access files based on user input.
