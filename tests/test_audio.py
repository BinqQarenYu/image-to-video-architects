import pytest
import respx
import httpx
from fastapi import HTTPException
from backend.server import app, AudioRequest

@pytest.mark.asyncio
async def test_generate_audio_elevenlabs_success():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        with respx.mock:
            respx.post("https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB").mock(
                return_value=httpx.Response(200, content=b"fake_audio_content")
            )

            response = await ac.post(
                "/api/generate-audio",
                json={"prompt": "Hello", "provider": "elevenlabs"},
                headers={"X-ElevenLabs-Key": "fake_key"}
            )

            assert response.status_code == 200
            assert "url" in response.json()
            assert response.json()["url"].startswith("/api/audio/")

@pytest.mark.asyncio
async def test_generate_audio_openai_success():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        with respx.mock:
            respx.post("https://api.openai.com/v1/audio/speech").mock(
                return_value=httpx.Response(200, content=b"fake_audio_content")
            )

            response = await ac.post(
                "/api/generate-audio",
                json={"prompt": "Hello", "provider": "openai"},
                headers={"X-OpenAI-Key": "fake_key"}
            )

            assert response.status_code == 200
            assert "url" in response.json()
            assert response.json()["url"].startswith("/api/audio/")

@pytest.mark.asyncio
async def test_generate_audio_missing_prompt():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-audio",
            json={"prompt": "", "provider": "elevenlabs"},
            headers={"X-ElevenLabs-Key": "fake_key"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Text is required for audio generation"

        response = await ac.post(
            "/api/generate-audio",
            json={"prompt": "   ", "provider": "elevenlabs"},
            headers={"X-ElevenLabs-Key": "fake_key"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Text is required for audio generation"

@pytest.mark.asyncio
async def test_generate_audio_elevenlabs_missing_key():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-audio",
            json={"prompt": "Hello", "provider": "elevenlabs"}
            # No header
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "ElevenLabs key required"

@pytest.mark.asyncio
async def test_generate_audio_openai_missing_key():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-audio",
            json={"prompt": "Hello", "provider": "openai"}
            # No header
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "OpenAI key required"

@pytest.mark.asyncio
async def test_generate_audio_unknown_provider():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/generate-audio",
            json={"prompt": "Hello", "provider": "invalid"},
            headers={"X-ElevenLabs-Key": "fake_key"}
        )
        assert response.status_code == 400
        assert "Unknown provider" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_audio_elevenlabs_api_failure():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        with respx.mock:
            respx.post("https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB").mock(
                return_value=httpx.Response(500, text="ElevenLabs Error")
            )

            response = await ac.post(
                "/api/generate-audio",
                json={"prompt": "Hello", "provider": "elevenlabs"},
                headers={"X-ElevenLabs-Key": "fake_key"}
            )

            assert response.status_code == 500
            # Backend passes through the exception detail or custom error
            assert "Audio generation error" in response.json()["detail"] or "500" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_audio_openai_api_failure():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        with respx.mock:
            respx.post("https://api.openai.com/v1/audio/speech").mock(
                return_value=httpx.Response(500, text="OpenAI Error")
            )

            response = await ac.post(
                "/api/generate-audio",
                json={"prompt": "Hello", "provider": "openai"},
                headers={"X-OpenAI-Key": "fake_key"}
            )

            assert response.status_code == 500
            assert "Audio generation error" in response.json()["detail"] or "500" in response.json()["detail"]
