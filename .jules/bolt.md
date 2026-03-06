# Bolt's Performance Journal

## 2025-05-14 - Initial Performance Audit
**Learning:** Found that `generate_video` processes images sequentially using high-quality but slow `LANCZOS` resampling.
**Action:** Will parallelize image processing using `asyncio.to_thread` and switch to `BILINEAR` resampling for faster execution.
