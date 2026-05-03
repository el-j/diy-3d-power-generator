import React from 'react';
import type { BuildStep } from '../types/content';

type BuildStepsSectionProps = {
  steps: BuildStep[];
};

export function BuildStepsSection({ steps }: BuildStepsSectionProps): React.JSX.Element {
  return (
    <section className="section" id="steps">
      <h2>Build Sequence</h2>
      <p className="section-lead">High-level path from printed parts to working tower assembly.</p>
      <div className="timeline">
        {steps.map((step) => (
          <article key={step.id} className="timeline-item">
            <div className="step-id">{step.id}</div>
            <div>
              <h3>{step.title}</h3>
              <p>{step.detail}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
