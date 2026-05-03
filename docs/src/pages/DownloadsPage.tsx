import React from 'react';
import { downloadItems, toRepoBlobUrl, toRepoRawUrl } from '../content/siteContent';

const CATEGORY_ORDER = ['bundle', 'generator', 'tower', 'base', 'tools'] as const;
const CATEGORY_LABELS: Record<string, string> = {
  bundle: 'Complete Bundles (.3mf)',
  generator: 'Generator Parts',
  tower: 'Tower Parts',
  base: 'Base Station Parts',
  tools: 'Winding Tools',
};

export function DownloadsPage(): React.JSX.Element {
  return (
    <div className="content-wrap">
      {CATEGORY_ORDER.map((cat) => {
        const items = downloadItems.filter((d) => d.category === cat);
        if (items.length === 0) return null;
        return (
          <section key={cat} className="section">
            <h2>{CATEGORY_LABELS[cat]}</h2>
            <div className="downloads-grid">
              {items.map((item) => (
                <article key={item.path} className="download-card">
                  <span className="tag">{item.category.toUpperCase()}</span>
                  <h3>{item.label}</h3>
                  <p className="dl-path">{item.path}</p>
                  <div className="download-links">
                    <a href={toRepoRawUrl(item.path)} target="_blank" rel="noreferrer">
                      Direct
                    </a>
                    <a href={toRepoBlobUrl(item.path)} target="_blank" rel="noreferrer">
                      View
                    </a>
                  </div>
                </article>
              ))}
            </div>
          </section>
        );
      })}

      <section className="section">
        <h2>Full Export Tree</h2>
        <p className="section-lead">Browse all generated STL/3MF artifacts in the repository.</p>
        <div className="download-links" style={{ marginTop: '0.7rem' }}>
          <a
            href="https://github.com/el-j/diy-3d-power-generator/tree/main/exports"
            target="_blank"
            rel="noreferrer"
            className="btn btn-ghost"
          >
            Open exports/ on GitHub
          </a>
        </div>
      </section>
    </div>
  );
}
