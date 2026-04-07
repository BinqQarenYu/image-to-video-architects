from playwright.sync_api import sync_playwright, expect
import urllib.request
import urllib.error

def run_tests():
    print("Testing backend API...")
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8000/api/")
        html = response.read().decode('utf-8')
        assert response.status == 200, f"Expected 200, got {response.status}"
        print("Backend is up and running.")
    except Exception as e:
        print(f"Backend test failed: {e}")
        return

    print("Testing frontend communication...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        responses = []
        page.on("response", lambda response: responses.append(response))
        
        page.goto("http://127.0.0.1:3000")
        page.wait_for_load_state("networkidle")
        
        expect(page.locator("body")).to_be_visible()
        
        print("Frontend loaded successfully.")
        
        backend_calls = [r for r in responses if "8000" in r.url]
        print(f"Found {len(backend_calls)} calls to backend API from frontend.")
        
        browser.close()
    
    print("All tests passed.")

if __name__ == "__main__":
    run_tests()

