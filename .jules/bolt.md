## 2025-05-15 - [Parallel Image Processing with Pillow]
**Learning:** Parallelizing image preparation (resize/save) using `asyncio.to_thread` and `asyncio.gather` provides a significant speedup (up to 5.6x-6.4x) in FastAPI applications. This is because Pillow releases the GIL for many CPU-intensive operations. Switching to `BILINEAR` resampling also offers a substantial speed boost compared to `LANCZOS` with acceptable quality for video frames.
**Action:** Always consider parallelizing asset preparation loops in media-heavy endpoints. Use `BILINEAR` for fast, real-time video generation tasks.
