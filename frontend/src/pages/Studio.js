import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, X, Play, ArrowLeft, Download, Loader2, Settings, Sparkles, Film, Music, PlusCircle, Database } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Slider } from '../components/ui/slider';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/ui/tooltip';
import { toast } from 'sonner';
import axios from 'axios';
import { ApiSettingsModal } from '../components/ApiSettingsModal';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const useSessionState = (key, defaultValue) => {
  const [state, setState] = useState(() => {
    try {
      const stored = sessionStorage.getItem(key);
      return stored ? JSON.parse(stored) : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  useEffect(() => {
    try {
      sessionStorage.setItem(key, JSON.stringify(state));
    } catch (e) {
      console.warn("Could not save to sessionStorage", e);
    }
  }, [key, state]);

  return [state, setState];
};

export const Studio = () => {
  const navigate = useNavigate();
  const [images, setImages] = useSessionState('studio_images', []);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [videoUrl, setVideoUrl] = useSessionState('studio_videoUrl', null);
  const [dragActive, setDragActive] = useState(false);
  const [prompt, setPrompt] = useSessionState('studio_prompt', '');
  const [imageDuration, setImageDuration] = useSessionState('studio_imageDuration', 3);
  const [transitionDuration, setTransitionDuration] = useSessionState('studio_transitionDuration', 1);
  const [transitionStyle, setTransitionStyle] = useSessionState('studio_transitionStyle', 'fade');
  const [aspectRatio, setAspectRatio] = useSessionState('studio_aspectRatio', '16:9');
  const [audioFile, setAudioFile] = useState(null);
  const [audioUrl, setAudioUrl] = useSessionState('studio_audioUrl', null);
  const [uploadingAudio, setUploadingAudio] = useState(false);
  const [isApiModalOpen, setIsApiModalOpen] = useState(false);

  // Script Engine State
  const [scriptScenes, setScriptScenes] = useSessionState('studio_scriptScenes', []);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [llmProvider, setLlmProvider] = useSessionState('studio_llmProvider', 'ollama');

  // Render Mode: 'slideshow' | 'animated'
  const [renderMode, setRenderMode] = useSessionState('studio_renderMode', 'slideshow');
  const [animationProvider, setAnimationProvider] = useSessionState('studio_animationProvider', 'minimax'); // 'minimax' | 'runway'

  // Stock Media State
  const [stockQuery, setStockQuery] = useSessionState('studio_stockQuery', '');
  const [stockResults, setStockResults] = useSessionState('studio_stockResults', []);
  const [isSearchingStock, setIsSearchingStock] = useState(false);

  // Export Settings
  const [exportQuality, setExportQuality] = useSessionState('studio_exportQuality', '1080p'); // '720p' | '1080p' | '4k'
  const [exportFormat, setExportFormat] = useSessionState('studio_exportFormat', 'mp4'); // 'mp4' | 'mkv'

  // ── Drag & drop ───────────────────────────────────────────────────────────
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    // Check if the dropped item is coming from our internal AI Script cards
    const source = e.dataTransfer.getData('source');
    if (source === 'script-writer') {
      const imageUrl = e.dataTransfer.getData('imageUrl');
      if (imageUrl) {
        setImages(prev => [...prev, {
          id: `script-img-${Date.now()}-${Math.random()}`,
          url: imageUrl,
          videoUrl: null,
        }]);
        toast.success("AI Image added to video rack!");
      }
      return;
    }

    // Otherwise, handle regular OS-level file drops
    const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    if (files.length > 0) uploadImages(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) uploadImages(files);
  };

  const uploadImages = async (files) => {
    setUploading(true);
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      const response = await axios.post(`${API}/upload-images`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      const newImages = response.data.urls.map(url => ({
        id: `${Date.now()}-${Math.random()}`,
        url: `${BACKEND_URL}${url}`,
        videoUrl: null,
      }));
      setImages(prev => [...prev, ...newImages]);
      toast.success(`${files.length} image${files.length > 1 ? 's' : ''} uploaded!`);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload images');
    } finally {
      setUploading(false);
    }
  };

  const removeImage = (id) => setImages(prev => prev.filter(img => img.id !== id));

  const reorderImages = (fromIndex, toIndex) => {
    setImages(prev => {
      const updated = [...prev];
      const [moved] = updated.splice(fromIndex, 1);
      updated.splice(toIndex, 0, moved);
      return updated;
    });
  };

  // ── Audio ─────────────────────────────────────────────────────────────────
  const handleAudioSelect = async (e) => {
    const file = e.target.files[0];
    if (file && (file.type.includes('audio/mpeg') || file.type.includes('audio/wav'))) {
      setAudioFile(file);
      await uploadAudio(file);
    } else {
      toast.error('Please upload an MP3 or WAV file');
    }
  };

  const uploadAudio = async (file) => {
    setUploadingAudio(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post(`${API}/upload-audio`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setAudioUrl(response.data.url);
      toast.success('Audio uploaded!');
    } catch (error) {
      toast.error('Failed to upload audio');
      setAudioFile(null);
    } finally {
      setUploadingAudio(false);
    }
  };

  const removeAudio = () => { setAudioFile(null); setAudioUrl(null); };

  // ── Video generation ──────────────────────────────────────────────────────
  const handleGenerateVideo = async () => {
    if (images.length === 0) { toast.error('Please upload at least one image'); return; }

    if (renderMode === 'animated') {
      const missing = images.filter(img => !img.videoUrl);
      if (missing.length > 0) {
        toast.error('Some scenes are missing animations. Animate all images first, or switch to Slideshow mode.');
        return;
      }
    }

    setGenerating(true);
    setVideoUrl(null);

    try {
      const formData = new FormData();

      if (renderMode === 'animated') {
        images.forEach(img => formData.append('video_urls', img.videoUrl.replace(BACKEND_URL, '')));
        if (audioUrl) formData.append('audio_url', audioUrl);
        if (prompt.trim()) formData.append('prompt', prompt);
        const response = await axios.post(`${API}/compile-video`, formData, { timeout: 120000 });
        const finalUrl = `${BACKEND_URL}${response.data.video_url}`;
        console.log("COMPILED URL:", finalUrl, "Raw:", response.data);
        setVideoUrl(finalUrl);
        toast.success('AI Animated video compiled!');
      } else {
        images.forEach(img => formData.append('image_urls', img.url.replace(BACKEND_URL, '')));
        formData.append('transition_duration', transitionDuration.toString());
        formData.append('transition_style', transitionStyle);
        formData.append('image_duration', imageDuration.toString());
        formData.append('aspect_ratio', aspectRatio);
        formData.append('quality', exportQuality);
        formData.append('format', exportFormat);
        if (prompt.trim()) formData.append('prompt', prompt);
        if (audioUrl) formData.append('audio_url', audioUrl);
        const response = await axios.post(`${API}/generate-video`, formData, { timeout: 120000 });
        const finalUrl = `${BACKEND_URL}${response.data.video_url}`;
        console.log("GENERATED URL:", finalUrl, "Raw:", response.data);
        setVideoUrl(finalUrl);
        toast.success('Video generated!');
      }
    } catch (error) {
      console.error('Generation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate video');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!videoUrl) return;

    try {
      if (window.showSaveFilePicker) {
        toast.info("Preparing video for save...");
        const response = await fetch(videoUrl);
        const blob = await response.blob();

        const handle = await window.showSaveFilePicker({
          suggestedName: 'studio-video.mp4',
          types: [{
            description: 'MP4 Video',
            accept: { 'video/mp4': ['.mp4'] },
          }],
        });

        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        toast.success("Video saved successfully!");
      } else {
        // Fallback for older browsers
        const link = document.createElement('a');
        link.href = videoUrl;
        link.download = 'studio-video.mp4';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error("Save error:", error);
        toast.error("Failed to save video.");
      }
    }
  };

  // ── Script Engine ─────────────────────────────────────────────────────────
  const handleGenerateScript = async () => {
    if (!prompt.trim()) { toast.error('Enter a description first'); return; }

    const keyMap = {
      openai: 'openai_api_key',
      gemini: 'gemini_api_key',
      grok: 'grok_api_key',
      openrouter: 'openrouter_api_key'
    };
    if (llmProvider !== 'ollama') {
      const key = localStorage.getItem(keyMap[llmProvider] || '');
      if (!key) { toast.error(`Set your ${llmProvider.toUpperCase()} key in API Settings first`); setIsApiModalOpen(true); return; }
    }

    setIsGeneratingScript(true);
    try {
      const headers = { 'Content-Type': 'application/json' };
      const openaiKey = localStorage.getItem('openai_api_key');
      const geminiKey = localStorage.getItem('gemini_api_key');
      const grokKey = localStorage.getItem('grok_api_key');
      const openRouterKey = localStorage.getItem('openrouter_api_key');
      const ollamaEp = localStorage.getItem('ollama_endpoint');
      const ollamaModel = localStorage.getItem('ollama_model');

      if (openaiKey) headers['X-OpenAI-Key'] = openaiKey;
      if (geminiKey) headers['X-Gemini-Key'] = geminiKey;
      if (grokKey) headers['X-Grok-Key'] = grokKey;
      if (openRouterKey) headers['X-OpenRouter-Key'] = openRouterKey;
      if (ollamaEp) headers['X-Ollama-Endpoint'] = ollamaEp;
      if (ollamaModel) headers['X-Ollama-Model'] = ollamaModel;

      const response = await axios.post(`${API}/generate-script`, { prompt, provider: llmProvider }, { headers });
      if (response.data?.scenes) {
        setScriptScenes(response.data.scenes);
        toast.success('Script generated!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate script');
    } finally {
      setIsGeneratingScript(false);
    }
  };

  // ── Per-scene image generation ────────────────────────────────────────────
  const generateSceneImage = async (sceneId, imagePrompt) => {
    const providers = ['fal', 'dalle', 'gemini']; // Fallback chain: Fal -> OpenAI -> Gemini
    const falKey = localStorage.getItem('fal_api_key');
    const openaiKey = localStorage.getItem('openai_api_key');
    const geminiKey = localStorage.getItem('gemini_api_key');

    if (!openaiKey && !falKey && !geminiKey) {
      toast.error('Set your OpenAI, Fal.ai, or Gemini API key in Settings');
      setIsApiModalOpen(true);
      return;
    }

    const toastId = toast.loading(`Generating image for Scene ${sceneId}...`);
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (falKey) headers['X-Fal-Key'] = falKey;
      if (openaiKey) headers['X-OpenAI-Key'] = openaiKey;
      if (geminiKey) headers['X-Gemini-Key'] = geminiKey;

      const response = await axios.post(`${API}/generate-image`, { prompt: imagePrompt, providers: providers }, { headers });
      if (response.data?.url) {
        const fullUrl = `${BACKEND_URL}${response.data.url}`;
        // Store image DIRECTLY inside the script scene, completely isolating it from the top video rack
        setScriptScenes(prev => {
          const updated = [...prev];
          updated[sceneId - 1] = { ...updated[sceneId - 1], imageUrl: fullUrl };
          return updated;
        });
        toast.success(`Scene ${sceneId} image generated!`, { id: toastId });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate image', { id: toastId });
    }
  };

  // ── Global voiceover ──────────────────────────────────────────────────────
  const generateGlobalAudio = async () => {
    if (scriptScenes.length === 0) { toast.error('Generate a script first'); return; }
    const provider = 'elevenlabs';
    const apiKey = localStorage.getItem('elevenlabs_api_key');
    if (!apiKey) { toast.error('Set your ElevenLabs key in Settings'); setIsApiModalOpen(true); return; }

    const toastId = toast.loading('Generating voiceover...');
    try {
      const masterScript = scriptScenes.map(s => s.description).join('. ');
      const headers = { 'Content-Type': 'application/json', 'X-ElevenLabs-Key': apiKey };
      const response = await axios.post(`${API}/generate-audio`, { prompt: masterScript, provider }, { headers });
      if (response.data?.url) {
        setAudioFile(new File([''], `voiceover_${Date.now()}.mp3`, { type: 'audio/mpeg' }));
        setAudioUrl(response.data.url);
        toast.success('Voiceover generated and attached!', { id: toastId });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate audio', { id: toastId });
    }
  };

  // ── Minimax per-scene animation ───────────────────────────────────────────
  const generateSceneVideo = async (imageObj) => {
    const apiKey = localStorage.getItem('minimax_api_key');
    if (!apiKey) { toast.error('Set your Minimax API key in Settings'); setIsApiModalOpen(true); return; }
    if (!imageObj?.url) { toast.error('Scene needs an image first'); return; }

    const toastId = toast.loading('Animating with Minimax (takes a few minutes)...');
    try {
      const headers = {
        'Content-Type': 'application/json',
        'X-Minimax-Key': localStorage.getItem('minimax_api_key'),
        'X-Runway-Key': localStorage.getItem('runway_api_key')
      };
      const response = await axios.post(`${API}/animate-image`, {
        image_url: imageObj.url.replace(BACKEND_URL, ''),
        provider: animationProvider,
      }, { headers, timeout: 660000 });

      if (response.data?.url) {
        const fullUrl = `${BACKEND_URL}${response.data.url}`;
        setImages(prev => prev.map(img => img.id === imageObj.id ? { ...img, videoUrl: fullUrl } : img));
        toast.success('Scene animated!', { id: toastId });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to animate scene', { id: toastId });
    }
  };

  // ── Stock Media ────────────────────────────────────────────────────────────
  const handleSearchStock = async () => {
    if (!stockQuery.trim()) return;
    const apiKey = localStorage.getItem('pexels_api_key');
    if (!apiKey) { toast.error('Set your Pexels API key in Settings'); setIsApiModalOpen(true); return; }

    setIsSearchingStock(true);
    try {
      const response = await axios.get(`${API}/stock-videos`, {
        params: { query: stockQuery },
        headers: { 'X-Pexels-Key': apiKey }
      });
      setStockResults(response.data?.videos || []);
      if (response.data?.videos?.length === 0) toast.info('No stock footage found');
    } catch (error) {
      toast.error('Failed to search stock footage');
    } finally {
      setIsSearchingStock(false);
    }
  };

  const importStockVideo = (video) => {
    setImages(prev => [...prev, {
      id: `${Date.now()}-${Math.random()}`,
      url: video.thumbnail,
      videoUrl: video.url
    }]);
    toast.success('Stock video imported!');
  };

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-[#0A0A0A]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button data-testid="back-btn" aria-label="Back to home" variant="ghost" onClick={() => navigate('/')} className="text-white/60 hover:text-white hover:bg-white/10">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <h1 className="text-2xl font-bold font-['Manrope']">Video Studio</h1>
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={() => navigate('/projects')} variant="outline" className="rounded-full border border-white/20 bg-transparent text-white hover:bg-white hover:text-black transition-colors">
              <Film className="w-4 h-4 mr-2" />Library
            </Button>
            <Button onClick={() => setIsApiModalOpen(true)} variant="outline" className="rounded-full border border-white/20 bg-transparent text-white hover:bg-white hover:text-black transition-colors">
              <Settings className="w-4 h-4 mr-2" />API Settings
            </Button>
            {videoUrl && (
              <Button data-testid="download-btn" onClick={handleDownload} variant="outline" className="rounded-full border border-white/20 bg-transparent text-white hover:bg-white hover:text-black">
                <Download className="w-4 h-4 mr-2" />Download
              </Button>
            )}
            <Tooltip>
              <TooltipTrigger asChild>
                <span className={images.length === 0 ? "cursor-not-allowed" : ""}>
                  <Button
                    data-testid="generate-video-btn"
                    onClick={handleGenerateVideo}
                    disabled={images.length === 0 || generating}
                    className="rounded-full font-semibold bg-[#FF4D00] text-white hover:bg-[#FF4D00]/90 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {generating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Generating...</> : <><Play className="w-4 h-4 mr-2" />Generate Video</>}
                  </Button>
                </span>
              </TooltipTrigger>
              {images.length === 0 && (
                <TooltipContent>
                  <p>Add at least one image to generate video</p>
                </TooltipContent>
              )}
            </Tooltip>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* ── LEFT PANEL ──────────────────────────────────────────────── */}
          <div className="space-y-4">

            {/* STICKY ASSET FILMSTRIP */}
            <div className="sticky top-[72px] z-40 bg-[#050505]/95 backdrop-blur-xl pt-2 pb-3">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-bold font-['Manrope'] flex items-center gap-2">
                  Scenes
                  {images.length > 0 && (
                    <span className="text-xs font-mono bg-white/10 text-white/60 px-2 py-0.5 rounded-full">{images.length}</span>
                  )}
                  {renderMode === 'animated' && images.length > 0 && (
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 capitalize">{animationProvider}</span>
                  )}
                </h2>

                {/* Compact upload button */}
                <div
                  data-testid="dropzone"
                  onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                  onClick={() => document.getElementById('file-input').click()}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border cursor-pointer text-xs font-medium transition-all duration-200 ${dragActive ? 'border-[#FF4D00] bg-[#FF4D00]/20 text-[#FF4D00]' : 'border-white/15 bg-white/5 text-white/60 hover:border-[#FF4D00]/50 hover:text-[#FF4D00] hover:bg-[#FF4D00]/10'}`}
                >
                  <input id="file-input" type="file" multiple accept="image/*" onChange={handleFileSelect} className="hidden" />
                  {uploading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
                  {images.length === 0 ? 'Upload Images' : 'Add More'}
                </div>
              </div>

              {images.length === 0 ? (
                /* Empty drop zone */
                <div
                  onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                  onClick={() => document.getElementById('file-input').click()}
                  className={`border-2 border-dashed rounded-xl flex flex-col items-center justify-center h-36 cursor-pointer transition-all duration-300 ${dragActive ? 'border-[#FF4D00] bg-[#FF4D00]/10' : 'border-white/10 bg-white/5 hover:border-[#FF4D00]/40'}`}
                >
                  {uploading ? (
                    <><Loader2 className="w-8 h-8 text-[#FF4D00] animate-spin mb-2" /><p className="text-sm text-white/60">Uploading...</p></>
                  ) : (
                    <>
                      <div className="w-10 h-10 rounded-full bg-[#FF4D00]/10 flex items-center justify-center mb-2">
                        <Upload className="w-5 h-5 text-[#FF4D00]" />
                      </div>
                      <p className="text-sm font-medium text-white/70">Drop images here or click to browse</p>
                      <p className="text-xs text-white/30 mt-1">JPG · PNG · WEBP</p>
                    </>
                  )}
                </div>
              ) : (
                /* Horizontal filmstrip */
                <div className="flex gap-2 overflow-x-auto pb-1 custom-scrollbar">
                  {images.map((img, index) => (
                    <div
                      key={img.id}
                      data-testid={`image-preview-${index}`}
                      className={`relative flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border transition-all duration-200 group cursor-grab active:cursor-grabbing ${renderMode === 'animated' && !img.videoUrl ? 'border-amber-500/50' : 'border-white/10 hover:border-[#FF4D00]'}`}
                      draggable
                      onDragStart={(e) => e.dataTransfer.setData('index', index)}
                      onDragOver={(e) => e.preventDefault()}
                      onDrop={(e) => { e.preventDefault(); reorderImages(parseInt(e.dataTransfer.getData('index')), index); }}
                    >
                      <img
                        src={img.url} alt={`Scene ${index + 1}`}
                        className={`w-full h-full object-cover ${renderMode === 'animated' && !img.videoUrl ? 'opacity-60 grayscale' : ''}`}
                      />
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent px-1.5 py-1">
                        <span className="text-[10px] font-['JetBrains_Mono'] text-white/80">#{index + 1}</span>
                      </div>
                      {img.videoUrl && (
                        <div className="absolute top-1 left-1 px-1 py-0.5 flex items-center gap-0.5 rounded bg-indigo-500/90 text-[8px] font-bold text-white">
                          <Film className="w-2.5 h-2.5" />AI
                        </div>
                      )}
                      {/* Animate button (visible in animated mode) */}
                      {renderMode === 'animated' && !img.videoUrl && (
                        <button
                          onClick={() => generateSceneVideo(img)}
                          className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-white font-bold gap-1"
                        >
                          <div className="w-8 h-8 rounded-full bg-[#FF4D00] flex items-center justify-center shadow-lg">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          Animate
                        </button>
                      )}
                      <button
                        data-testid={`remove-image-${index}`}
                        aria-label="Remove image"
                        onClick={() => removeImage(img.id)}
                        className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/80 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[#FF4D00]"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* END FILMSTRIP */}

            {/* AI Script Writer */}
            <div className="glass-panel rounded-2xl p-6 space-y-4 mb-6">
              <div className="flex items-center justify-between">
                <Label htmlFor="prompt" className="flex items-center gap-2 text-white/80">
                  <Sparkles className="w-4 h-4 text-[#FF4D00]" />AI Script Writer
                </Label>
                <Select value={llmProvider} onValueChange={setLlmProvider}>
                  <SelectTrigger className="w-[175px] h-8 text-xs bg-[#111] border-white/10 text-white rounded-lg">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#1A1A1A] border-white/10 text-white text-xs">
                    <SelectItem value="openai">OpenAI (GPT-4o)</SelectItem>
                    <SelectItem value="gemini">Google Gemini 1.5</SelectItem>
                    <SelectItem value="grok">xAI Grok Beta</SelectItem>
                    <SelectItem value="openrouter">OpenRouter (Claude 3.5)</SelectItem>
                    <SelectItem value="ollama">Ollama (Local)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="relative">
                <Textarea
                  id="prompt"
                  data-testid="video-prompt"
                  placeholder="Describe your vision (e.g. 'A cinematic tour of a modern concrete mansion in a pine forest...')"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="bg-[#111] border-white/10 focus:border-[#FF4D00]/50 text-white placeholder:text-white/30 rounded-lg min-h-[96px] resize-none pb-12"
                />
                <Button
                  onClick={handleGenerateScript}
                  disabled={isGeneratingScript || !prompt.trim()}
                  className="absolute bottom-2 right-2 h-8 text-xs bg-white/10 hover:bg-white/20 text-white rounded-md"
                >
                  {isGeneratingScript ? <Loader2 className="w-3 h-3 mr-1.5 animate-spin" /> : <Sparkles className="w-3 h-3 mr-1.5" />}
                  Generate Script
                </Button>
              </div>

              {/* Script scenes */}
              {scriptScenes.length > 0 && (
                <div className="space-y-3 mt-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-white/80">Generated Scenes ({scriptScenes.length})</h4>
                    <Button onClick={generateGlobalAudio} className="h-7 text-[10px] bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/40 border border-indigo-500/30 rounded">
                      <Music className="w-3 h-3 mr-1" />Generate Voiceover
                    </Button>
                  </div>
                  <div className="max-h-[320px] overflow-y-auto pr-1 custom-scrollbar space-y-2">
                    {scriptScenes.map((scene, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-[#111]/50 border border-white/5 relative group hover:border-[#FF4D00]/30 transition-all">
                        <div className="flex justify-between items-start mb-2">
                          <span className="text-xs font-bold text-[#FF4D00] flex items-center gap-1.5">
                            <div className="w-4 h-4 rounded bg-[#FF4D00]/20 flex items-center justify-center text-[9px]">{idx + 1}</div>Scene
                          </span>
                          <div className="flex items-center gap-1.5">
                            {scene.imageUrl ? (
                              <div className="flex items-center gap-2 mr-2">
                                <img
                                  src={scene.imageUrl}
                                  alt={`Scene ${idx + 1}`}
                                  className="w-8 h-8 rounded object-cover cursor-grab active:cursor-grabbing border border-[#FF4D00]/50"
                                  draggable
                                  onDragStart={(e) => {
                                    // Set data so we can drag this generated image UP to the manual rack
                                    e.dataTransfer.setData('source', 'script-writer');
                                    e.dataTransfer.setData('imageUrl', scene.imageUrl);
                                  }}
                                  title="Drag me to the top rack to use in your video!"
                                />
                                <span className="text-[10px] text-white/50 italic">Drag to rack ⬆️</span>
                              </div>
                            ) : (
                              <Button
                                onClick={() => generateSceneImage(idx + 1, scene.image_prompt)}
                                className="h-6 text-[10px] bg-[#FF4D00]/20 text-[#FF4D00] hover:bg-[#FF4D00]/40 border border-[#FF4D00]/30 rounded opacity-0 group-hover:opacity-100 transition-all font-mono"
                              >
                                <Sparkles className="w-3 h-3 mr-1" />Generate Image
                              </Button>
                            )}
                            <Button variant="ghost" aria-label="Remove scene" onClick={() => setScriptScenes(scriptScenes.filter((_, i) => i !== idx))} className="h-6 w-6 p-0 text-white/30 hover:text-red-400 hover:bg-red-400/10 opacity-0 group-hover:opacity-100 transition-all rounded">
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                        </div>
                        <p className="text-xs text-white/80 mb-2 leading-relaxed">{scene.description}</p>
                        <div className="bg-black/40 p-2 rounded text-[10px] text-white/40 font-mono break-words border border-white/5">
                          <span className="text-white/20 uppercase text-[9px] block mb-0.5 tracking-wider">Image Prompt</span>
                          {scene.image_prompt}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* VIDEO SETTINGS */}
            {images.length > 0 && (
              <div className="glass-panel rounded-2xl p-6 space-y-6">
                <div className="flex items-center gap-2 mb-2">
                  <Settings className="w-5 h-5 text-[#FF4D00]" />
                  <h3 className="text-xl font-semibold font-['Manrope']">Video Settings</h3>
                </div>



                {/* Render mode toggle */}
                <div className="space-y-2">
                  <Label className="text-white/80 flex items-center gap-2">
                    <Film className="w-4 h-4 text-[#FF4D00]" />Rendering Mode
                  </Label>
                  <Select value={renderMode} onValueChange={setRenderMode}>
                    <SelectTrigger className="bg-[#111] border-[#FF4D00]/30 text-white rounded-lg h-11">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                      <SelectItem value="slideshow">⚡ Fast Slideshow (FFmpeg — uses transitions)</SelectItem>
                      <SelectItem value="animated">✨ AI Animated (Premium clips per scene)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {renderMode === 'animated' && (
                  <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                    <Label className="text-white/80 flex items-center gap-2 text-sm">
                      <Sparkles className="w-4 h-4 text-indigo-400" />Animation Provider
                    </Label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => setAnimationProvider('minimax')}
                        className={`px-3 py-2 rounded-lg border text-xs font-medium transition-all ${animationProvider === 'minimax' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'}`}
                      >
                        Minimax-01
                      </button>
                      <button
                        onClick={() => setAnimationProvider('runway')}
                        className={`px-3 py-2 rounded-lg border text-xs font-medium transition-all ${animationProvider === 'runway' ? 'bg-indigo-500/20 border-indigo-500 text-indigo-300' : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'}`}
                      >
                        Runway Gen-3
                      </button>
                    </div>
                  </div>
                )}

                {/* FFmpeg-only settings — fade out in animated mode */}
                <div className={`grid grid-cols-1 md:grid-cols-2 gap-6 transition-opacity ${renderMode === 'animated' ? 'opacity-40 pointer-events-none' : ''}`}>
                  {/* Aspect ratio */}
                  <div className="space-y-2">
                    <Label className="text-white/80">Aspect Ratio</Label>
                    <Select value={aspectRatio} onValueChange={setAspectRatio}>
                      <SelectTrigger id="aspect-ratio" data-testid="aspect-ratio-select" className="bg-[#111] border-white/10 text-white rounded-lg h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                        <SelectItem value="16:9">16:9 — Landscape</SelectItem>
                        <SelectItem value="9:16">9:16 — Portrait</SelectItem>
                        <SelectItem value="1:1">1:1 — Square</SelectItem>
                        <SelectItem value="4:5">4:5 — Instagram</SelectItem>
                        <SelectItem value="21:9">21:9 — Cinematic</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Image duration */}
                  <div className="space-y-2">
                    <Label className="text-white/80 flex items-center justify-between">
                      <span>Image Duration</span>
                      <span className="text-[#FF4D00] font-['JetBrains_Mono'] text-sm">{imageDuration}s</span>
                    </Label>
                    <Slider data-testid="image-duration-slider" value={[imageDuration]} onValueChange={(v) => setImageDuration(v[0])} min={1} max={10} step={0.5} className="py-4" />
                    <div className="flex justify-between text-xs text-white/40 font-['JetBrains_Mono']"><span>1s</span><span>10s</span></div>
                  </div>

                  {/* Transition style */}
                  <div className="space-y-2">
                    <Label className="text-white/80">Transition Style</Label>
                    <Select value={transitionStyle} onValueChange={setTransitionStyle}>
                      <SelectTrigger className="bg-[#111] border-white/10 text-white rounded-lg h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                        <SelectItem value="fade">Crossfade (Smooth)</SelectItem>
                        <SelectItem value="wipeleft">Wipe Left</SelectItem>
                        <SelectItem value="wiperight">Wipe Right</SelectItem>
                        <SelectItem value="slideup">Slide Up</SelectItem>
                        <SelectItem value="none">Hard Cut</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Transition duration */}
                  <div className="space-y-2">
                    <Label className="text-white/80 flex items-center justify-between">
                      <span>Transition Duration</span>
                      <span className="text-[#FF4D00] font-['JetBrains_Mono'] text-sm">{transitionDuration}s</span>
                    </Label>
                    <Slider data-testid="transition-duration-slider" value={[transitionDuration]} onValueChange={(v) => setTransitionDuration(v[0])} min={0.5} max={3} step={0.5} className="py-4" />
                    <div className="flex justify-between text-xs text-white/40 font-['JetBrains_Mono']"><span>0.5s</span><span>3s</span></div>
                  </div>

                  {/* Export Quality */}
                  <div className="space-y-2">
                    <Label className="text-white/80">Export Quality</Label>
                    <Select value={exportQuality} onValueChange={setExportQuality}>
                      <SelectTrigger className="bg-[#111] border-white/10 text-white rounded-lg h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                        <SelectItem value="240p">240p (Testing)</SelectItem>
                        <SelectItem value="360p">360p (Fast)</SelectItem>
                        <SelectItem value="480p">480p SD</SelectItem>
                        <SelectItem value="720p">720p HD</SelectItem>
                        <SelectItem value="1080p">1080p Full HD</SelectItem>
                        <SelectItem value="4k">4K Ultra HD</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Export Format */}
                  <div className="space-y-2">
                    <Label className="text-white/80">Video Format</Label>
                    <Select value={exportFormat} onValueChange={setExportFormat}>
                      <SelectTrigger className="bg-[#111] border-white/10 text-white rounded-lg h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-[#1A1A1A] border-white/10 text-white">
                        <SelectItem value="mp4">MP4 (H.264)</SelectItem>
                        <SelectItem value="mkv">WebM / MKV</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Audio upload */}
                <div className="pt-4 border-t border-white/10 space-y-3">
                  <Label className="flex items-center gap-2 text-white/80">
                    <Music className="w-4 h-4 text-[#FF4D00]" />Background Music / Voiceover
                  </Label>
                  {audioFile ? (
                    <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="w-8 h-8 rounded-full bg-[#FF4D00]/20 flex items-center justify-center flex-shrink-0">
                          <Music className="w-4 h-4 text-[#FF4D00]" />
                        </div>
                        <span className="text-sm truncate text-white/80">{audioFile.name}</span>
                      </div>
                      <button onClick={removeAudio} aria-label="Remove audio" className="text-white/40 hover:text-red-500 transition-colors p-1">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="relative">
                      <input type="file" accept="audio/mpeg,audio/wav" onChange={handleAudioSelect} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" disabled={uploadingAudio} />
                      <Button variant="outline" className="w-full border-dashed border-white/20 bg-transparent text-white/60 hover:text-white hover:border-[#FF4D00]/50 h-11">
                        {uploadingAudio ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
                        {uploadingAudio ? 'Uploading...' : 'Upload MP3 / WAV'}
                      </Button>
                    </div>
                  )}
                </div>

                {/* Stock Footage Fallback */}
                <div className="pt-4 border-t border-white/10 space-y-4">
                  <Label className="flex items-center gap-2 text-white/80">
                    <Database className="w-4 h-4 text-[#FF4D00]" />Stock Footage Search
                  </Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="e.g. 'modern house architecture'"
                      value={stockQuery}
                      onChange={(e) => setStockQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSearchStock()}
                      className="h-9 bg-[#111] border-white/10 text-white text-xs"
                    />
                    <Button onClick={handleSearchStock} disabled={isSearchingStock} className="h-9 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-xs px-3">
                      {isSearchingStock ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Search'}
                    </Button>
                  </div>

                  {stockResults.length > 0 && (
                    <div className="grid grid-cols-3 gap-2 max-h-[120px] overflow-y-auto pr-1 custom-scrollbar">
                      {stockResults.map((v) => (
                        <div key={v.id} className="relative aspect-video rounded-md overflow-hidden bg-white/5 group border border-transparent hover:border-[#FF4D00] transition-all">
                          <img src={v.thumbnail} alt="Stock tumbnail" className="w-full h-full object-cover" />
                          <button
                            onClick={() => importStockVideo(v)}
                            className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <PlusCircle className="w-6 h-6 text-white" />
                          </button>
                          <div className="absolute bottom-0 right-0 bg-black/60 px-1 text-[8px] text-white/60">
                            {v.duration}s
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* ── RIGHT PANEL: Video Preview ───────────────────────────────── */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold font-['Manrope'] mb-2">Video Preview</h2>
              <p className="text-white/60">Your generated video will appear here</p>
            </div>

            <div className="glass-panel rounded-2xl p-8 min-h-[500px] flex items-center justify-center">
              {generating ? (
                <div className="text-center max-w-sm w-full">
                  <div className="spinner mx-auto mb-6"></div>
                  <h3 className="text-xl font-semibold mb-3">
                    {renderMode === 'animated' ? 'Compiling AI Videos...' : 'Generating Your Video'}
                  </h3>
                  <p className="text-white/60 mb-6">
                    {renderMode === 'animated'
                      ? `Stitching ${images.length} AI clips together...`
                      : `Processing ${images.length} image${images.length > 1 ? 's' : ''} at ${aspectRatio}...`}
                  </p>
                  <div className="space-y-2 text-sm text-white/50">
                    {['Optimizing assets', 'Applying transitions', 'Encoding video'].map((step, i) => (
                      <p key={step} className="flex items-center gap-2 justify-center">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#FF4D00] animate-pulse" style={{ animationDelay: `${i * 0.2}s` }} />
                        {step}
                      </p>
                    ))}
                  </div>
                  <div className="mt-6 px-4 py-3 rounded-lg bg-white/5 border border-white/10">
                    <p className="text-xs text-white/40">
                      ⏱ Est. {Math.ceil(images.length * 5)}–{Math.ceil(images.length * 10)} seconds
                    </p>
                  </div>
                </div>
              ) : videoUrl ? (
                <div className="w-full">
                  <video
                    key={videoUrl}
                    src={videoUrl}
                    controls
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="w-full rounded-xl shadow-2xl border border-white/10"
                  />
                  <div className="flex justify-end mt-4">
                    <Button onClick={handleDownload} className="bg-[#FF4D00] hover:bg-[#FF4D00]/90 text-white rounded-full">
                      <Download className="w-4 h-4 mr-2" />Download MP4
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-white/30">
                  <Play className="w-16 h-16 mx-auto mb-4 opacity-20" />
                  <p>Upload images and click Generate Video</p>
                  {renderMode === 'animated' && images.length > 0 && (
                    <p className="text-xs mt-2 text-amber-400/60">
                      Hover scene thumbnails to animate them first
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <ApiSettingsModal isOpen={isApiModalOpen} onClose={() => setIsApiModalOpen(false)} />
    </div>
  );
};