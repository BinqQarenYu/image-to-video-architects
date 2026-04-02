from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, Header, Depends
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import ffmpeg
from PIL import Image
import shutil
import tempfile
import httpx
import base64
import json
import re
import traceback

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (use safe defaults for local dev)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'image_to_video_db')
try:
    # Set aggressive timeouts so the app doesn't hang if MongoDB is offline
    client = AsyncIOMotorClient(
        mongo_url, 
        serverSelectionTimeoutMS=100, 
        connectTimeoutMS=100,
        socketTimeoutMS=100
    )
    db = client[db_name]
except Exception as e:
    logging.getLogger(__name__).error(f"Could not connect to MongoDB: {e}")
    class _DummyCursor:
        def sort(self, *a, **k): return self
        async def to_list(self, length): return []
    class _DummyColl:
        async def insert_one(self, *a, **k): return None
        def find(self, *a, **k): return _DummyCursor()
        async def delete_one(self, *a, **k):
            class R:
                deleted_count = 0
            return R()
    class _DummyDB(dict):
        def __getitem__(self, n): return _DummyColl()
        def __getattr__(self, n): return _DummyColl()
    db = _DummyDB()

# Directories
UPLOADS_DIR = ROOT_DIR / 'uploads'
VIDEOS_DIR = ROOT_DIR / 'videos'
AUDIO_DIR = ROOT_DIR / 'audio'
UPLOADS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ─── Dependency: extract API keys from request headers ────────────────────────
class AIProviderKeys:
    def __init__(
        self,
        openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
        gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"),
        ollama_endpoint: Optional[str] = Header(None, alias="X-Ollama-Endpoint"),
        fal_key: Optional[str] = Header(None, alias="X-Fal-Key"),
        elevenlabs_key: Optional[str] = Header(None, alias="X-ElevenLabs-Key"),
        minimax_key: Optional[str] = Header(None, alias="X-Minimax-Key"),
        runway_key: Optional[str] = Header(None, alias="X-Runway-Key"),
        pexels_key: Optional[str] = Header(None, alias="X-Pexels-Key"),
    ):
        self.openai = openai_key
        self.gemini = gemini_key
        self.ollama_endpoint = ollama_endpoint or "http://localhost:11434"
        self.fal = fal_key
        self.elevenlabs = elevenlabs_key
        self.minimax = minimax_key
        self.runway = runway_key
        self.pexels = pexels_key

# ─── Models ───────────────────────────────────────────────────────────────────
class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    image_urls: List[str]
    video_url: Optional[str] = None
    prompt: Optional[str] = None
    aspect_ratio: str = "16:9"
    image_duration: float = 3.0
    transition_duration: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    image_urls: List[str]

class VideoGenerateResponse(BaseModel):
    video_url: str
    project_id: str

class ScriptRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    num_scenes: int = 5

class SceneItem(BaseModel):
    description: str
    image_prompt: str

class ScriptResponse(BaseModel):
    scenes: List[SceneItem]

class ImageRequest(BaseModel):
    prompt: str
    providers: Optional[List[str]] = ["fal", "dalle", "gemini"]
    provider: Optional[str] = None # Legacy support

class ImageResponse(BaseModel):
    url: str

class AudioRequest(BaseModel):
    prompt: str
    provider: str = "elevenlabs"

class AudioResponse(BaseModel):
    url: str

class AnimateRequest(BaseModel):
    image_url: str
    prompt: Optional[str] = "Cinematic subtle camera pan, smooth motion."
    provider: str = "minimax"

class AnimateResponse(BaseModel):
    url: str

# ─── Engines ──────────────────────────────────────────────────────────────────
class ScriptEngine:
    @staticmethod
    async def generate_openai(prompt: str, num_scenes: int, api_key: str) -> List[dict]:
        system = (
            "You are a cinematic video director. Given a description, generate a structured video script. "
            f"Return ONLY a valid JSON array of exactly {num_scenes} scene objects. "
            "Each object must have: 'description' (narration text, 1-2 sentences) and "
            "'image_prompt' (detailed Midjourney-style image generation prompt). "
            "No markdown, no explanation — raw JSON array only."
        )
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "gpt-4o", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.8}
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse OpenAI JSON. Raw content: {content}")
                raise ValueError(f"OpenAI returned invalid JSON: {e}")

    @staticmethod
    async def generate_grok(prompt: str, num_scenes: int, api_key: str) -> List[dict]:
        system = (
            "You are a cinematic video director. Given a description, generate a structured video script. "
            f"Return ONLY a valid JSON array of exactly {num_scenes} scene objects. "
            "Each object must have: 'description' (narration text, 1-2 sentences) and "
            "'image_prompt' (detailed Midjourney-style image generation prompt). "
            "No markdown, no explanation — raw JSON array only."
        )
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "grok-beta", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.8}
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse Grok JSON. Raw content: {content}")
                raise ValueError(f"Grok returned invalid JSON: {e}")

    @staticmethod
    async def generate_openrouter(prompt: str, num_scenes: int, api_key: str) -> List[dict]:
        system = (
            "You are a cinematic video director. Given a description, generate a structured video script. "
            f"Return ONLY a valid JSON array of exactly {num_scenes} scene objects. "
            "Each object must have: 'description' (narration text, 1-2 sentences) and "
            "'image_prompt' (detailed Midjourney-style image generation prompt). "
            "No markdown, no explanation — raw JSON array only."
        )
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "anthropic/claude-3.5-sonnet", "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "temperature": 0.8}
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse OpenRouter JSON. Raw content: {content}")
                raise ValueError(f"OpenRouter returned invalid JSON: {e}")

    @staticmethod
    async def generate_gemini(prompt: str, num_scenes: int, api_key: str) -> List[dict]:
        system = (
            f"You are a cinematic video director. Return ONLY a valid JSON array of exactly {num_scenes} scene objects. "
            "Each has 'description' (narration, 1-2 sentences) and 'image_prompt' (Midjourney-style prompt). Raw JSON only."
        )
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
                json={"contents": [{"parts": [{"text": f"{system}\n\nVideo description: {prompt}"}]}]}
            )
            r.raise_for_status()
            content = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse Gemini JSON. Raw content: {content}")
                raise ValueError(f"Gemini returned invalid JSON: {e}")

    @staticmethod
    async def generate_ollama(prompt: str, num_scenes: int, endpoint: str, model: str) -> List[dict]:
        sys_msg = (
            f"You are a cinematic video director. Return ONLY a valid JSON array of {num_scenes} scene objects. "
            "Each has 'description' and 'image_prompt'. Raw JSON only."
        )
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{endpoint}/api/chat",
                json={"model": model, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}], "stream": False}
            )
            r.raise_for_status()
            content = r.json()["message"]["content"].strip()
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to parse Ollama JSON. Raw content: {content}")
                raise ValueError(f"Ollama returned invalid JSON: {e}")


class ImageEngine:
    @staticmethod
    async def generate_fal(prompt: str, api_key: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://fal.run/fal-ai/flux/schnell",
                headers={"Authorization": f"Key {api_key}", "Content-Type": "application/json"},
                json={"prompt": prompt, "image_size": "landscape_16_9", "num_images": 1}
            )
            r.raise_for_status()
            return r.json()["images"][0]["url"]

    @staticmethod
    async def generate_openai(prompt: str, api_key: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "dall-e-3", "prompt": prompt, "n": 1, "size": "1792x1024"}
            )
            r.raise_for_status()
            return r.json()["data"][0]["url"]

    @staticmethod
    async def generate_gemini(prompt: str, api_key: str) -> bytes:
        """Call Gemini Imagen 3 via AI Studio REST API. Returns raw bytes."""
        async with httpx.AsyncClient(timeout=120) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages?key={api_key}"
            r = await client.post(
                url,
                json={
                    "prompt": prompt,
                    "number_of_images": 1
                }
            )
            if r.status_code != 200:
                error_body = r.text
                logger.error(f"Gemini Imagen failed: {r.status_code} - {error_body}")
                r.raise_for_status()
            
            data = r.json()
            if "images" not in data or not data["images"]:
                raise ValueError(f"Gemini Imagen returned no images: {data}")
                
            img_b64 = data["images"][0]["image"]["imageBytes"]
            return base64.b64decode(img_b64)


class VideoEngine:
    @staticmethod
    async def generate_minimax(image_local_path: str, prompt: str, api_key: str) -> str:
        """Upload image → generate video → poll → download → return local path"""
        async with httpx.AsyncClient(timeout=30) as client:
            with open(image_local_path, "rb") as f:
                img_bytes = f.read()
            ext = Path(image_local_path).suffix.lstrip(".")
            upload_r = await client.post(
                "https://api.minimax.chat/v1/files/upload",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": (Path(image_local_path).name, img_bytes, f"image/{ext}")},
                data={"purpose": "video_generation"}
            )
            upload_r.raise_for_status()
            file_id = upload_r.json()["file"]["file_id"]

        async with httpx.AsyncClient(timeout=30) as client:
            gen_r = await client.post(
                "https://api.minimax.chat/v1/video_generation",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "video-01", "prompt": prompt, "first_frame_image": file_id}
            )
            gen_r.raise_for_status()
            task_id = gen_r.json()["task_id"]

        # Poll every 10 seconds, up to 10 minutes
        for _ in range(60):
            await asyncio.sleep(10)
            async with httpx.AsyncClient(timeout=30) as client:
                status_r = await client.get(
                    f"https://api.minimax.chat/v1/query/video_generation?task_id={task_id}",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                status_r.raise_for_status()
                data = status_r.json()
                status = data.get("status")
                if status == "Success":
                    video_url = data["file_id"]
                    # Retrieve download URL
                    retrieve_r = await client.get(
                        f"https://api.minimax.chat/v1/files/retrieve?file_id={video_url}",
                        headers={"Authorization": f"Bearer {api_key}"}
                    )
                    retrieve_r.raise_for_status()
                    download_url = retrieve_r.json()["file"]["download_url"]
                    break
                elif status in ("Fail", "Unknown"):
                    raise HTTPException(status_code=500, detail=f"Minimax generation failed: {data}")
        else:
            raise HTTPException(status_code=504, detail="Minimax video generation timed out")

        # Download the video locally
        local_filename = f"{uuid.uuid4()}.mp4"
        local_path = VIDEOS_DIR / local_filename
        async with httpx.AsyncClient(timeout=120) as client:
            dl = await client.get(download_url)
            dl.raise_for_status()
            local_path.write_bytes(dl.content)

        return f"/api/videos/{local_filename}"

    @staticmethod
    async def generate_runway(image_local_path: str, prompt: str, api_key: str) -> str:
        """Task creation → polling → download → return local path"""
        ext = Path(image_local_path).suffix.lstrip(".")
        with open(image_local_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
        
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "X-Runway-Version": "2024-11-06",
                "Content-Type": "application/json"
            }
            # Task creation
            gen_r = await client.post(
                "https://api.runwayml.com/v1/image_to_video",
                headers=headers,
                json={
                    "model": "gen3a_turbo",
                    "promptImage": f"data:image/{ext};base64,{b64_img}",
                    "promptText": prompt
                }
            )
            gen_r.raise_for_status()
            task_id = gen_r.json()["id"]

        # Polling (Max 10 minutes)
        for _ in range(60):
            await asyncio.sleep(10)
            async with httpx.AsyncClient(timeout=30) as client:
                status_r = await client.get(
                    f"https://api.runwayml.com/v1/tasks/{task_id}",
                    headers=headers
                )
                status_r.raise_for_status()
                data = status_r.json()
                status = data.get("status")
                
                if status == "SUCCEEDED":
                    video_url = data["output"][0]
                    break
                elif status == "FAILED":
                    raise HTTPException(status_code=500, detail=f"Runway generation failed: {data.get('error')}")
        else:
            raise HTTPException(status_code=504, detail="Runway video generation timed out")

        # Download local copy
        local_filename = f"{uuid.uuid4()}.mp4"
        local_path = VIDEOS_DIR / local_filename
        async with httpx.AsyncClient(timeout=120) as client:
            dl = await client.get(video_url)
            dl.raise_for_status()
            local_path.write_bytes(dl.content)

        return f"/api/videos/{local_filename}"

class StockEngine:
    @staticmethod
    async def search_pexels(query: str, api_key: str) -> List[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": api_key},
                params={"query": query, "per_page": 12, "orientation": "landscape"}
            )
            r.raise_for_status()
            data = r.json()
            results = []
            for v in data.get("videos", []):
                # Get the best quality HD/4K file link
                files = v.get("video_files", [])
                files.sort(key=lambda x: x.get("width", 0), reverse=True)
                if files:
                    results.append({
                        "id": v["id"],
                        "url": files[0]["link"],
                        "thumbnail": v["image"],
                        "duration": v["duration"],
                        "width": v["width"],
                        "height": v["height"]
                    })
            return results

# ─── Basic routes ──────────────────────────────────────────────────────────────
@api_router.get("/")
async def root():
    return {"message": "AI Modular Studio API"}

@api_router.post("/upload-images")
async def upload_images(files: List[UploadFile] = File(...)):
    try:
        uploaded_urls = []
        for file in files:
            file_ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOADS_DIR / unique_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_urls.append(f"/api/uploads/{unique_filename}")
        return {"urls": uploaded_urls}
    except Exception as e:
        logger.error(f"Error uploading images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/uploads/{filename}")
async def get_upload(filename: str):
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@api_router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = AUDIO_DIR / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"url": f"/api/audio/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = AUDIO_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(file_path)

@api_router.get("/videos/{filename}")
async def get_video(filename: str):
    file_path = VIDEOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(file_path, media_type="video/mp4")

# ─── AI: Script Generation ────────────────────────────────────────────────────
@api_router.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    request: ScriptRequest, 
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"), 
    x_gemini_key: Optional[str] = Header(None, alias="X-Gemini-Key"), 
    x_grok_key: Optional[str] = Header(None, alias="X-Grok-Key"), 
    x_openrouter_key: Optional[str] = Header(None, alias="X-OpenRouter-Key"), 
    x_ollama_endpoint: Optional[str] = Header(None, alias="X-Ollama-Endpoint"),
    x_ollama_model: Optional[str] = Header(None, alias="X-Ollama-Model")
):
    try:
        if request.provider == "openai":
            if not x_openai_key:
                raise HTTPException(status_code=400, detail="OpenAI key required")
            scenes = await ScriptEngine.generate_openai(request.prompt, request.num_scenes, x_openai_key)
        elif request.provider == "gemini":
            if not x_gemini_key:
                raise HTTPException(status_code=400, detail="Gemini key required")
            scenes = await ScriptEngine.generate_gemini(request.prompt, request.num_scenes, x_gemini_key)
        elif request.provider == "grok":
            if not x_grok_key:
                raise HTTPException(status_code=400, detail="Grok key required")
            scenes = await ScriptEngine.generate_grok(request.prompt, request.num_scenes, x_grok_key)
        elif request.provider == "openrouter":
            if not x_openrouter_key:
                raise HTTPException(status_code=400, detail="OpenRouter key required")
            scenes = await ScriptEngine.generate_openrouter(request.prompt, request.num_scenes, x_openrouter_key)
        elif request.provider == "ollama":
            endpoint = x_ollama_endpoint or "http://localhost:11434"
            model = x_ollama_model or "llama3"
            scenes = await ScriptEngine.generate_ollama(request.prompt, request.num_scenes, endpoint, model)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {request.provider}")
        return ScriptResponse(scenes=[SceneItem(**s) for s in scenes])
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        if status == 429:
            msg = f"{request.provider.capitalize()} API out of credits or rate-limited (429)."
        elif status == 500 and request.provider == "ollama":
            model_name = x_ollama_model or "llama3"
            msg = f"Local Ollama server crashed (500). The model '{model_name}' might be too large for your system's memory."
        else:
            msg = f"{request.provider.capitalize()} returned an error: {status} {e.response.reason_phrase}"
        logger.error(f"Script generation HTTP error: {msg}")
        raise HTTPException(status_code=500, detail=msg)
    except httpx.ReadTimeout:
        msg = f"{request.provider.capitalize()} took too long to respond. The model might be loading or frozen."
        logger.error(f"Script generation timeout: {msg}")
        raise HTTPException(status_code=504, detail=msg)
    except Exception as e:
        logger.error(f"Script generation error details:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── AI: Image Generation ─────────────────────────────────────────────────────
@api_router.post("/generate-image", response_model=ImageResponse)
async def generate_image(request: ImageRequest, keys: AIProviderKeys = Depends()):
    # Support legacy single provider or new fallback list
    providers_to_try = request.providers if request.providers else ([request.provider] if request.provider else ["fal", "dalle", "gemini"])
    
    last_error = None
    image_bytes = None
    remote_url = None

    for provider in providers_to_try:
        try:
            logger.info(f"Attempting image generation with provider: {provider}")
            if provider == "fal":
                if not keys.fal:
                    raise Exception("Fal.ai key missing")
                remote_url = await ImageEngine.generate_fal(request.prompt, keys.fal)
                break # Success

            elif provider == "dalle" or provider == "openai":
                if not keys.openai:
                    raise Exception("OpenAI key missing")
                remote_url = await ImageEngine.generate_openai(request.prompt, keys.openai)
                break # Success
                
            elif provider == "gemini":
                if not keys.gemini:
                    raise Exception("Gemini API key missing")
                image_bytes = await ImageEngine.generate_gemini(request.prompt, keys.gemini)
                break # Success
                
            else:
                logger.warning(f"Unknown image provider: {provider}")
                continue

        except Exception as e:
            error_details = getattr(getattr(e, 'response', None), 'text', str(e))
            logger.warning(f"Image generation failed with {provider}: {e} | Details: {error_details}")
            last_error = e
            continue # Try next provider

    if not remote_url and not image_bytes:
        logger.error(f"All image generation providers failed. Last error: {last_error}")
        raise HTTPException(status_code=500, detail=f"Image generation failed. Ensure API keys are correct. Last error: {str(last_error)}")

    try:
        # If we got a URL, download it first
        if not image_bytes:
            async with httpx.AsyncClient(timeout=60) as client:
                dl = await client.get(remote_url)
                dl.raise_for_status()
                image_bytes = dl.content
                
        filename = f"{uuid.uuid4()}.jpg"
        await asyncio.to_thread((UPLOADS_DIR / filename).write_bytes, image_bytes)
        return ImageResponse(url=f"/api/uploads/{filename}")
    except Exception as e:
        logger.error(f"Failed to cache generated image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── AI: Audio Generation ─────────────────────────────────────────────────────
@api_router.post("/generate-audio", response_model=AudioResponse)
async def generate_audio(request: AudioRequest, x_elevenlabs_key: Optional[str] = Header(None, alias="X-ElevenLabs-Key"), x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key")):
    try:
        if request.provider == "elevenlabs":
            if not x_elevenlabs_key:
                raise HTTPException(status_code=400, detail="ElevenLabs key required")
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB",
                    headers={"xi-api-key": x_elevenlabs_key, "Content-Type": "application/json"},
                    json={"text": request.prompt, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
                )
                r.raise_for_status()
                audio_bytes = r.content
        elif request.provider == "openai":
            if not x_openai_key:
                raise HTTPException(status_code=400, detail="OpenAI key required")
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {x_openai_key}", "Content-Type": "application/json"},
                    json={"model": "tts-1", "input": request.prompt, "voice": "onyx"}
                )
                r.raise_for_status()
                audio_bytes = r.content
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {request.provider}")

        filename = f"{uuid.uuid4()}.mp3"
        await asyncio.to_thread((AUDIO_DIR / filename).write_bytes, audio_bytes)
        return AudioResponse(url=f"/api/audio/{filename}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── AI: Image → Video (Minimax) ──────────────────────────────────────────────
@api_router.post("/animate-image", response_model=AnimateResponse)
async def animate_image(request: AnimateRequest, keys: AIProviderKeys = Depends()): # Using keys dependency
    try:
        filename = request.image_url.split("/")[-1]
        local_path = UPLOADS_DIR / filename
        if not local_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {filename}")
        
        if request.provider == "minimax":
            if not keys.minimax:
                raise HTTPException(status_code=400, detail="Minimax API key required")
            video_url = await VideoEngine.generate_minimax(str(local_path), request.prompt, keys.minimax)
        elif request.provider == "runway":
            if not keys.runway:
                raise HTTPException(status_code=400, detail="Runway API key required")
            video_url = await VideoEngine.generate_runway(str(local_path), request.prompt, keys.runway)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown animation provider: {request.provider}")
            
        return AnimateResponse(url=video_url)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Animation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── Compile video clips (AI mode) ────────────────────────────────────────────
@api_router.post("/compile-video", response_model=VideoGenerateResponse)
async def compile_video(
    video_urls: List[str] = Form(...),
    audio_url: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
):
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            concat_file = tmp / "concat.txt"
            lines = []
            for vurl in video_urls:
                filename = vurl.split("/")[-1]
                vpath = VIDEOS_DIR / filename
                if not vpath.exists():
                    raise HTTPException(status_code=404, detail=f"Video not found: {filename}")
                lines.append(f"file '{vpath}'\n")
            await asyncio.to_thread(concat_file.write_text, "".join(lines))

            output_filename = f"{uuid.uuid4()}.mp4"
            output_path = VIDEOS_DIR / output_filename

            if audio_url:
                audio_filename = audio_url.split("/")[-1]
                audio_path = AUDIO_DIR / audio_filename
                if not audio_path.exists():
                    raise HTTPException(status_code=404, detail="Audio file not found")
                video_in = ffmpeg.input(str(concat_file), format="concat", safe=0)
                audio_in = ffmpeg.input(str(audio_path))
                stream = (
                    ffmpeg
                    .output(video_in, audio_in, str(output_path), vcodec="copy", acodec="aac", shortest=None)
                    .overwrite_output()
                )
                await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))
            else:
                stream = (
                    ffmpeg
                    .input(str(concat_file), format="concat", safe=0)
                    .output(str(output_path), vcodec="copy")
                    .overwrite_output()
                )
                await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))

            project = Project(
                name=f"AI Animated — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                image_urls=video_urls,
                video_url=f"/api/videos/{output_filename}",
                prompt=prompt,
            )
            project_dict = project.model_dump()
            project_dict['created_at'] = project_dict['created_at'].isoformat()
            project_dict['updated_at'] = project_dict['updated_at'].isoformat()
            try:
                await db.projects.insert_one(project_dict)
            except Exception as db_err:
                logger.warning(f"Failed to save project to MongoDB (is it running?): {db_err}")

            return VideoGenerateResponse(video_url=f"/api/videos/{output_filename}", project_id=project.id)

    except ffmpeg.Error as e:
        raise HTTPException(status_code=500, detail=f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Compile video error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── FFmpeg slideshow ─────────────────────────────────────────────────────────
async def _prepare_image(idx: int, url: str, width: int, height: int, temp_path: Path):
    """Helper to process and resize images in a separate thread."""
    filename = url.split('/')[-1]
    source_path = UPLOADS_DIR / filename
    if not source_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {filename}")

    def _process():
        img = Image.open(source_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Using BILINEAR for ~60-75% speedup over LANCZOS with minimal quality loss for video
        img = img.resize((width, height), Image.Resampling.BILINEAR)
        processed_path = temp_path / f"image_{idx:04d}.jpg"
        img.save(processed_path, 'JPEG', quality=95)
        return str(processed_path)

    return await asyncio.to_thread(_process)


@api_router.post("/generate-video", response_model=VideoGenerateResponse)
async def generate_video(
    image_urls: List[str] = Form(...),
    transition_duration: float = Form(1.0),
    image_duration: float = Form(3.0),
    aspect_ratio: str = Form("16:9"),
    prompt: Optional[str] = Form(None),
    audio_url: Optional[str] = Form(None),
    quality: str = Form("1080p"),
    format: str = Form("mp4"),
):
    try:
        if not image_urls:
            raise HTTPException(status_code=400, detail="No images provided")

        aspect_map = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "21:9": (2560, 1080)}
        width, height = aspect_map.get(aspect_ratio, (1920, 1080))

        # Apply resolution scaling based on quality (target the short edge)
        short_edge = min(width, height)
        if quality == "240p":
            scale = 240 / short_edge
        elif quality == "360p":
            scale = 360 / short_edge
        elif quality == "480p":
            scale = 480 / short_edge
        elif quality == "720p":
            scale = 720 / short_edge
        elif quality == "4k":
            scale = 2160 / short_edge
        else: # 1080p
            scale = 1080 / short_edge

        width, height = int(width * scale), int(height * scale)
        
        # Ensure even dimensions for FFmpeg
        width = (width // 2) * 2
        height = (height // 2) * 2

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Process all images in parallel for significant performance boost
            tasks = [_prepare_image(idx, url, width, height, temp_path) for idx, url in enumerate(image_urls)]
            processed_images = await asyncio.gather(*tasks)

            video_id = str(uuid.uuid4())
            output_ext = "mp4" if format == "mp4" else "mkv"
            output_filename = f"{video_id}.{output_ext}"
            output_path = VIDEOS_DIR / output_filename

            if len(processed_images) == 1:
                stream = (
                    ffmpeg
                    .input(processed_images[0], loop=1, t=image_duration)
                    .filter('zoompan', z='min(zoom+0.0015,1.5)', d=int(image_duration * 25), s=f'{width}x{height}')
                    .output(str(output_path), vcodec='libx264', pix_fmt='yuv420p', r=25, preset='ultrafast', crf=23)
                    .overwrite_output()
                )
                await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))
            else:
                concat_file = temp_path / "concat_list.txt"

                def _write_concat_file():
                    with open(concat_file, 'w') as f:
                        for img_path in processed_images:
                            f.write(f"file '{img_path}'\n")
                            f.write(f"duration {image_duration}\n")
                        f.write(f"file '{processed_images[-1]}'\n")

                await asyncio.to_thread(_write_concat_file)

                video_stream = ffmpeg.input(str(concat_file), format='concat', safe=0).filter('fps', fps=25).filter('format', pix_fmts='yuv420p')

                if audio_url:
                    audio_filename = audio_url.split("/")[-1]
                    audio_path = AUDIO_DIR / audio_filename
                    if audio_path.exists():
                        audio_stream = ffmpeg.input(str(audio_path))
                        stream = (
                            ffmpeg
                            .output(video_stream, audio_stream, str(output_path), vcodec='libx264', acodec='aac', preset='ultrafast', crf=23, shortest=None)
                            .overwrite_output()
                        )
                        await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))
                    else:
                        stream = (
                            video_stream
                            .output(str(output_path), vcodec='libx264', preset='ultrafast', crf=23)
                            .overwrite_output()
                        )
                        await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))
                else:
                    stream = (
                        video_stream
                        .output(str(output_path), vcodec='libx264', preset='ultrafast', crf=23)
                        .overwrite_output()
                    )
                    await asyncio.to_thread(lambda: stream.run(capture_stdout=True, capture_stderr=True))

            project = Project(
                name=f"Project {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                image_urls=image_urls,
                video_url=f"/api/videos/{output_filename}",
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                image_duration=image_duration,
                transition_duration=transition_duration,
            )
            project_dict = project.model_dump()
            project_dict['created_at'] = project_dict['created_at'].isoformat()
            project_dict['updated_at'] = project_dict['updated_at'].isoformat()
            try:
                await db.projects.insert_one(project_dict)
            except Exception as db_err:
                logger.warning(f"Failed to save project to MongoDB (is it running?): {db_err}")

            return VideoGenerateResponse(video_url=f"/api/videos/{output_filename}", project_id=project.id)

    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        raise HTTPException(status_code=500, detail="Video generation failed")
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── Projects CRUD ────────────────────────────────────────────────────────────
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    try:
        projects = await db.projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
        for p in projects:
            if isinstance(p.get('created_at'), str):
                p['created_at'] = datetime.fromisoformat(p['created_at'])
            if isinstance(p.get('updated_at'), str):
                p['updated_at'] = datetime.fromisoformat(p['updated_at'])
        return projects
    except Exception as e:
        logger.warning(f"Could not load projects from MongoDB: {e}")
        return []

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

# ─── Stock Media ──────────────────────────────────────────────────────────────
@api_router.get("/stock-videos")
async def get_stock_videos(query: str, x_pexels_key: Optional[str] = Header(None, alias="X-Pexels-Key")):
    if not x_pexels_key:
        raise HTTPException(status_code=400, detail="Pexels API key required")
    try:
        videos = await StockEngine.search_pexels(query, x_pexels_key)
        return {"videos": videos}
    except Exception as e:
        logger.error(f"Stock search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── App setup ────────────────────────────────────────────────────────────────
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        client.close()
    except Exception:
        pass