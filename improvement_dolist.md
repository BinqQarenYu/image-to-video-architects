# Architecture AI Studio - Improvement Do-List

This document tracks the current capabilities of the AI Studio, known UX/UI issues, and the roadmap for ongoing improvements.

## 🟢 Current Capabilities (What Works)
- **Workspaces:** Persistent storage across navigation (History/Library/Studio) using sessionStorage.
- **AI Script Writer:** Generates structured JSON scenes via OpenAI, Gemini 1.5, xAI Grok, OpenRouter, and local Ollama.
- **Local AI Integration:** Ollama endpoint configuration with customizable model tags (e.g., `gpt-oss:20b`).
- **Image Generation:** Scene-specific image generation with automatic failover (OpenAI DALL-E 3 -> Fal.ai).
- **Backend Infrastructure:** Fully hardened MongoDB connection handling (prevents crashes if DB is offline).
- **Video Processing:** FFmpeg integration for compiling scenes, applying global audio, and auto-scaling aspect ratios.
- **Video Export:** Selectable resolutions (240p, 360p, 480p, 720p, 1080p, 4k).
- **Playback & Download:** Auto-looping video player with a dedicated "Save As" OS-level file dialog.
- **API Setup:** Secure API settings modal that saves to the browser's persistent `localStorage`.

## 🟡 High Priority UX/UI Revisions
- [ ] **Image Generation Loading State:** The "Generating Image..." toast can spin forever if an API fails silently. We need an absolute timeout or a visible "Cancel" button on the UI.
- [ ] **Empty States:** The filmstrip and script sidebars look barren when starting a new project. Add helpful placeholder graphics or "Getting Started" text.
- [ ] **Error Handling Visibility:** Display underlying API errors (e.g., "Out of Credits") more clearly in the UI rather than relying solely on tiny pop-up toasts.
- [ ] **Mobile Responsiveness:** The AI Studio dashboard is extremely dense. It needs a responsive layout for smaller laptop screens or tablets.
- [ ] **Progress Indicators:** When hitting "Compile Video," provide a real-time progress bar (polling the backend) instead of a static "Compiling..." spinner, as FFmpeg takes a long time.

## 🟠 Video Generation & Processing Roadmap
- [ ] **Voiceover Ducking (FFmpeg):** Automatically lower the background music volume when the AI Voiceover (ElevenLabs) is speaking.
- [ ] **Auto-Transitions (FFmpeg):** Implement crossfades or dynamic transitions between the generated scene videos.
- [ ] **Whisper Captions:** Integrate OpenAI Whisper to generate `.srt` subtitles and burn them into the final video compile.
- [ ] **Stock Footage Fallback:** If an image fails or the user wants real video, seamlessly pull a query-matched video from Pexels/Pixabay via the backend.
- [ ] **Watermarking:** Add an optional toggle to burn a logo or watermark into the corner of the 4K/1080p export.

## 🔴 Future Scaling & Architecture
- [ ] **Database Migration:** Fully connect and verify the MongoDB `projects` collection so generated videos are saved to an actual User Account, rather than just the session.
- [ ] **Dockerization:** Create a `docker-compose` file to run the FastAPI backend, React frontend, and MongoDB instance simultaneously with one command.
- [ ] **Production Deployment:** Prepare `.env.production` files and secure CORS origins for Vercel (Frontend) and Render/AWS (Backend) deployment.
