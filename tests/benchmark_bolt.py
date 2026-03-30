import time
import asyncio
from PIL import Image
import os
import tempfile
from pathlib import Path
import concurrent.futures

def process_sequential(image_paths, width, height, temp_path):
    start_time = time.time()
    processed_images = []
    for idx, source_path in enumerate(image_paths):
        img = Image.open(source_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        processed_path = temp_path / f"seq_image_{idx:04d}.jpg"
        img.save(processed_path, 'JPEG', quality=95)
        processed_images.append(str(processed_path))
    end_time = time.time()
    return end_time - start_time

def _prepare_image(source_path, width, height, processed_path):
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.BILINEAR)
    img.save(processed_path, 'JPEG', quality=95)

async def process_parallel(image_paths, width, height, temp_path):
    start_time = time.time()
    tasks = []
    for idx, source_path in enumerate(image_paths):
        processed_path = temp_path / f"par_image_{idx:04d}.jpg"
        tasks.append(asyncio.to_thread(_prepare_image, source_path, width, height, processed_path))
    await asyncio.gather(*tasks)
    end_time = time.time()
    return end_time - start_time

def create_test_images(temp_path, count=10):
    paths = []
    for i in range(count):
        path = temp_path / f"test_{i}.jpg"
        img = Image.new('RGB', (3000, 2000), color=(i * 20, 100, 150))
        img.save(path, 'JPEG')
        paths.append(str(path))
    return paths

async def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        print(f"Creating 10 high-resolution test images...")
        image_paths = create_test_images(tmp_path, 10)

        width, height = 1920, 1080

        print(f"Running Sequential (LANCZOS)...")
        seq_time = process_sequential(image_paths, width, height, tmp_path)
        print(f"Sequential time: {seq_time:.4f}s")

        print(f"Running Parallel (BILINEAR)...")
        par_time = await process_parallel(image_paths, width, height, tmp_path)
        print(f"Parallel time: {par_time:.4f}s")

        improvement = (seq_time - par_time) / seq_time * 100
        speedup = seq_time / par_time
        print(f"\nOptimization Results:")
        print(f"Time saved: {seq_time - par_time:.4f}s ({improvement:.2f}%)")
        print(f"Speedup: {speedup:.2f}x")

if __name__ == "__main__":
    asyncio.run(main())
