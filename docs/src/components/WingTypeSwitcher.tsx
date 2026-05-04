import React, { useState } from 'react';
import { BLADE_TYPES, BETZ_LIMIT, ROTOR_TYPE_KEYS } from '../data/bladeTypes';

interface WingTypeSwitcherProps {
  selected?: string;
  onSelect?: (key: string) => void;
}

export function WingTypeSwitcher({ selected: controlledSelected, onSelect }: WingTypeSwitcherProps = {}): React.JSX.Element {
  const keys = ROTOR_TYPE_KEYS;
  const [internalKey, setInternalKey] = useState<string>(keys[0]);
  const activeKey = controlledSelected ?? internalKey;

  function handleSelect(key: string) {
    if (onSelect) {
      onSelect(key);
    } else {
      setInternalKey(key);
    }
  }

  const blade = BLADE_TYPES[activeKey as keyof typeof BLADE_TYPES] ?? BLADE_TYPES[keys[0]];
  const cpPct = (blade.cpValue / BETZ_LIMIT) * 100;

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
              ['Tip Speed Ratio', blade.tsrRange],
              ['Peak Efficiency (Cp)', blade.cpDisplay],
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
              {blade.cpDisplay}
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
