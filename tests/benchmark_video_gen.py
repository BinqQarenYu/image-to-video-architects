import asyncio
import time
from pathlib import Path
from PIL import Image
import tempfile
import shutil

# Mocking parts of the server for benchmarking
def sync_process_images(image_paths, width, height):
    processed_images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for idx, source_path in enumerate(image_paths):
            img = Image.open(source_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            processed_path = temp_path / f"image_{idx:04d}.jpg"
            img.save(processed_path, 'JPEG', quality=95)
            processed_images.append(str(processed_path))
    return processed_images

async def process_image(idx, source_path, width, height, temp_path):
    def _inner():
        img = Image.open(source_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((width, height), Image.Resampling.BILINEAR)
        processed_path = temp_path / f"image_{idx:04d}.jpg"
        img.save(processed_path, 'JPEG', quality=95)
        return str(processed_path)
    return await asyncio.to_thread(_inner)

async def async_process_images(image_paths, width, height):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tasks = [process_image(idx, path, width, height, temp_path) for idx, path in enumerate(image_paths)]
        return await asyncio.gather(*tasks)

def setup_test_images(count=10):
    assets_dir = Path("tests/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    for i in range(count):
        path = assets_dir / f"test_{i}.jpg"
        if not path.exists():
            img = Image.new('RGB', (2000, 2000), color=(i*20, i*20, i*20))
            img.save(path)
        image_paths.append(path)
    return image_paths

async def run_benchmark():
    image_paths = setup_test_images(10)
    width, height = 1920, 1080

    print(f"Benchmarking with {len(image_paths)} images...")

    # Baseline
    start = time.perf_counter()
    sync_process_images(image_paths, width, height)
    sync_time = time.perf_counter() - start
    print(f"Sync (LANCZOS) time: {sync_time:.4f}s")

    # Optimized
    start = time.perf_counter()
    await async_process_images(image_paths, width, height)
    async_time = time.perf_counter() - start
    print(f"Async (BILINEAR) time: {async_time:.4f}s")

    improvement = (sync_time - async_time) / sync_time * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
