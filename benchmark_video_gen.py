import time
import os
import tempfile
from PIL import Image
import asyncio
import concurrent.futures

def prepare_image_original(source_path, processed_path, width, height):
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img.save(processed_path, 'JPEG', quality=95)

def prepare_image_optimized(source_path, processed_path, width, height):
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.BILINEAR)
    img.save(processed_path, 'JPEG', quality=95)

async def benchmark():
    width, height = 1920, 1080
    num_images = 10

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = os.path.join(tmp_dir)
        source_images = []
        for i in range(num_images):
            p = os.path.join(tmp, f"source_{i}.jpg")
            img = Image.new('RGB', (3000, 2000), color=(i*10, 100, 200))
            img.save(p, 'JPEG')
            source_images.append(p)

        print(f"Benchmarking {num_images} images (3000x2000 -> 1920x1080)...")

        # 1. Original (Sequential + LANCZOS)
        start = time.time()
        for i, p in enumerate(source_images):
            out = os.path.join(tmp, f"out_orig_{i}.jpg")
            prepare_image_original(p, out, width, height)
        orig_duration = time.time() - start
        print(f"1. Original (Sequential, LANCZOS): {orig_duration:.4f}s")

        # 2. Optimized Algorithm (Sequential + BILINEAR)
        start = time.time()
        for i, p in enumerate(source_images):
            out = os.path.join(tmp, f"out_opt_algo_{i}.jpg")
            prepare_image_optimized(p, out, width, height)
        opt_algo_duration = time.time() - start
        print(f"2. Optimized Algo (Sequential, BILINEAR): {opt_algo_duration:.4f}s")

        # 3. Optimized Parallel (Parallel + BILINEAR)
        start = time.time()
        tasks = []
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            for i, p in enumerate(source_images):
                out = os.path.join(tmp, f"out_opt_para_{i}.jpg")
                tasks.append(loop.run_in_executor(pool, prepare_image_optimized, p, out, width, height))
            await asyncio.gather(*tasks)
        opt_para_duration = time.time() - start
        print(f"3. Optimized Parallel (Parallel, BILINEAR): {opt_para_duration:.4f}s")

        total_improvement = (orig_duration - opt_para_duration) / orig_duration * 100
        print(f"Total Speedup (Algo + Parallel): {total_improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(benchmark())
