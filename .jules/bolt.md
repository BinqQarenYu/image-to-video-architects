## 2026-03-16 - Concurrency in Asset Preparation
**Learning:** Parallelizing I/O-bound and CPU-bound tasks (like image resizing and file saving) in FastAPI using `asyncio.gather` and `asyncio.to_thread` significantly reduces latency for batch operations. Combining this with faster algorithms (e.g., BILINEAR resizing) provides a compound performance win.
**Action:** Always look for sequential loops handling independent I/O or processing tasks and refactor them to use concurrent execution patterns.
