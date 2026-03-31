import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Play, Trash2, Calendar, Clock, Layout, Film } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/ui/tooltip';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "../components/ui/alert-dialog";
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ProjectLibrary = () => {
    const navigate = useNavigate();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const response = await axios.get(`${API}/projects`);
            setProjects(response.data);
        } catch (error) {
            console.error('Error fetching projects:', error);
            toast.error('Failed to load project library');
        } finally {
            setLoading(false);
        }
    };

    const deleteProject = async (id) => {
        try {
            await axios.delete(`${API}/projects/${id}`);
            setProjects(projects.filter(p => p.id !== id));
            toast.success('Project deleted');
        } catch (error) {
            console.error('Error deleting project:', error);
            toast.error('Failed to delete project');
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        }).format(date);
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white">
            {/* Header */}
            <header className="border-b border-white/10 bg-[#0A0A0A]/80 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    data-testid="back-btn"
                                    variant="ghost"
                                    onClick={() => navigate('/studio')}
                                    className="text-white/60 hover:text-white hover:bg-white/10"
                                    aria-label="Back to Studio"
                                >
                                    <ArrowLeft className="w-5 h-5" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>Back to Studio</p>
                            </TooltipContent>
                        </Tooltip>
                        <h1 className="text-2xl font-bold font-['Manrope']">Project Library</h1>
                    </div>
                    <Button
                        onClick={() => navigate('/studio')}
                        className="rounded-full font-semibold bg-[#FF4D00] text-white hover:bg-[#FF4D00]/90 hover:scale-105"
                    >
                        New Project
                    </Button>
                </div>
            </header>

            <div className="max-w-7xl mx-auto px-6 py-12">
                {loading ? (
                    <div className="flex flex-col items-center justify-center min-h(\[400px\])">
                        <Loader2 className="w-12 h-12 text-[#FF4D00] animate-spin mb-4" />
                        <p className="text-white/60">Loading your projects...</p>
                    </div>
                ) : projects.length === 0 ? (
                    <div className="text-center py-24 glass-panel rounded-3xl">
                        <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mx-auto mb-6">
                            <Film className="w-10 h-10 text-white/40" />
                        </div>
                        <h2 className="text-2xl font-bold font-['Manrope'] mb-3">No Projects Yet</h2>
                        <p className="text-white/60 mb-8 max-w-md mx-auto">
                            You haven't generated any videos yet. Head over to the studio to create your first cinematic architecture video.
                        </p>
                        <Button
                            onClick={() => navigate('/studio')}
                            className="rounded-full font-semibold bg-white text-black hover:bg-white/90"
                        >
                            Go to Studio
                        </Button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {projects.map((project) => (
                            <div key={project.id} className="glass-panel rounded-2xl overflow-hidden group hover:border-[#FF4D00]/50 transition-all duration-300 transform hover:-translate-y-1">
                                {/* Video Thumbnail (using the first image if video can't autoplay) */}
                                <div className="relative aspect-video bg-black/50 border-b border-white/10 overflow-hidden">
                                    {project.video_url ? (
                                        <video
                                            src={`${BACKEND_URL}${project.video_url}`}
                                            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-500"
                                            muted
                                            loop
                                            playsInline
                                            onMouseOver={(e) => e.target.play().catch(() => { })}
                                            onMouseOut={(e) => e.target.pause()}
                                        />
                                    ) : (
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <Play className="w-12 h-12 text-white/20" />
                                        </div>
                                    )}
                                    <div className="absolute top-3 right-3 flex gap-2">
                                        <AlertDialog>
                                            <AlertDialogTrigger asChild>
                                                <button
                                                    aria-label="Delete project"
                                                    className="w-8 h-8 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-white/60 hover:text-red-500 hover:bg-red-500/10 transition-colors duration-200"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </AlertDialogTrigger>
                                            <AlertDialogContent className="bg-[#1A1A1A] border-white/10 text-white">
                                                <AlertDialogHeader>
                                                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                                    <AlertDialogDescription className="text-white/60">
                                                        This action cannot be undone. This will permanently delete your
                                                        project and remove the video from our servers.
                                                    </AlertDialogDescription>
                                                </AlertDialogHeader>
                                                <AlertDialogFooter>
                                                    <AlertDialogCancel className="bg-transparent border-white/10 text-white hover:bg-white/5">Cancel</AlertDialogCancel>
                                                    <AlertDialogAction
                                                        onClick={() => deleteProject(project.id)}
                                                        className="bg-red-600 text-white hover:bg-red-700 border-none"
                                                    >
                                                        Delete Project
                                                    </AlertDialogAction>
                                                </AlertDialogFooter>
                                            </AlertDialogContent>
                                        </AlertDialog>
                                    </div>
                                </div>

                                {/* Project Info */}
                                <div className="p-5">
                                    <h3 className="text-lg font-semibold font-['Manrope'] mb-3 truncate" title={project.name}>
                                        {project.name}
                                    </h3>

                                    <div className="grid grid-cols-2 gap-3 mb-4">
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            <Layout className="w-3.5 h-3.5" />
                                            <span>{project.aspect_ratio}</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            <Clock className="w-3.5 h-3.5" />
                                            <span className="font-['JetBrains_Mono']">{project.image_duration}s / img</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            <Calendar className="w-3.5 h-3.5" />
                                            <span>{formatDate(project.created_at)}</span>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-white/50">
                                            <div className="w-3.5 h-3.5 rounded bg-white/10 flex items-center justify-center text-[8px] font-bold">
                                                {project.image_urls?.length || 0}
                                            </div>
                                            <span>Images</span>
                                        </div>
                                    </div>

                                    {project.prompt && (
                                        <p className="text-xs text-white/40 italic line-clamp-2 mt-2 bg-white/5 p-2 rounded">
                                            "{project.prompt}"
                                        </p>
                                    )}

                                    {project.video_url && (
                                        <div className="mt-4 pt-4 border-t border-white/10">
                                            <a
                                                href={`${BACKEND_URL}${project.video_url}`}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="flex items-center justify-center w-full gap-2 text-sm font-semibold text-white/80 hover:text-white bg-white/5 hover:bg-white/10 py-2 rounded-lg transition-colors"
                                            >
                                                <Play className="w-4 h-4" />
                                                Open Video
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
