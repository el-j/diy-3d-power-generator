import React, { useState } from 'react';

interface BladeType {
  name: string;
  principle: string;
  blades: number;
  twist: string;
  tsr: string;
  cp: string;
  selfStarting: boolean;
  bestFor: string;
  partId: string;
  color: string;
  sourceFile: string;
}

const BLADE_TYPES: Record<string, BladeType> = {
  'savonius-helix': {
    name: 'Helix (Coreless)',
    principle: 'Hybrid drag/lift',
    blades: 1,
    twist: '90°',
    tsr: '1.0–1.5',
    cp: '~18%',
    selfStarting: true,
    bestFor: 'Variable/gusty wind, urban, low cut-in speed',
    partId: 'TWR-LEAF-01',
    color: '#6ce0ff',
    sourceFile: 'src/leaf/helix_leaf+connector.py',
  },
  'savonius-straight': {
    name: 'Savonius Straight',
    principle: 'Pure drag',
    blades: 2,
    twist: '0°',
    tsr: '0.8–1.0',
    cp: '~14%',
    selfStarting: true,
    bestFor: 'Very low wind, highest torque, pumping',
    partId: 'TWR-STR-01',
    color: '#ffd08b',
    sourceFile: 'src/leaf/savonius_straight_leaf.py',
  },
  'lenz2': {
    name: 'Lenz2 Cup',
    principle: 'Drag + vortex lift',
    blades: 3,
    twist: '0°',
    tsr: '1.2–1.8',
    cp: '~22%',
    selfStarting: true,
    bestFor: 'Urban turbulence, moderate efficiency',
    partId: 'TWR-LEN-01',
    color: '#a8ff78',
    sourceFile: 'src/leaf/lenz2_leaf.py',
  },
  'darrieus-h': {
    name: 'Darrieus H-Rotor',
    principle: 'Pure lift',
    blades: 3,
    twist: '0°',
    tsr: '3.0–4.0',
    cp: '~28%',
    selfStarting: false,
    bestFor: 'Consistent wind, efficiency priority',
    partId: 'TWR-DAR-01',
    color: '#ff8a3d',
    sourceFile: 'src/leaf/darrieus_h_leaf.py',
  },
  'gorlov': {
    name: 'Gorlov Helical',
    principle: 'Lift-drag hybrid',
    blades: 3,
    twist: '120°',
    tsr: '2.0–3.0',
    cp: '~32%',
    selfStarting: true,
    bestFor: 'Best efficiency + smooth power output',
    partId: 'TWR-GOR-01',
    color: '#c084fc',
    sourceFile: 'src/leaf/gorlov_leaf.py',
  },
};

const BETZ_LIMIT = 59.3;

function parseCpValue(cp: string): number {
  // e.g. "~18%" -> 18
  const match = cp.replace('~', '').replace('%', '').trim();
  return parseFloat(match) || 0;
}

interface WingTypeSwitcherProps {
  selected?: string;
  onSelect?: (key: string) => void;
}

export function WingTypeSwitcher({ selected: controlledSelected, onSelect }: WingTypeSwitcherProps = {}): React.JSX.Element {
  const keys = Object.keys(BLADE_TYPES);
  const [internalKey, setInternalKey] = useState<string>(keys[0]);
  const activeKey = controlledSelected ?? internalKey;

  function handleSelect(key: string) {
    if (onSelect) {
      onSelect(key);
    } else {
      setInternalKey(key);
    }
  }

  const blade = BLADE_TYPES[activeKey] ?? BLADE_TYPES[keys[0]];
  const cpValue = parseCpValue(blade.cp);
  const cpPct = (cpValue / BETZ_LIMIT) * 100;

  return (
    <div
      style={{
        border: '1px solid rgba(115,203,238,0.28)',
        borderRadius: 14,
        background: 'rgba(6,16,28,0.72)',
        padding: '1.1rem 1.25rem',
        marginBottom: '1.5rem',
      }}
    >
      {/* Title */}
      <p
        style={{
          margin: '0 0 0.9rem',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.7rem',
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          color: 'var(--accent)',
        }}
      >
        Blade Type Comparison
      </p>

      {/* Selector buttons */}
      <div
        className="tab-bar"
        style={{ marginTop: 0, marginBottom: '1rem', gap: '0.45rem' }}
      >
        {keys.map((key) => {
          const b = BLADE_TYPES[key];
          const isActive = key === activeKey;
          return (
            <button
              key={key}
              className={`tab-btn${isActive ? ' active' : ''}`}
              onClick={() => handleSelect(key)}
              style={{
                borderLeftWidth: 3,
                borderLeftStyle: 'solid',
                borderLeftColor: b.color,
                paddingLeft: '0.6rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
              }}
            >
              <span
                style={{
                  display: 'inline-block',
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: b.color,
                  flexShrink: 0,
                }}
              />
              {b.name}
            </button>
          );
        })}
      </div>

      {/* Detail card */}
      <div
        style={{
          border: `1px solid ${blade.color}44`,
          borderRadius: 12,
          background: 'rgba(6,14,26,0.7)',
          padding: '1rem 1.15rem',
          display: 'grid',
          gap: '0.9rem',
        }}
      >
        {/* Name + self-starting badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '1.18rem',
              fontWeight: 700,
              color: blade.color,
            }}
          >
            {blade.name}
          </span>
          {blade.selfStarting ? (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
                background: 'rgba(108,255,140,0.12)',
                border: '1px solid rgba(108,255,140,0.45)',
                borderRadius: 999,
                color: '#6dffb0',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                padding: '0.18rem 0.55rem',
                textTransform: 'uppercase',
              }}
            >
              <span style={{ fontSize: '0.85em' }}>✓</span> Self-starting
            </span>
          ) : (
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.3rem',
                background: 'rgba(255,100,100,0.1)',
                border: '1px solid rgba(255,100,100,0.4)',
                borderRadius: 999,
                color: '#ff7b7b',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.05em',
                padding: '0.18rem 0.55rem',
                textTransform: 'uppercase',
              }}
            >
              <span style={{ fontSize: '0.85em' }}>✗</span> Needs assist
            </span>
          )}
        </div>

        {/* Spec grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
            gap: '0.55rem',
          }}
        >
          {(
            [
              ['Operating Principle', blade.principle],
              ['Blades', String(blade.blades)],
              ['Blade Twist', blade.twist],
              ['Tip Speed Ratio', blade.tsr],
              ['Peak Efficiency (Cp)', blade.cp],
              ['Part ID', blade.partId],
            ] as [string, string][]
          ).map(([label, value]) => (
            <div
              key={label}
              style={{
                background: 'rgba(108,224,255,0.04)',
                border: '1px solid rgba(115,203,238,0.15)',
                borderRadius: 8,
                padding: '0.5rem 0.65rem',
              }}
            >
              <span
                style={{
                  display: 'block',
                  color: 'var(--muted)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.68rem',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                  marginBottom: '0.2rem',
                }}
              >
                {label}
              </span>
              <span
                style={{
                  display: 'block',
                  color: 'var(--text)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '0.92rem',
                  fontWeight: 700,
                }}
              >
                {value}
              </span>
            </div>
          ))}
        </div>

        {/* Best for */}
        <div>
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.68rem',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: 'var(--muted)',
            }}
          >
            Best for
          </span>
          <p
            style={{
              margin: '0.2rem 0 0',
              fontSize: '0.9rem',
              color: '#d8ecf8',
              lineHeight: 1.55,
            }}
          >
            {blade.bestFor}
          </p>
        </div>

        {/* Efficiency bar vs Betz limit */}
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '0.4rem',
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.68rem',
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                color: 'var(--muted)',
              }}
            >
              Efficiency vs. Betz limit ({BETZ_LIMIT}%)
            </span>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.76rem',
                color: blade.color,
                fontWeight: 700,
              }}
            >
              {blade.cp}
            </span>
          </div>
          {/* Track */}
          <div
            style={{
              height: 10,
              borderRadius: 5,
              background: 'rgba(115,203,238,0.12)',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            {/* Betz limit marker at 100% of track */}
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: 0,
                bottom: 0,
                width: 2,
                background: 'rgba(255,255,255,0.25)',
              }}
            />
            {/* Actual fill */}
            <div
              style={{
                height: '100%',
                width: `${cpPct}%`,
                background: `linear-gradient(90deg, ${blade.color}99, ${blade.color})`,
                borderRadius: 5,
                transition: 'width 0.35s ease',
              }}
            />
          </div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginTop: '0.25rem',
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.62rem',
                color: 'rgba(115,203,238,0.45)',
              }}
            >
              0%
            </span>
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.62rem',
                color: 'rgba(115,203,238,0.45)',
              }}
            >
              Betz {BETZ_LIMIT}%
            </span>
          </div>
        </div>

        {/* Source file */}
        <div>
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '0.68rem',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: 'var(--muted)',
              display: 'block',
              marginBottom: '0.3rem',
            }}
          >
            Source script
          </span>
          <code
            style={{
              display: 'inline-block',
              fontFamily: 'var(--font-mono)',
              background: 'rgba(108,224,255,0.12)',
              border: '1px solid rgba(108,224,255,0.24)',
              borderRadius: 6,
              padding: '0.15rem 0.5rem',
              fontSize: '0.82rem',
              color: '#a8deff',
            }}
          >
            {blade.sourceFile}
          </code>
        </div>
      </div>
    </div>
  );
}
