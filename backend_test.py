import requests
import sys
import os
import tempfile
from datetime import datetime
from PIL import Image

class ArchitectureVideoAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.uploaded_images = []
        self.uploaded_audio = []
        self.generated_video_url = None
        self.project_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, timeout=60)
                elif data:
                    if isinstance(data, dict):
                        response = requests.post(url, data=data, timeout=60)
                    else:
                        headers['Content-Type'] = 'application/json'
                        response = requests.post(url, json=data, headers=headers, timeout=60)
                else:
                    response = requests.post(url, headers=headers, timeout=60)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Request Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_image(self, filename, width=800, height=600):
        """Create a test image file"""
        img = Image.new('RGB', (width, height), color=(255, 100, 50))  # Orange color
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        img.save(temp_path, 'JPEG')
        return temp_path

    def create_test_audio(self, filename):
        """Create a dummy test audio file"""
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(b'ID3\x03\x00\x00\x00\x00\x00\x00' + b'\x00' * 100)
        return temp_path

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test("API Root", "GET", "", 200)
        return success and "Architecture Video Generator API" in str(response)

    def test_upload_single_image(self):
        """Test uploading a single image"""
        test_image_path = self.create_test_image("test_single.jpg")
        
        try:
            with open(test_image_path, 'rb') as f:
                files = {'files': ('test_single.jpg', f, 'image/jpeg')}
                success, response = self.run_test(
                    "Upload Single Image", 
                    "POST", 
                    "upload-images", 
                    200, 
                    files=files
                )
            
            if success and 'urls' in response:
                self.uploaded_images.extend(response['urls'])
                print(f"✅ Uploaded image URLs: {response['urls']}")
                return True
            return False
        finally:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def test_upload_multiple_images(self):
        """Test uploading multiple images"""
        test_image1_path = self.create_test_image("test_multi1.jpg", 900, 600)
        test_image2_path = self.create_test_image("test_multi2.jpg", 700, 500)
        
        try:
            with open(test_image1_path, 'rb') as f1, open(test_image2_path, 'rb') as f2:
                files = [
                    ('files', ('test_multi1.jpg', f1.read(), 'image/jpeg')),
                    ('files', ('test_multi2.jpg', f2.read(), 'image/jpeg'))
                ]
                
                success, response = self.run_test(
                    "Upload Multiple Images", 
                    "POST", 
                    "upload-images", 
                    200, 
                    files=files
                )
            
            if success and 'urls' in response and len(response['urls']) == 2:
                self.uploaded_images.extend(response['urls'])
                print(f"✅ Uploaded {len(response['urls'])} images")
                return True
            return False
        finally:
            for path in [test_image1_path, test_image2_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_upload_audio(self):
        """Test uploading a background audio file"""
        test_audio_path = self.create_test_audio("test_audio.mp3")

        try:
            with open(test_audio_path, 'rb') as f:
                files = {'file': ('test_audio.mp3', f, 'audio/mpeg')}
                success, response = self.run_test(
                    "Upload Audio",
                    "POST",
                    "upload-audio",
                    200,
                    files=files
                )

            if success and 'url' in response:
                self.uploaded_audio.append(response['url'])
                print(f"✅ Uploaded audio URL: {response['url']}")
                return True
            return False
        finally:
            if os.path.exists(test_audio_path):
                os.remove(test_audio_path)

    def test_get_uploaded_image(self):
        """Test accessing an uploaded image"""
        if not self.uploaded_images:
            print("❌ No uploaded images to test")
            return False
        
        image_url = self.uploaded_images[0]
        image_filename = image_url.split('/')[-1]
        
        success, response = self.run_test(
            "Get Uploaded Image", 
            "GET", 
            f"uploads/{image_filename}", 
            200
        )
        return success

    def test_get_uploaded_audio(self):
        """Test accessing an uploaded audio file"""
        if not self.uploaded_audio:
            print("❌ No uploaded audio to test")
            return False

        audio_url = self.uploaded_audio[0]
        audio_filename = audio_url.split('/')[-1]

        success, response = self.run_test(
            "Get Uploaded Audio",
            "GET",
            f"audio/{audio_filename}",
            200
        )
        return success

    def test_generate_video_single_image(self):
        """Test video generation with a single image"""
        if not self.uploaded_images:
            print("❌ No uploaded images for video generation")
            return False
        
        data = {
            'image_urls': [self.uploaded_images[0]],
            'transition_duration': '1.0',
            'image_duration': '3.0'
        }
        
        success, response = self.run_test(
            "Generate Video (Single Image)", 
            "POST", 
            "generate-video", 
            200, 
            data=data
        )
        
        if success and 'video_url' in response and 'project_id' in response:
            self.generated_video_url = response['video_url']
            self.project_id = response['project_id']
            print(f"✅ Generated video: {self.generated_video_url}")
            return True
        return False

    def test_generate_video_multiple_images(self):
        """Test video generation with multiple images"""
        if len(self.uploaded_images) < 2:
            print("❌ Need at least 2 uploaded images for multiple image test")
            return False
        
        data = {
            'image_urls': self.uploaded_images[:2],
            'transition_duration': '1.5',
            'image_duration': '4.0'
        }
        
        success, response = self.run_test(
            "Generate Video (Multiple Images)", 
            "POST", 
            "generate-video", 
            200, 
            data=data
        )
        
        if success and 'video_url' in response:
            print(f"✅ Generated multi-image video: {response['video_url']}")
            return True
        return False

    def test_get_generated_video(self):
        """Test accessing a generated video"""
        if not self.generated_video_url:
            print("❌ No generated video to test")
            return False
        
        video_filename = self.generated_video_url.split('/')[-1]
        
        success, response = self.run_test(
            "Get Generated Video", 
            "GET", 
            f"videos/{video_filename}", 
            200
        )
        return success

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test("Get Projects", "GET", "projects", 200)
        
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} projects")
            return True
        return False

    def test_delete_project(self):
        """Test deleting a project"""
        if not self.project_id:
            print("❌ No project to delete")
            return False
        
        success, response = self.run_test(
            "Delete Project", 
            "DELETE", 
            f"projects/{self.project_id}", 
            200
        )
        return success

    def test_error_cases(self):
        """Test various error scenarios"""
        print("\n🔍 Testing Error Cases...")
        
        success1, _ = self.run_test("Upload No Files", "POST", "upload-images", 422)
        success_audio_err, _ = self.run_test("Upload Audio No File", "POST", "upload-audio", 422)
        
        data = {'image_urls': [], 'transition_duration': '1.0', 'image_duration': '3.0'}
        success2, _ = self.run_test("Generate Video No Images", "POST", "generate-video", 400, data=data)
        
        success3, _ = self.run_test("Get Non-existent Image", "GET", "uploads/nonexistent.jpg", 404)
        success4, _ = self.run_test("Get Non-existent Video", "GET", "videos/nonexistent.mp4", 404)
        
        return success1 and success2 and success3 and success4 and success_audio_err

def main():
    print("🚀 Starting Architecture Video Generator API Tests")
    print("=" * 60)
    
    tester = ArchitectureVideoAPITester()
    
    test_results = [
        tester.test_api_root(),
        tester.test_upload_single_image(),
        tester.test_upload_multiple_images(), 
        tester.test_upload_audio(),
        tester.test_get_uploaded_audio(),
        tester.test_get_uploaded_image(),
        tester.test_generate_video_single_image(),
        tester.test_generate_video_multiple_images(),
        tester.test_get_generated_video(),
        tester.test_get_projects(),
        tester.test_delete_project(),
        tester.test_error_cases()
    ]
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if all(test_results):
        print("✅ All core functionality tests passed!")
        return 0
    else:
        print("❌ Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())