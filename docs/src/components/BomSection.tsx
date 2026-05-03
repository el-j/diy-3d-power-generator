import React from 'react';
import type { AssemblyStatRow, BomData } from '../types/content';
import { countEntries, formatKey } from '../utils/content';

type BomSectionProps = {
  bomData: BomData;
};

export function BomSection({ bomData }: BomSectionProps): React.JSX.Element {
  const assemblyStats: AssemblyStatRow[] = Object.entries(bomData.assemblies).map(([name, value]) => ({
    name: formatKey(name),
    count: countEntries(value)
  }));

  return (
    <section className="section" id="bom">
      <h2>Master BOM Snapshot</h2>
      <p className="section-lead">Live totals loaded from <code>docs/bom/master_bom.json</code>.</p>

      <div className="metrics-grid">
        {Object.entries(bomData.totals).map(([key, value]) => (
          <article key={key} className="metric-card">
            <span>{formatKey(key)}</span>
            <strong>{value}</strong>
          </article>
        ))}
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Assembly</th>
              <th>Entries</th>
            </tr>
          </thead>
          <tbody>
            {assemblyStats.map((row) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td>{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
