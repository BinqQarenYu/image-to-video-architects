import requests
import sys
import os

def test_upload():
    # Ensure file exists
    file_path = "e:/012A_Github/image-to-video-architects/frontend/public/index.html"
    if not os.path.exists(file_path):
        print("Test file not found")
        sys.exit(1)
        
    print(f"Testing upload with {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "http://localhost:8000/api/upload-images",
                files={"files": f}
            )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_upload()
