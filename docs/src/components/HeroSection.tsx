import React from 'react';
import { REPO_URL } from '../data/content';
import type { NavItem } from '../types/content';

type HeroSectionProps = {
  navItems: NavItem[];
};

export function HeroSection({ navItems }: HeroSectionProps): React.JSX.Element {
  return (
    <header className="hero" id="overview">
      <div className="hero-glow" aria-hidden="true" />
      <nav className="top-nav">
        <a href="#overview" className="brand">Helix Wind Build</a>
        <div className="nav-links">
          {navItems.map((item) => (
            <a key={item.href} href={item.href}>{item.label}</a>
          ))}
          <a href={REPO_URL} target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </nav>

      <div className="hero-content">
        <p className="eyebrow">Open Source Wind Generator</p>
        <h1>Static Build Portal With Typed React Architecture</h1>
        <p>
          This page replaces the giant hand-managed HTML shell with strongly typed React components.
          It keeps the project documentation, BOM visibility, and download access in a cleaner, maintainable structure.
        </p>
        <div className="hero-actions">
          <a href="#downloads" className="btn btn-primary">Get Files</a>
          <a href="#steps" className="btn btn-ghost">Start Build</a>
        </div>
      </div>
    </header>
  );
}
