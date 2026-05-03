import React, { useState } from 'react';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { getMarkdown } from '../md-loader';
import { buildGuideLinks } from '../content/siteContent';

export function BuildGuidePage(): React.JSX.Element {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = buildGuideLinks[activeIndex];

  return (
    <div className="reader-shell">
      <aside className="reader-sidebar">
        <p className="sidebar-label">Build Guide</p>
        {buildGuideLinks.map((item, i) => (
          <button
            key={item.path}
            className={`sidebar-btn${i === activeIndex ? ' active' : ''}`}
            onClick={() => setActiveIndex(i)}
          >
            {item.title}
            {item.description && <span className="sidebar-desc">{item.description}</span>}
          </button>
        ))}
      </aside>
      <main className="reader-content">
        <MarkdownRenderer content={getMarkdown(active.path)} />
      </main>
    </div>
  );
}
