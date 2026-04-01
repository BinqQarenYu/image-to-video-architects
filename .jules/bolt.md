## 2025-05-15 - Parallelizing Image Processing with Threading
**Learning:** For CPU-bound tasks like image resizing in an async FastAPI environment, standard sequential loops block the event loop and slow down the entire application. Offloading these tasks to threads using `asyncio.to_thread` combined with `asyncio.gather` allows for concurrent execution, yielding a significant speedup (approx. 5.6x to 6.4x based on theoretical analysis for multi-image sets) while keeping the event loop responsive.
**Action:** Always prefer `asyncio.to_thread` for Pillow image operations in async endpoints.

## 2025-05-15 - Regressions during Search-and-Replace
**Learning:** Targeted search-and-replace using tools like `replace_with_git_merge_diff` can lead to accidental deletion of neighboring code (like redundant-looking routes) if the search block is not sufficiently precise or if the agent over-cleans.
**Action:** Double-check that no unrelated routes or core functions are removed during refactoring, especially when consolidating shadowed routes.
