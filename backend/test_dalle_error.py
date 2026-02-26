import httpx
import asyncio

async def test_dalle():
    async with httpx.AsyncClient() as client:
        # Intentionally trigger DALL-E with a prompt to see why the backend throws a 400
        res = await client.post(
            "http://localhost:8000/api/generate-image",
            json={"prompt": "A beautiful cinematic shot of a sunset", "providers": ["dalle"]},
            headers={"X-OpenAI-Key": "test_key"}
        )
        print(res.status_code)
        print(res.text)

if __name__ == "__main__":
    asyncio.run(test_dalle())
