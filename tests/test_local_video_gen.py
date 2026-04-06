import requests
import os
import tempfile
from PIL import Image

BASE_URL = "http://localhost:8000/api"

def test_api_root():
    print("🔍 Testing API Root...")
    try:
        r = requests.get(f"{BASE_URL}/")
        r.raise_for_status()
        print(f"✅ API Root: {r.json()}")
        return True
    except Exception as e:
        print(f"❌ API Root failed: {e}")
        return False

def test_generate_video():
    print("🔍 Testing Video Generation (Parallelized)...")
    try:
        # 1. Upload two images
        uploaded_urls = []
        for i in range(2):
            img = Image.new('RGB', (100, 100), color=(i*100, 0, 0))
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                img.save(f.name)
                with open(f.name, 'rb') as rb:
                    r = requests.post(f"{BASE_URL}/upload-images", files={'files': rb})
                    r.raise_for_status()
                    uploaded_urls.append(r.json()['urls'][0])
            os.unlink(f.name)

        # 2. Generate video
        data = {
            'image_urls': uploaded_urls,
            'image_duration': 1.0,
            'aspect_ratio': '16:9'
        }
        print(f"Sending request with {len(uploaded_urls)} images...")
        r = requests.post(f"{BASE_URL}/generate-video", data=data)
        r.raise_for_status()
        print(f"✅ Video Generated: {r.json()['video_url']}")
        return True
    except Exception as e:
        print(f"❌ Video Generation failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    s1 = test_api_root()
    s2 = test_generate_video()
    if s1 and s2:
        print("\n🚀 All local tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed.")
        exit(1)
