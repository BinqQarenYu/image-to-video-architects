import requests

url = "http://localhost:8000/api/generate-script"
headers = {
    "X-Ollama-Endpoint": "http://localhost:11434",
    "Content-Type": "application/json"
}
data = {
    "prompt": "A cinematic tour of a modern concrete mansion in a pine forest",
    "provider": "ollama",
    "num_scenes": 3
}

try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("Success:")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response text: {e.response.text}")
