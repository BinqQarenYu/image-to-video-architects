import asyncio
import time
import os
from pathlib import Path
from PIL import Image
import io

def create_dummy_images(count=10, size=(4000, 3000)):
    uploads_dir = Path("backend/uploads")
    uploads_dir.mkdir(exist_ok=True)
    urls = []
    for i in range(count):
        img = Image.new('RGB', size, color=(i*10, i*20, i*30))
        filename = f"dummy_{i}.jpg"
        filepath = uploads_dir / filename
        img.save(filepath)
        urls.append(f"/api/uploads/{filename}")
    return urls

async def benchmark_original():
    # Mocking the logic in generate_video
    image_urls = [f"/api/uploads/dummy_{i}.jpg" for i in range(10)]
    width, height = 1920, 1080
    uploads_dir = Path("backend/uploads")

    start_time = time.time()
    processed_images = []
    # We use a temp dir in the real code, but here we just simulate
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        for idx, url in enumerate(image_urls):
            filename = url.split('/')[-1]
            source_path = uploads_dir / filename
            img = Image.open(source_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # CURRENT CODE USES LANCZOS
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            processed_path = temp_path / f"image_{idx:04d}.jpg"
            img.save(processed_path, 'JPEG', quality=95)
            processed_images.append(str(processed_path))

    end_time = time.time()
    print(f"Original (LANCZOS, Sequential) took: {end_time - start_time:.4f}s")
    return end_time - start_time

async def benchmark_optimized():
    image_urls = [f"/api/uploads/dummy_{i}.jpg" for i in range(10)]
    width, height = 1920, 1080
    uploads_dir = Path("backend/uploads")

    def process_image(idx, url, target_width, target_height, temp_path):
        filename = url.split('/')[-1]
        source_path = uploads_dir / filename
        img = Image.open(source_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # OPTIMIZED USES BILINEAR
        img = img.resize((target_width, target_height), Image.Resampling.BILINEAR)
        processed_path = temp_path / f"image_{idx:04d}.jpg"
        img.save(processed_path, 'JPEG', quality=95)
        return str(processed_path)

    start_time = time.time()
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tasks = [
            asyncio.to_thread(process_image, idx, url, width, height, temp_path)
            for idx, url in enumerate(image_urls)
        ]
        processed_images = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Optimized (BILINEAR, Parallel) took: {end_time - start_time:.4f}s")
    return end_time - start_time

async def main():
    create_dummy_images()
    t1 = await benchmark_original()
    t2 = await benchmark_optimized()
    print(f"Improvement: {(t1-t2)/t1*100:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
