import React from 'react';
import type { FeatureCard } from '../types/content';

type WhySectionProps = {
  cards: FeatureCard[];
};

export function WhySection({ cards }: WhySectionProps): React.JSX.Element {
  return (
    <section className="section" id="why">
      <h2>Why This Refactor</h2>
      <p className="section-lead">
        Typed components, explicit data models, and smaller render units are easier to evolve than one monolithic page.
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
