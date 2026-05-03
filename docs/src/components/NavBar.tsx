import React from 'react';
import type { RouteId } from '../hooks/useHashRoute';
import { REPO_URL } from '../data/content';

type Props = {
  route: RouteId;
  navigate: (r: RouteId) => void;
};

const NAV_ITEMS: { id: RouteId; label: string }[] = [
  { id: 'home', label: 'Overview' },
  { id: 'playground', label: '3D Playground' },
  { id: 'docs', label: 'Docs' },
  { id: 'build-guide', label: 'Build Guide' },
  { id: 'bom', label: 'BOM' },
  { id: 'downloads', label: 'Downloads' },
];

export function NavBar({ route, navigate }: Props): React.JSX.Element {
  return (
    <nav className="top-nav">
      <button className="brand nav-brand-btn" onClick={() => navigate('home')}>
        Helix Wind Build
      </button>
      <div className="nav-links">
        {NAV_ITEMS.map(({ id, label }) => (
          <button
            key={id}
            className={`nav-route-btn${route === id ? ' active' : ''}`}
            onClick={() => navigate(id)}
          >
            {label}
          </button>
        ))}
        <a href={REPO_URL} target="_blank" rel="noreferrer" className="nav-route-btn">
          GitHub
        </a>
      </div>
    </nav>
  );
}
