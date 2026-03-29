import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/sonner';
import { TooltipProvider } from './components/ui/tooltip';
import { Landing } from './pages/Landing';
import { Studio } from './pages/Studio';
import { ProjectLibrary } from './pages/ProjectLibrary';
import './App.css';

function App() {
  return (
    <TooltipProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/studio" element={<Studio />} />
          <Route path="/projects" element={<ProjectLibrary />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" theme="dark" />

      {/* LikhaTech branding badge */}
      <BrandingBadge />
    </TooltipProvider>
  );
}

const BrandingBadge = () => {
  return (
    <a
        href="https://likhatechbuilder.com"
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: 'fixed',
          bottom: '16px',
          right: '16px',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '7px',
          padding: '7px 13px',
          borderRadius: '999px',
          background: 'rgba(20,20,20,0.85)',
          backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255,77,0,0.3)',
          color: 'rgba(255,255,255,0.8)',
          fontSize: '12px',
          fontWeight: 600,
          textDecoration: 'none',
          letterSpacing: '0.02em',
          boxShadow: '0 2px 12px rgba(0,0,0,0.4)',
          transition: 'border-color 0.2s, color 0.2s',
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(255,77,0,0.8)'; e.currentTarget.style.color = '#fff'; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,77,0,0.3)'; e.currentTarget.style.color = 'rgba(255,255,255,0.8)'; }}
      >
        <span style={{ color: '#FF4D00', fontSize: '14px' }}>⚡</span>
        Made by LikhaTech
      </a>
  );
};

export default App;