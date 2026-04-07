import requests
import sys
import os
import tempfile
from PIL import Image

def test_api_basic():
    """Test basic API connectivity"""
    print("🔍 Testing API Root...")
    try:
        response = requests.get("http://localhost:8000/api/", timeout=10)
        if response.status_code == 200:
            print("✅ API Root - PASSED")
            return True
        else:
            print(f"❌ API Root - FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Root - ERROR: {e}")
        return False

def test_upload_image():
    """Test image upload"""
    print("🔍 Testing Image Upload...")
    
    # Create test image
    img = Image.new('RGB', (800, 600), color=(255, 100, 50))
    temp_path = os.path.join(tempfile.gettempdir(), "test_upload.jpg")
    img.save(temp_path, 'JPEG')
    
    try:
        with open(temp_path, 'rb') as f:
            files = {'files': ('test_upload.jpg', f, 'image/jpeg')}
            response = requests.post(
                "http://localhost:8000/api/upload-images",
                files=files, 
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            if 'urls' in data and len(data['urls']) > 0:
                print("✅ Image Upload - PASSED")
                return data['urls'][0]
            else:
                print(f"❌ Image Upload - No URLs in response: {data}")
                return None
        else:
            print(f"❌ Image Upload - FAILED: {response.status_code}, {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Image Upload - ERROR: {e}")
        return None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_get_projects():
    """Test get projects endpoint"""
    print("🔍 Testing Get Projects...")
    try:
        response = requests.get("http://localhost:8000/api/projects", timeout=15)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Get Projects - PASSED ({len(projects)} projects)")
            return True
        else:
            print(f"❌ Get Projects - FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get Projects - ERROR: {e}")
        return False

def main():
    print("🚀 Quick Backend API Tests")
    print("=" * 50)
    
    results = []
    
    # Test basic connectivity
    results.append(test_api_basic())
    
    # Test image upload
    uploaded_url = test_upload_image()
    results.append(uploaded_url is not None)
    
    # Test projects endpoint
    results.append(test_get_projects())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All basic backend tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())