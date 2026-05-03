import React from 'react';
import type { FeatureCard } from '../types/content';

type WhySectionProps = {
  cards: FeatureCard[];
};

export function WhySection({ cards }: WhySectionProps): React.JSX.Element {
  return (
    <section className="section" id="why">
      <h2>What This Build Is</h2>
      <p className="section-lead">
        An open-source 3D-printable vertical-axis wind generator — from aerodynamic blades to axial-flux generator to wall-mounted base station.
      </p>
      <div className="card-grid">
        {cards.map((feature) => (
          <article key={feature.title} className="card">
            <h3>{feature.title}</h3>
            <p>{feature.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
