import React, { useState } from 'react';
import { MarkdownRenderer } from '../components/MarkdownRenderer';
import { Checklist } from '../components/Checklist';
import { WingTypeSwitcher } from '../components/WingTypeSwitcher';
import { getMarkdown } from '../md-loader';
import { buildGuideLinks } from '../content/siteContent';

// ---------------------------------------------------------------------------
// Checklist data per section (keyed by buildGuideLinks[i].title)
// ---------------------------------------------------------------------------

interface SectionChecklist {
  id: string;
  items: string[];
}

const SECTION_CHECKLISTS: Record<string, SectionChecklist> = {
  '01 Tower': {
    id: 'build-guide-tower',
    items: [
      'Printed all tower parts (blade, connector, plug, disc)',
      'Verified vielzahn spline fit (12-tooth, 30° indexing)',
      'Checked blade wall thickness ≥ 2.4 mm',
      'Stacked stages and confirmed 240 mm height per stage',
      'Inserted square shaft (10×10 mm) through all stages',
      'Blade orientation confirmed: 90° twist per stage (Helix)',
      'Test rotation: no binding or vibration',
    ],
  },
  '02 Generator': {
    id: 'build-guide-generator',
    items: [
      'Printed all 13 generator parts',
      'Inserted 20× N52 magnets (20×5×3 mm) into XLG-ROT-01 — alternating polarity!',
      'Inserted 20× N52 magnets into XLG-ROT-02 — mirror polarity to ROT-01!',
      'Wound 12 capsule coils (120–150 turns, 0.5 mm wire)',
      'Verified coil resistance ±5% between coils',
      'Inserted coils into stator pockets (XLG-STAT-01)',
      'Installed stator lid (XLG-STAT-02)',
      'Assembled rotor stack: spacer → stator → spacer',
      'Pressed bearing reducers (XLG-REDUZ-01/02) — 0.15 mm interference',
      'Test spin: rotor must spin freely, stator must not rotate',
      'LED test: 3-phase AC output visible at low RPM',
    ],
  },
  '03 Base Station': {
    id: 'build-guide-base',
    items: [
      'Printed all 6 base station parts',
      'Press-fit tapered roller bearing 32005 (29×50×15 mm) into XL-DECK-01',
      'Slid stator through U-form opening into slot at Z=25.8 mm',
      'Confirmed stator slot clearance (0.5 mm)',
      'Installed wall flanges XL-FLNSH-01 (3× required)',
      'Mounted PCB on standoffs in service hatch',
      'Routed cables through 10 mm cable port',
      'Attached maintenance hatch XL-KLAP-01',
      'Attached hatch floor XL-BODEN-01',
      'Final rotation test: 0 friction, 0 wobble',
    ],
  },
  '04 Final Assembly': {
    id: 'build-guide-final',
    items: [
      'Connected generator shaft to tower shaft (vielzahn coupling)',
      'Verified air gap: rotor 92 mm radius, inner chamber 96 mm (4 mm clearance)',
      'Blade assembly click-locked via 12-tooth spline',
      'Wiring connected to rectifier (3-phase AC → DC)',
      'Load test at low wind: LEDs or resistor bank',
      'Outdoor mounting secured (3× wall flanges)',
      'Safety check: no loose fasteners, no exposed conductors',
    ],
  },
  '05 Tools': {
    id: 'build-guide-tools',
    items: [
      'Built winding mandrel (correct capsule 22×8 mm core)',
      'Assembled Komplex-Spooler traversing mechanism (1:24 gear ratio)',
      'Tension test: magnet buffer braking at correct tension',
      'Wound test coil: 120 turns, 0.5 mm wire, measure resistance',
      'Coil dimensions match pocket: 40×26 mm outer',
    ],
  },
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function BuildGuidePage(): React.JSX.Element {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = buildGuideLinks[activeIndex];
  const checklist = SECTION_CHECKLISTS[active.title];
  const isTower = active.title === '01 Tower';

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
            {item.description && (
              <span className="sidebar-desc">{item.description}</span>
            )}
          </button>
        ))}
      </aside>

      <main className="reader-content">
        {/* Wing type comparison — only on Tower section */}
        {isTower && <WingTypeSwitcher />}

        {/* Markdown content */}
        <MarkdownRenderer content={getMarkdown(active.path)} />

        {/* Checklist — shown for every section that has one */}
        {checklist && (
          <Checklist id={checklist.id} items={checklist.items} />
        )}
      </main>
    </div>
  );
}
