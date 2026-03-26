import time
import asyncio
from PIL import Image
from pathlib import Path
import tempfile
import os

def create_dummy_image(path, size=(1920, 1080)):
    img = Image.new('RGB', size, color=(73, 109, 137))
    img.save(path, 'JPEG')

def _prepare_image_sequential(source_path: Path, processed_path: Path, width: int, height: int):
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(processed_path, 'JPEG', quality=95)

def _prepare_image_optimized(source_path: Path, processed_path: Path, width: int, height: int):
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.BILINEAR)
    img.save(processed_path, 'JPEG', quality=95)

def process_sequential(image_paths, target_size, temp_path):
    processed_paths = []
    width, height = target_size
    for idx, source_path in enumerate(image_paths):
        processed_path = temp_path / f"image_seq_{idx:04d}.jpg"
        _prepare_image_sequential(source_path, processed_path, width, height)
        processed_paths.append(str(processed_path))
    return processed_paths

async def process_parallel(image_paths, target_size, temp_path):
    width, height = target_size
    tasks = []
    for idx, source_path in enumerate(image_paths):
        processed_path = temp_path / f"image_par_{idx:04d}.jpg"
        tasks.append(asyncio.to_thread(_prepare_image_optimized, source_path, processed_path, width, height))
    await asyncio.gather(*tasks)
    return [str(temp_path / f"image_par_{idx:04d}.jpg") for idx in range(len(image_paths))]

async def main():
    num_images = 20
    target_size = (1920, 1080)

    with tempfile.TemporaryDirectory() as base_dir:
        base_path = Path(base_dir)
        input_dir = base_path / "inputs"
        input_dir.mkdir()

        image_paths = []
        for i in range(num_images):
            p = input_dir / f"input_{i}.jpg"
            create_dummy_image(p, size=(3840, 2160))
            image_paths.append(p)

        print(f"Benchmarking {num_images} images (4K -> 1080p)...")

        # Sequential
        seq_temp = base_path / "seq_outputs"
        seq_temp.mkdir()
        start_time = time.perf_counter()
        process_sequential(image_paths, target_size, seq_temp)
        seq_time = time.perf_counter() - start_time
        print(f"Sequential (LANCZOS) time: {seq_time:.4f}s")

        # Parallel + Bilinear
        par_temp = base_path / "par_outputs"
        par_temp.mkdir()
        start_time = time.perf_counter()
        await process_parallel(image_paths, target_size, par_temp)
        par_time = time.perf_counter() - start_time
        print(f"Parallel (BILINEAR) time:   {par_time:.4f}s")

        improvement = (seq_time - par_time) / seq_time * 100
        print(f"\nImprovement: {improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
