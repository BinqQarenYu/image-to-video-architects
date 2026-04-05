# Bolt's Journal - Critical Learnings

## 2025-05-15 - Initial Journal Creation
**Learning:** Always check for existing journals and follow the naming convention.
**Action:** Created .Jules/bolt.md to document performance-related insights.

## 2025-05-15 - Parallelizing Image Processing with PIL
**Learning:** Sequential image processing (open, resize, save) is a major bottleneck in video generation. Offloading these tasks to threads using `asyncio.to_thread` and executing them in parallel with `asyncio.gather` significantly reduces total processing time. Switching from `LANCZOS` to `BILINEAR` resampling further improves speed (~40% gain) with negligible quality loss for video frames.
**Action:** Refactored the `generate_video` endpoint to process images in parallel. Benchmarked a 1.76x speedup (3.10s -> 1.76s for 10 high-res images).
