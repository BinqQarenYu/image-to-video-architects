from fastapi.testclient import TestClient
from backend.server import app, UPLOADS_DIR, VIDEOS_DIR
import os
import io
from PIL import Image
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/api/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_upload_image():
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    response = client.post(
        "/api/upload-images",
        files={"files": ("test.jpg", img_byte_arr, "image/jpeg")}
    )
    assert response.status_code == 200
    assert "urls" in response.json()
    assert len(response.json()["urls"]) > 0
    return response.json()["urls"][0]

def test_generate_video():
    # 1. Upload an image
    img_url = test_upload_image()

    # 2. Generate video
    response = client.post(
        "/api/generate-video",
        data={
            "image_urls": [img_url],
            "image_duration": 1.0,
            "aspect_ratio": "16:9",
            "quality": "360p"
        }
    )
    assert response.status_code == 200
    assert "video_url" in response.json()
    video_url = response.json()["video_url"]

    # Check if file exists
    video_filename = video_url.split("/")[-1]
    assert (VIDEOS_DIR / video_filename).exists()

if __name__ == "__main__":
    test_read_root()
    print("Root test passed")
    test_upload_image()
    print("Upload test passed")
    try:
        test_generate_video()
        print("Video generation test passed")
    except Exception as e:
        print(f"Video generation test failed: {e}")
        # ffmpeg might not be installed in the environment
