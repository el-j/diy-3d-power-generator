import React from 'react';
import { useHashRoute } from './hooks/useHashRoute';
import { NavBar } from './components/NavBar';
import { LandingPage } from './pages/LandingPage';
import { PlaygroundPage } from './pages/PlaygroundPage';
import { DocsPage } from './pages/DocsPage';
import { BuildGuidePage } from './pages/BuildGuidePage';
import { BomPage } from './pages/BomPage';
import { DownloadsPage } from './pages/DownloadsPage';

export function App(): React.JSX.Element {
  const [route, navigate] = useHashRoute();

  return (
    <div className="page-shell">
      {route !== 'playground' && (
        <header className="hero" id="overview">
          <div className="hero-glow" aria-hidden="true" />
          <NavBar route={route} navigate={navigate} />
        </header>
      )}

      {route === 'home' && <LandingPage navigate={navigate} />}
      {route === 'playground' && <PlaygroundPage navigate={navigate} />}
      {route === 'docs' && <DocsPage />}
      {route === 'build-guide' && <BuildGuidePage />}
      {route === 'bom' && <BomPage />}
      {route === 'downloads' && <DownloadsPage />}
    </div>
  );
}
