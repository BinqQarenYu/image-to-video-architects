## 2025-05-15 - [Parallel Image Processing for Video Generation]
**Learning:** Heavy CPU-bound tasks like image resizing (PIL) in a FastAPI async endpoint can block the event loop, causing poor responsiveness. Parallelizing these tasks with `asyncio.to_thread` and `asyncio.gather` significantly improves performance.
**Action:** Always offload blocking PIL operations to threads using `asyncio.to_thread` when processing multiple assets in an async context.

## 2025-05-15 - [Resampling Filter Performance Trade-off]
**Learning:** `LANCZOS` resampling is high-quality but slow. For video generation where frames are displayed for short durations, `BILINEAR` offers a much better performance-to-quality ratio.
**Action:** Use `BILINEAR` or `BICUBIC` for fast asset preparation in video pipelines unless extreme quality is requested.
