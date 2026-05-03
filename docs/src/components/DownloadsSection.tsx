import React from 'react';
import type { DownloadItem } from '../types/content';
import { toBlobUrl, toRawUrl } from '../utils/content';

type DownloadsSectionProps = {
  items: DownloadItem[];
};

export function DownloadsSection({ items }: DownloadsSectionProps): React.JSX.Element {
  return (
    <section className="section" id="downloads">
      <h2>Downloads</h2>
      <p className="section-lead">Direct raw links and repo links for active printable packages.</p>
      <div className="downloads-grid">
        {items.map((item) => (
          <article key={item.path} className="download-card">
            <span className="tag">{item.category}</span>
            <h3>{item.label}</h3>
            <p>{item.path}</p>
            <div className="download-links">
              <a href={toRawUrl(item.path)} target="_blank" rel="noreferrer">Direct</a>
              <a href={toBlobUrl(item.path)} target="_blank" rel="noreferrer">View</a>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
