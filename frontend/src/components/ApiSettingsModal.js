import React, { useState, useEffect } from 'react';
import { X, Key, Save, ShieldCheck, MessageSquare, Image as ImageIcon, Music, Database } from 'lucide-react';
import * as Tabs from '@radix-ui/react-tabs';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { toast } from 'sonner';

export const ApiSettingsModal = ({ isOpen, onClose }) => {
    // State management for all categories
    const [keys, setKeys] = useState({
        // LLMs
        openai_api_key: '',
        gemini_api_key: '',
        grok_api_key: '',
        openrouter_api_key: '',
        ollama_endpoint: 'http://localhost:11434', // Local default
        ollama_model: 'llama3', // Local default model

        // Image & Video Gen
        fal_api_key: '',
        minimax_api_key: '',
        runway_api_key: '',
        huggingface_api_key: '',

        // Audio
        elevenlabs_api_key: '',

        // Stock
        pexels_api_key: '',
        pixabay_api_key: ''
    });

    // Load keys from localStorage on mount
    useEffect(() => {
        if (isOpen) {
            setKeys(prev => {
                const loadedKeys = { ...prev };
                Object.keys(loadedKeys).forEach(keyName => {
                    const storedValue = localStorage.getItem(keyName);
                    if (storedValue !== null) {
                        loadedKeys[keyName] = storedValue;
                    }
                });
                return loadedKeys;
            });
        }
    }, [isOpen]);

    const handleInputChange = (e) => {
        const { id, value } = e.target;
        setKeys(prev => ({ ...prev, [id]: value }));
    };

    const handleSave = () => {
        Object.entries(keys).forEach(([keyName, value]) => {
            localStorage.setItem(keyName, value);
        });
        toast.success('AI Provider Settings saved securely.');
        onClose();
    };

    if (!isOpen) return null;

    // Helper component for creating input fields
    const KeyInput = ({ id, label, placeholder, desc, type = "password" }) => (
        <div className="space-y-2 mb-4">
            <Label htmlFor={id} className="text-white/80">{label}</Label>
            <Input
                id={id}
                type={type}
                placeholder={placeholder}
                value={keys[id]}
                onChange={handleInputChange}
                className="bg-[#111] border-white/10 focus:border-[#FF4D00]/50 text-white placeholder:text-white/20"
            />
            {desc && <p className="text-[10px] text-white/40">{desc}</p>}
        </div>
    );

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="relative w-full max-w-2xl bg-[#0A0A0A] border border-white/10 rounded-2xl shadow-2xl flex flex-col max-h-[90vh]">

                {/* Header - Fixed */}
                <div className="p-6 pb-4 border-b border-white/5 shrink-0">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 border rounded-full bg-white/5 border-white/10 text-[#FF4D00]">
                                <Key className="w-5 h-5" />
                            </div>
                            <h2 className="text-xl font-bold font-['Manrope'] text-white">AI Provider Settings</h2>
                        </div>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <button
                                    onClick={onClose}
                                    aria-label="Close settings"
                                    className="p-1 transition-colors rounded-full text-white/50 hover:text-white hover:bg-white/10"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </TooltipTrigger>
                            <TooltipContent>Close settings</TooltipContent>
                        </Tooltip>
                    </div>

                    <div className="flex items-start gap-3 p-3 border rounded-lg bg-green-500/10 border-green-500/20 text-green-400">
                        <ShieldCheck className="w-5 h-5 mt-0.5 shrink-0" />
                        <p className="text-xs leading-relaxed">
                            Your API keys are stored securely in your browser's local storage. They are never sent to our servers.
                        </p>
                    </div>
                </div>

                {/* Body - Scrollable */}
                <div className="p-6 overflow-y-auto overflow-x-hidden flex-1 custom-scrollbar">
                    <Tabs.Root defaultValue="llm" className="flex flex-col w-full">
                        <Tabs.List className="flex w-full mb-6 border-b border-white/10">
                            {[
                                { id: 'llm', icon: MessageSquare, label: 'Scripts (LLM)' },
                                { id: 'image', icon: ImageIcon, label: 'Image & Video' },
                                { id: 'audio', icon: Music, label: 'Audio' },
                                { id: 'stock', icon: Database, label: 'Stock Media' }
                            ].map((tab) => (
                                <Tabs.Trigger
                                    key={tab.id}
                                    value={tab.id}
                                    className="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 border-transparent text-white/50 hover:text-white/80 data-[state=active]:text-[#FF4D00] data-[state=active]:border-[#FF4D00]"
                                >
                                    <tab.icon className="w-4 h-4" />
                                    {tab.label}
                                </Tabs.Trigger>
                            ))}
                        </Tabs.List>

                        <Tabs.Content value="llm" className="outline-none space-y-6 animate-in fade-in-50">
                            <div>
                                <h3 className="text-sm font-semibold text-white/90 mb-4">Cloud Providers</h3>
                                <KeyInput id="openai_api_key" label="OpenAI API Key" placeholder="sk-..." desc="Used for generating high-quality architectural scripts with GPT-4." />
                                <KeyInput id="gemini_api_key" label="Google Gemini API Key" placeholder="AIza..." desc="Excellent for vision-based prompt analysis." />
                                <KeyInput id="grok_api_key" label="xAI Grok API Key" placeholder="xai-..." />
                                <KeyInput id="openrouter_api_key" label="OpenRouter API Key" placeholder="sk-or-..." desc="Access multiple community models." />
                            </div>
                            <div className="pt-4 border-t border-white/5">
                                <h3 className="text-sm font-semibold text-white/90 mb-4">Local Providers</h3>
                                <KeyInput id="ollama_endpoint" type="text" label="Ollama Endpoint" placeholder="http://localhost:11434" desc="URL to your running Ollama instance for free, local script generation." />
                                <KeyInput id="ollama_model" type="text" label="Ollama Model" placeholder="gpt-oss:20b" desc="The tag of the model pulled via Ollama (e.g., 'gpt-oss:20b', 'llama3')." />
                            </div>
                        </Tabs.Content>

                        <Tabs.Content value="image" className="outline-none space-y-6 animate-in fade-in-50">
                            <KeyInput id="fal_api_key" label="Fal.ai API Key" placeholder="fal-..." desc="Fast image generation models (Flux, Stable Diffusion)." />
                            <KeyInput id="minimax_api_key" label="Minimax.io API Key" placeholder="..." desc="High-quality AI video generation (image-to-video)." />
                            <KeyInput id="runway_api_key" label="Runway ML API Key" placeholder="..." desc="Gen-3 Alpha Turbo image-to-video API." />
                            <KeyInput id="huggingface_api_key" label="Hugging Face Token" placeholder="hf_..." />
                        </Tabs.Content>

                        <Tabs.Content value="audio" className="outline-none space-y-6 animate-in fade-in-50">
                            <KeyInput id="elevenlabs_api_key" label="ElevenLabs API Key" placeholder="..." desc="Cinematic and realistic AI voiceover generation." />
                        </Tabs.Content>

                        <Tabs.Content value="stock" className="outline-none space-y-6 animate-in fade-in-50">
                            <KeyInput id="pexels_api_key" label="Pexels API Key" placeholder="..." desc="For searching free stock images and B-roll video." />
                            <KeyInput id="pixabay_api_key" label="Pixabay API Key" placeholder="..." />
                        </Tabs.Content>

                    </Tabs.Root>
                </div>

                {/* Footer - Fixed */}
                <div className="p-6 pt-4 border-t border-white/5 bg-[#050505] shrink-0 flex justify-end gap-3 rounded-b-2xl">
                    <Button variant="ghost" onClick={onClose} className="text-white/70 hover:text-white hover:bg-white/5">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSave}
                        className="bg-[#FF4D00] text-white hover:bg-[#FF4D00]/90 px-6 font-semibold"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        Save All Keys
                    </Button>
                </div>
            </div>
        </div>
    );
};
