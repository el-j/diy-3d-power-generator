import React from 'react';
import type { RouteId } from '../hooks/useHashRoute';
import { WhySection } from '../components/WhySection';
import { BomSection } from '../components/BomSection';
import { BuildStepsSection } from '../components/BuildStepsSection';
import { buildSteps, featureCards } from '../data/content';
import type { BomData } from '../types/content';
import bomDataRaw from '../../bom/master_bom.json';

type Props = {
  navigate: (r: RouteId) => void;
};

export function LandingPage({ navigate }: Props): React.JSX.Element {
  const bomData = bomDataRaw as BomData;

  return (
    <main className="content-wrap">
      <section className="section hero-intro">
        <p className="eyebrow">Open Source Wind Generator</p>
        <h1 style={{ margin: '0.4rem 0 0.6rem', fontFamily: 'var(--font-display)', fontSize: 'clamp(1.8rem,4vw,2.8rem)', lineHeight: 1 }}>
          Helix Wind Build
        </h1>
        <p style={{ margin: 0, color: 'var(--muted)', maxWidth: 660, lineHeight: 1.6 }}>
          Parametric 3D-printed axial-flux generator and helix tower. All geometry from FreeCAD
          Python. Explore the interactive 3D playground, read docs, or download print-ready files.
        </p>
        <div className="hero-actions" style={{ marginTop: '1rem' }}>
          <button className="btn btn-primary" onClick={() => navigate('playground')}>
            3D Playground
          </button>
          <button className="btn btn-ghost" onClick={() => navigate('build-guide')}>
            Build Guide
          </button>
          <button className="btn btn-ghost" onClick={() => navigate('downloads')}>
            Downloads
          </button>
        </div>
      </section>

      <WhySection cards={featureCards} />
      <BomSection bomData={bomData} />
      <BuildStepsSection steps={buildSteps} />
    </main>
  );
}
