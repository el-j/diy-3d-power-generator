import React, { useState } from 'react';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { getMarkdown } from '../md-loader';
import { formatKey, countEntries } from '../utils/content';
import type { BomData } from '../types/content';
import bomDataRaw from '../../bom/master_bom.json';

type Tab = 'summary' | 'markdown' | 'json';

export function BomPage(): React.JSX.Element {
  const [tab, setTab] = useState<Tab>('summary');
  const bomData = bomDataRaw as BomData;

  const TAB_LABELS: Record<Tab, string> = {
    summary: 'Summary',
    markdown: 'BOM Markdown',
    json: 'BOM JSON',
  };

  return (
    <div className="content-wrap">
      <section className="section">
        <h2>Bill of Materials</h2>
        <p className="section-lead">
          Live totals from <code>docs/bom/master_bom.json</code>.
        </p>

        <div className="metrics-grid">
          {Object.entries(bomData.totals).map(([k, v]) => (
            <article key={k} className="metric-card">
              <span>{formatKey(k)}</span>
              <strong>{v}</strong>
            </article>
          ))}
        </div>

        <div className="tab-bar">
          {(['summary', 'markdown', 'json'] as Tab[]).map((t) => (
            <button
              key={t}
              className={`tab-btn${tab === t ? ' active' : ''}`}
              onClick={() => setTab(t)}
            >
              {TAB_LABELS[t]}
            </button>
          ))}
        </div>

        {tab === 'summary' && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Assembly</th>
                  <th>Entries</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(bomData.assemblies).map(([name, value]) => (
                  <tr key={name}>
                    <td>{formatKey(name)}</td>
                    <td>{countEntries(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'markdown' && (
          <div style={{ marginTop: '1rem' }}>
            <MarkdownRenderer content={getMarkdown('docs/bom/master_bom.md')} />
          </div>
        )}

        {tab === 'json' && (
          <pre className="json-pre">
            <code>{JSON.stringify(bomDataRaw, null, 2)}</code>
          </pre>
        )}
      </section>
    </div>
  );
}
