from playwright.sync_api import sync_playwright
import time

def debug_upload():
    print("Testing frontend image upload communication...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen to console logs to catch frontend errors
        page.on("console", lambda msg: print(f"Frontend Console [{msg.type}]: {msg.text}"))
        
        # Listen to network responses to see if the upload request is made and what it returns
        page.on("response", lambda response: print(f"Network: {response.url} - Status: {response.status}"))
        
        page.goto("http://localhost:3001")
        page.wait_for_load_state("networkidle")
        
        print("Page loaded. Executing fetch to upload an image...")
        
        # Simulating upload and then video generation
        script = """
        async () => {
            const formData = new FormData();
            
            // Create a simple 1x1 transparent PNG blob
            const b64Data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg==';
            const bstr = atob(b64Data);
            let n = bstr.length;
            const u8arr = new Uint8Array(n);
            while (n--) {
                u8arr[n] = bstr.charCodeAt(n);
            }
            const blob = new Blob([u8arr], { type: 'image/png' });
            formData.append('files', blob, 'test.png');
            
            try {
                // 1. Upload
                const res = await fetch('http://127.0.0.1:8000/api/upload-images', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                console.log("Upload Success:", JSON.stringify(data));
                
                // 2. Generate video
                const genData = new FormData();
                genData.append('image_urls', data.urls[0]);
                genData.append('transition_style', 'fade');
                genData.append('transition_duration', '1');
                genData.append('image_duration', '3');
                genData.append('aspect_ratio', '16:9');
                
                const genRes = await fetch('http://127.0.0.1:8000/api/generate-video', {
                    method: 'POST',
                    body: genData
                });
                const genJson = await genRes.json();
                console.log("Video Generation Response:", JSON.stringify(genJson));
            } catch (err) {
                console.error("Test Error:", err.message);
            }
        }
        """
        page.evaluate(script)
        
        # Wait for backend background task to trigger and log
        page.wait_for_timeout(5000)
        
        browser.close()
        print("Finished debugging front-end upload.")

if __name__ == "__main__":
    debug_upload()
