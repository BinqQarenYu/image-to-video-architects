# 🎬 LikhaTech AI Modular Studio

> Transform architectural concepts and creative visions into cinematic videos using a modular AI pipeline — powered by your own API keys.

Built with **React** (frontend) and **FastAPI** (backend). Plug in keys for any combination of AI providers to unlock scriptwriting, image generation, voiceover, and AI video animation — all compiled locally with FFmpeg.

---

## 📂 Project Structure

```
image-to-video-architects/
├── frontend/                  # React app (CRA + Tailwind + Radix UI)
├── backend/                   # Python FastAPI server
├── design_guidelines.json     # UI/UX identity: "Obsidian Lens" aesthetic
├── docker-compose.yml         # Full-stack container setup
└── .env.example               # Template for environment variables
```

---

## ✅ Feature Status

### Batch 1 — Settings & State
| Status | Feature |
|:---:|:---|
| ✅ | Tabbed `ApiSettingsModal` (LLMs / Images / Audio / Video tabs) |
| ✅ | Secure API key injection via HTTP headers (never in request body) |

### Batch 2 — Script Engine
| Status | Feature |
|:---:|:---|
| ✅ | Provider support: OpenAI GPT-4o, Google Gemini 2.5, local Ollama |
| ✅ | Structured scene output: `description` + `image_prompt` per scene |

### Batch 3 — Asset Generators
| Status | Feature |
|:---:|:---|
| ✅ | `/api/generate-image`: Fal.ai (Flux) and OpenAI DALL-E 3 |
| ✅ | `/api/generate-audio`: ElevenLabs and OpenAI TTS |
| ✅ | "Generate Image" per scene card, "Generate Voiceover" for full script |

### Batch 4 — Animation Engine
| Status | Feature |
|:---:|:---|
| ✅ | `/api/animate-image`: Minimax (Hailuo) and Runway ML (Gen-3 Alpha Turbo) |
| ✅ | `/api/compile-video`: Full stitching of MP4 clips + audio |
| ✅ | Frontend toggle: **Slideshow (FFmpeg fast)** vs **AI Animated (Premium)** |

### Batch 5 — UI/UX Refinement
| Status | Feature |
|:---:|:---|
| ✅ | Compact smart dropzone & horizontal **Asset Filmstrip** |
| ✅ | **LikhaTech** branding and premium "Obsidian Lens" UI |

### Batch 6 (Latest) — Advanced Controls
| Status | Feature |
|:---:|:---|
| ✅ | **Per-scene animation**: Trigger AI animation directly from script cards |
| ✅ | **Runway ML Integration**: Secondary premium animation provider |
| ✅ | **Stock Footage Fallback**: Integrated Pexels API for architectural B-roll |
| ✅ | **Advanced Export**: Configurable resolution (720p/1080p/4K) and format (MP4/MKV) |

---

## 🚀 Running Locally

### Quick Start (Docker)
```bash
docker-compose up -d --build
# Frontend → http://localhost
# Backend  → http://localhost:8000
```

### Manual Dev Servers
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000

# Frontend
cd frontend
npm start
# Runs on http://localhost:3000
```

---

## 🔑 API Keys Setup

Open **API Settings** in the Studio header. Keys are stored in `localStorage` and injected via HTTP headers.

| Provider | Used For | Get Key |
|:---|:---|:---|
| OpenAI | Script, Images, Audio (TTS) | [platform.openai.com](https://platform.openai.com) |
| Google Gemini | Script generation | [aistudio.google.com](https://aistudio.google.com) |
| Fal.ai | Fast image generation | [fal.ai](https://fal.ai) |
| ElevenLabs | Cinematic voiceover | [elevenlabs.io](https://elevenlabs.io) |
| Minimax | AI video animation | [minimax.chat](https://minimax.chat) |
| **Runway ML** | **Premium Gen-3 animation** | [runwayml.com](https://runwayml.com) |
| **Pexels** | **Stock Video Search** | [pexels.com/api](https://www.pexels.com/api/) |

---

## 📋 Next Steps (Batch 7)

- [ ] **Voiceover Ducking**: Auto-lower background music during narration
- [ ] **Auto-Transitions**: Intelligent scene transition matching
- [ ] **Whisper Captions**: Automatic subtitle generation and overlay
- [ ] **Production Deployment**: SSL setup & cloud containerization

