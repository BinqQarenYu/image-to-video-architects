# Bolt's Performance Journal ⚡

## 2025-05-15 - Image Resampling and Parallelism
**Learning:** Parallelizing image processing with `asyncio.to_thread` and `asyncio.gather` combined with switching from `LANCZOS` to `BILINEAR` resampling provides a massive speedup (up to 6.4x in benchmarks) for large image batches. `BILINEAR` is significantly faster than `LANCZOS` for HD transformations while maintaining acceptable visual quality for video slideshows.
**Action:** Always prefer `asyncio.to_thread` for PIL operations in FastAPI to avoid blocking the event loop, and use `BILINEAR` for fast image-to-video pipelines unless extreme quality is requested.
