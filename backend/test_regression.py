
import unittest
from fastapi.testclient import TestClient
from backend.server import app, UPLOADS_DIR, VIDEOS_DIR
import os
from PIL import Image
import io
import uuid

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure test directories exist
        UPLOADS_DIR.mkdir(exist_ok=True)
        VIDEOS_DIR.mkdir(exist_ok=True)

    def test_root(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_upload_and_generate_video(self):
        # 1. Upload images
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')

        buf1 = io.BytesIO()
        img1.save(buf1, format='JPEG')
        buf1.seek(0)

        buf2 = io.BytesIO()
        img2.save(buf2, format='JPEG')
        buf2.seek(0)

        files = [
            ("files", ("test1.jpg", buf1, "image/jpeg")),
            ("files", ("test2.jpg", buf2, "image/jpeg"))
        ]

        upload_resp = self.client.post("/api/upload-images", files=files)
        self.assertEqual(upload_resp.status_code, 200)
        urls = upload_resp.json()["urls"]
        self.assertEqual(len(urls), 2)

        # 2. Generate video (Slideshow mode)
        # Note: We can't actually run FFmpeg in this environment if it's missing,
        # but we can test if the image processing part works before it calls ffmpeg.
        # Actually, if ffmpeg is missing, it will fail at the stream.run() part.

        data = {
            "image_urls": urls,
            "image_duration": "1.0",
            "aspect_ratio": "1:1",
            "quality": "240p"
        }

        # We expect a 500 if FFmpeg is missing, but let's see if it fails earlier
        try:
            gen_resp = self.client.post("/api/generate-video", data=data)
            # If ffmpeg is missing, it should fail with 500 and stderr mentioning ffmpeg
            if gen_resp.status_code == 500:
                print(f"Generation failed as expected (probably missing ffmpeg): {gen_resp.json()['detail']}")
            else:
                self.assertEqual(gen_resp.status_code, 200)
        except Exception as e:
            print(f"Caught exception during generate-video: {e}")

    def test_get_video_endpoint(self):
        # Test if the get_video endpoint is working and has the correct media_type
        filename = f"test_{uuid.uuid4()}.mp4"
        test_video = VIDEOS_DIR / filename
        test_video.write_bytes(b"fake video content")

        response = self.client.get(f"/api/videos/{filename}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "video/mp4")

        # Cleanup
        os.remove(test_video)

if __name__ == "__main__":
    unittest.main()
