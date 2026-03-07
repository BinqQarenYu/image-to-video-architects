
import asyncio
import time
from PIL import Image
from pathlib import Path
import tempfile
import shutil

# Mocking the environment
UPLOADS_DIR = Path("backend/uploads")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def create_test_images(num=10):
    paths = []
    for i in range(num):
        path = UPLOADS_DIR / f"test_{i}.jpg"
        img = Image.new('RGB', (4000, 3000), color=(i*10, i*20, i*30))
        img.save(path)
        paths.append(f"/api/uploads/test_{i}.jpg")
    return paths

def process_image_sync(url, idx, width, height, temp_path):
    filename = url.split('/')[-1]
    source_path = UPLOADS_DIR / filename
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    processed_path = temp_path / f"image_{idx:04d}.jpg"
    img.save(processed_path, 'JPEG', quality=95)
    return str(processed_path)

async def process_image_async(url, idx, width, height, temp_path):
    return await asyncio.to_thread(process_image_sync_bilinear, url, idx, width, height, temp_path)

def process_image_sync_bilinear(url, idx, width, height, temp_path):
    filename = url.split('/')[-1]
    source_path = UPLOADS_DIR / filename
    img = Image.open(source_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img = img.resize((width, height), Image.Resampling.BILINEAR)
    processed_path = temp_path / f"image_{idx:04d}.jpg"
    img.save(processed_path, 'JPEG', quality=95)
    return str(processed_path)

async def main():
    num_images = 10
    width, height = 1920, 1080
    image_urls = create_test_images(num_images)

    print(f"Benchmarking with {num_images} images...")

    # Sequential LANCZOS (Current)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        start = time.time()
        processed_images = []
        for idx, url in enumerate(image_urls):
            processed_images.append(process_image_sync(url, idx, width, height, temp_path))
        end = time.time()
        print(f"Sequential LANCZOS: {end - start:.4f}s")

    # Parallel BILINEAR (Proposed)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        start = time.time()
        tasks = [process_image_async(url, idx, width, height, temp_path) for idx, url in enumerate(image_urls)]
        processed_images = await asyncio.gather(*tasks)
        end = time.time()
        print(f"Parallel BILINEAR: {end - start:.4f}s")

if __name__ == "__main__":
    asyncio.run(main())
