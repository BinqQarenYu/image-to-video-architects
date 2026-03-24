import asyncio
import time
import os
import shutil
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient
from backend.server import app, UPLOADS_DIR, VIDEOS_DIR

# Set up test environment
UPLOADS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

def create_dummy_images(count=10, size=(4000, 3000)):
    urls = []
    for i in range(count):
        img = Image.new('RGB', size, color=(i*10, i*20, i*30))
        filename = f"test_perf_{i}.jpg"
        filepath = UPLOADS_DIR / filename
        img.save(filepath)
        urls.append(f"/api/uploads/{filename}")
    return urls

def test_video_gen_functional():
    client = TestClient(app)
    image_urls = create_dummy_images(5)

    start_time = time.time()
    # Mocking ffmpeg.run and ffmpeg.input (for the first-frame-only case)
    from unittest import mock
    with mock.patch('ffmpeg.run') as mock_run, mock.patch('ffmpeg.input') as mock_input:
        response = client.post(
            "/api/generate-video",
            data={
                "image_urls": image_urls,
                "transition_duration": 1.0,
                "image_duration": 3.0,
                "aspect_ratio": "16:9",
                "quality": "720p",
                "format": "mp4"
            }
        )
        duration = time.time() - start_time

        # We expect a success or a specific error message if ffmpeg was the only blocker
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response detail: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "video_url" in data
    assert "project_id" in data

    # video_path = VIDEOS_DIR / data["video_url"].split("/")[-1]
    # assert video_path.exists() # Mocked ffmpeg won't create the file
    print(f"Functional test (image processing part) passed. Duration: {duration:.2f}s")

    # Cleanup
    for url in image_urls:
        (UPLOADS_DIR / url.split("/")[-1]).unlink()
    # video_path.unlink() # video_path is not defined

async def main():
    print("Running functional and performance verification...")
    try:
        test_video_gen_functional()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
