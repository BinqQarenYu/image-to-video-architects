## 2025-05-15 - Parallel Image Preparation in FastAPI
**Learning:** Sequential image processing (resizing and saving) is a significant bottleneck in video generation endpoints. While FFmpeg does the heavy lifting, the preparation phase (especially using `LANCZOS` resampling) can take seconds per image.
**Action:** Use `asyncio.gather` with `asyncio.to_thread` to parallelize image processing. Switching from `LANCZOS` to `BILINEAR` provides a massive speed boost for video frames with negligible quality loss.

## 2025-05-15 - Async Responsiveness and Blocking I/O
**Learning:** Synchronous file operations like `Path.write_text` block the FastAPI event loop, reducing overall server throughput even for unrelated requests.
**Action:** Always wrap synchronous I/O in `asyncio.to_thread` within async route handlers to maintain event loop responsiveness.
