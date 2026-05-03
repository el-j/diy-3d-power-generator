import React, { useState, useEffect, useCallback } from 'react';

export interface ChecklistProps {
  id: string;
  items: string[];
}

export function Checklist({ id, items }: ChecklistProps): React.JSX.Element {
  const storageKey = `checklist-${id}`;

  const loadChecked = useCallback((): boolean[] => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const parsed = JSON.parse(raw) as boolean[];
        if (Array.isArray(parsed) && parsed.length === items.length) {
          return parsed;
        }
      }
    } catch {
      // ignore parse errors
    }
    return items.map(() => false);
  }, [storageKey, items]);

  const [checked, setChecked] = useState<boolean[]>(loadChecked);

  // Sync to localStorage whenever checked changes
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(checked));
    } catch {
      // quota exceeded or similar
    }
  }, [storageKey, checked]);

  // Re-init if item count changes (e.g. different section loaded)
  useEffect(() => {
    setChecked(loadChecked());
  }, [loadChecked]);

  const completedCount = checked.filter(Boolean).length;
  const total = items.length;
  const pct = total === 0 ? 0 : Math.round((completedCount / total) * 100);

  function toggle(index: number) {
    setChecked((prev) => {
      const next = [...prev];
      next[index] = !next[index];
      return next;
    });
  }

  function resetAll() {
    setChecked(items.map(() => false));
  }

  return (
    <div
      style={{
        border: '1px solid rgba(115,203,238,0.28)',
        borderRadius: 14,
        background: 'rgba(6,16,28,0.72)',
        padding: '1.1rem 1.25rem',
        marginTop: '1.5rem',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '0.85rem',
          gap: '0.75rem',
          flexWrap: 'wrap',
        }}
      >
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.7rem',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            color: 'var(--accent)',
          }}
        >
          Build Checklist
        </span>
        <span
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.76rem',
            color: 'var(--muted)',
          }}
        >
          {completedCount} / {total} completed
        </span>
      </div>

      {/* Progress bar */}
      <div
        style={{
          height: 6,
          borderRadius: 3,
          background: 'rgba(115,203,238,0.14)',
          marginBottom: '1rem',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: 'linear-gradient(90deg, var(--accent), #bcffcb)',
            borderRadius: 3,
            transition: 'width 0.3s ease',
          }}
        />
      </div>

      {/* Items */}
      <ul
        style={{
          listStyle: 'none',
          margin: 0,
          padding: 0,
          display: 'grid',
          gap: '0.45rem',
        }}
      >
        {items.map((item, i) => (
          <li key={i}>
            <label
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.65rem',
                cursor: 'pointer',
                padding: '0.38rem 0.5rem',
                borderRadius: 8,
                transition: 'background 0.12s',
                background: checked[i] ? 'rgba(108,224,255,0.05)' : 'transparent',
              }}
            >
              <input
                type="checkbox"
                checked={checked[i] ?? false}
                onChange={() => toggle(i)}
                style={{
                  marginTop: '0.18rem',
                  accentColor: 'var(--accent)',
                  width: 15,
                  height: 15,
                  flexShrink: 0,
                  cursor: 'pointer',
                }}
              />
              <span
                style={{
                  fontSize: '0.88rem',
                  lineHeight: 1.5,
                  color: checked[i] ? 'var(--muted)' : '#d8ecf8',
                  textDecoration: checked[i] ? 'line-through' : 'none',
                  opacity: checked[i] ? 0.55 : 1,
                  transition: 'color 0.15s, opacity 0.15s',
                }}
              >
                {item}
              </span>
            </label>
          </li>
        ))}
      </ul>

      {/* Reset button */}
      <div style={{ marginTop: '0.9rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button
          onClick={resetAll}
          disabled={completedCount === 0}
          style={{
            background: 'none',
            border: '1px solid rgba(115,203,238,0.3)',
            borderRadius: 999,
            color: completedCount === 0 ? 'rgba(115,203,238,0.3)' : 'var(--muted)',
            cursor: completedCount === 0 ? 'default' : 'pointer',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.72rem',
            fontWeight: 700,
            letterSpacing: '0.05em',
            padding: '0.3rem 0.8rem',
            textTransform: 'uppercase',
            transition: 'color 0.15s, border-color 0.15s',
          }}
        >
          Reset progress
        </button>
      </div>
    </div>
  );
}
