## 2025-05-14 - [Async I/O and Parallel Image Processing]
**Learning:** In FastAPI applications, synchronous file I/O and CPU-bound operations (like PIL resizing) block the main event loop, causing severe performance degradation under concurrency. Parallelizing these tasks with `asyncio.gather` and offloading them to threads using `asyncio.to_thread` can yield massive speedups (measured ~86% for image preparation).
**Action:** Proactively identify blocking loops in async handlers and refactor them to use concurrent execution with `to_thread` helpers.
