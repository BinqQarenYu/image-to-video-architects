import { useNavigate } from 'react-router-dom';
import { Film, Upload, Play, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';

export const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Hero Section */}
      <div className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: 'url(https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1920&q=85&auto=format&fit=crop)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 hero-gradient z-10" />

        {/* Noise Overlay */}
        <div className="absolute inset-0 noise-overlay z-10" />

        {/* Content */}
        <div className="relative z-20 text-center px-6 max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-sm border border-white/10 mb-8">
            <Sparkles className="w-4 h-4 text-[#FF4D00]" />
            <span className="text-sm text-white/80">Free Architecture Video Generator</span>
          </div>

          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-['Manrope'] tracking-tight mb-6 leading-tight">
            Transform Your <span className="text-[#FF4D00]">Architecture</span>
            <br />Into Cinematic Videos
          </h1>

          <p className="text-lg sm:text-xl text-white/70 mb-12 max-w-2xl mx-auto">
            Upload your architectural images and create stunning video presentations with smooth transitions. Perfect for portfolios, presentations, and social media.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              data-testid="create-video-btn"
              onClick={() => navigate('/studio')}
              className="rounded-full font-semibold tracking-wide transition-all duration-300 bg-[#FF4D00] text-white hover:bg-[#FF4D00]/90 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(255,77,0,0.3)] px-8 py-6 text-lg h-auto"
            >
              <Upload className="w-5 h-5 mr-2" />
              Create Video Now
            </Button>

            <Button
              data-testid="learn-more-btn"
              onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
              variant="outline"
              className="rounded-full border border-white/20 bg-transparent text-white hover:bg-white hover:text-black hover:border-white transition-all duration-300 px-8 py-6 text-lg h-auto"
            >
              <Play className="w-5 h-5 mr-2" />
              Learn More
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold font-['Manrope'] tracking-tight mb-4">
              Powerful Yet Simple
            </h2>
            <p className="text-lg text-white/60 max-w-2xl mx-auto">
              Everything you need to create professional architectural videos in minutes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="glass-panel rounded-2xl p-8 hover:border-white/20 transition-all duration-500 group">
              <div className="w-14 h-14 rounded-full bg-[#FF4D00]/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Upload className="w-7 h-7 text-[#FF4D00]" />
              </div>
              <h3 className="text-2xl font-semibold font-['Manrope'] mb-3">Easy Upload</h3>
              <p className="text-white/60 leading-relaxed">
                Drag and drop your architectural images or click to browse. Supports multiple images at once.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="glass-panel rounded-2xl p-8 hover:border-white/20 transition-all duration-500 group">
              <div className="w-14 h-14 rounded-full bg-[#FF4D00]/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Film className="w-7 h-7 text-[#FF4D00]" />
              </div>
              <h3 className="text-2xl font-semibold font-['Manrope'] mb-3">Smooth Transitions</h3>
              <p className="text-white/60 leading-relaxed">
                Professional crossfade and pan effects create cinematic videos that showcase your work beautifully.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="glass-panel rounded-2xl p-8 hover:border-white/20 transition-all duration-500 group">
              <div className="w-14 h-14 rounded-full bg-[#FF4D00]/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Sparkles className="w-7 h-7 text-[#FF4D00]" />
              </div>
              <h3 className="text-2xl font-semibold font-['Manrope'] mb-3">Free Forever</h3>
              <p className="text-white/60 leading-relaxed">
                No hidden costs, no subscriptions. Create unlimited videos completely free with no watermarks.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24 px-6">
        <div className="max-w-4xl mx-auto glass-panel rounded-3xl p-12 text-center">
          <h2 className="text-4xl sm:text-5xl font-bold font-['Manrope'] tracking-tight mb-6">
            Ready to Create?
          </h2>
          <p className="text-lg text-white/70 mb-8 max-w-2xl mx-auto">
            Start transforming your architectural images into stunning videos today.
          </p>
          <Button
            data-testid="cta-create-video-btn"
            onClick={() => navigate('/studio')}
            className="rounded-full font-semibold tracking-wide transition-all duration-300 bg-[#FF4D00] text-white hover:bg-[#FF4D00]/90 hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(255,77,0,0.3)] px-8 py-6 text-lg h-auto"
          >
            <Upload className="w-5 h-5 mr-2" />
            Get Started Free
          </Button>
        </div>
      </div>
    </div>
  );
};