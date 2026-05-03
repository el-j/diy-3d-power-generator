import React, { useRef, useEffect, useState } from 'react';
import type { RouteId } from '../hooks/useHashRoute';
import { initPlaygroundScene } from '../playground/initScene';

type Props = {
  navigate: (r: RouteId) => void;
};

export function PlaygroundPage({ navigate }: Props): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    return initPlaygroundScene(containerRef.current);
  }, []);

  return (
    <div className="pg-root">
      {/* Three.js canvas */}
      <div id="canvas-container" ref={containerRef} />

      {/* Loading overlay */}
      <div id="loader">
        <div className="spinner" />
        <div className="loader-text">ASSEMBLING TURBINE...</div>
      </div>

      {/* Part hover tooltip */}
      <div id="part-card">
        <div className="part-title" id="pc-title" />
        <div className="part-desc" id="pc-desc" />
      </div>

      {/* Mobile scene hint */}
      <div id="mobile-scene-hint" className="mobile-scene-hint" role="status" aria-live="polite">
        <span>Tap Inspect, Exploded, or Print Focus to switch camera modes.</span>
        <button id="mobile-scene-hint-dismiss" type="button">Got it</button>
      </div>

      {/* Fixed UI overlay */}
      <div id="ui-layer">
        {/* Left: title + lighting + scene modes + back */}
        <div className="header-panel">
          <h1>
            Helix Wind
            <br />
            Generator
          </h1>
          <p className="subtitle">
            Interactive open-source axial-flux wind generator with live physics and power
            estimation.
          </p>

         

          
          <div className="scene-mode-row">
            <button className="pg-back-btn" onClick={() => navigate('home')}>
            ← Overview
          </button>
            <button className="scene-mode-btn active" data-scene-mode="inspect">Inspect</button>
            <button className="scene-mode-btn" data-scene-mode="learn">Exploded</button>
            <button className="scene-mode-btn" data-scene-mode="print">Print Focus</button>
          </div>
          <div className="light-control">
              <label htmlFor="select-light-mode">Scene Light</label>
              <select id="select-light-mode" className="ui-select">
                <option value="current-light">Current Light (Local Time)</option>
                <option value="day">Day Boost</option>
                <option value="night">Night Focus</option>
                <option value="studio">Studio Contrast</option>
              </select>
              <p id="sun-status" className="sun-status">Finding local light profile...</p>
            </div>
        </div>
        

        {/* Right: full control panel */}
        <div 
          className={`control-panel ${isCollapsed ? 'collapsed' : ''}`}
          style={{ 
            transition: 'max-height 0.4s cubic-bezier(0.16, 1, 0.3, 1), padding 0.4s',
            maxHeight: isCollapsed ? '52px' : '900px',
            overflow: isCollapsed ? 'hidden' : 'visible'
          }}
        >
          <div 
            className="panel-header" 
            id="panel-header-toggle"
            onClick={() => setIsCollapsed(!isCollapsed)}
            style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          >
            <span>⚙️ Tower Configuration</span>
            <i className="panel-chevron" style={{ transition: 'transform 0.3s', transform: isCollapsed ? 'rotate(-180deg)' : 'none' }}>▲</i>
          </div>

          {/* Rotor type */}
          <div className="control-group">
            <div className="control-header"><span>Rotor Principle</span></div>
            <select id="select-rotor" className="ui-select" defaultValue="savonius-helix">
              <option value="savonius-helix">Savonius (Helical) – Drag Based</option>
              <option value="savonius-straight">Savonius (Straight) – Drag Based</option>
              <option value="lenz2">Lenz2 (Hybrid) – Lift &amp; Drag Based</option>
              <option value="darrieus-h">Darrieus (H-Rotor) – Lift Based</option>
              <option value="gorlov">Gorlov (Helical) – Max Lift Based</option>
            </select>
          </div>

          {/* Stages */}
          <div className="control-group compact-top">
            <div className="control-header">
              <span>Stages</span>
              <span className="val-display" id="val-stages">3</span>
            </div>
            <input type="range" id="slider-stages" min="1" max="8" defaultValue="3" step="1" />
            <div className="hint">Tower Height: <span id="val-height">720</span> mm</div>
          </div>

          {/* Generators */}
          <div className="control-group">
            <div className="control-header">
              <span>Generators</span>
              <span className="val-display" id="val-gens">1</span>
            </div>
            <input type="range" id="slider-gens" min="1" max="4" defaultValue="1" step="1" />
          </div>

          {/* Radius */}
          <div className="control-group">
            <div className="control-header">
              <span>Rotor Radius</span>
              <span className="val-display" id="val-radius">66 mm</span>
            </div>
            <input type="range" id="slider-radius" min="40" max="150" defaultValue="66" step="2" />
          </div>

          {/* Wind speed */}
          <div className="control-group compact-top">
            <div className="control-header">
              <span>Wind Speed</span>
              <span className="val-display" id="val-wind">6.0 m/s</span>
            </div>
            <input type="range" id="slider-wind" min="0" max="15" defaultValue="6" step="0.5" />
            <div className="preset-row">
              <button className="toggle-btn preset-btn" data-wind="4">Urban (4)</button>
              <button className="toggle-btn preset-btn active" data-wind="6">Suburban (6)</button>
              <button className="toggle-btn preset-btn" data-wind="9">Rural (9)</button>
            </div>
          </div>

          {/* Energy readout */}
          <div className="energy-card">
            <div className="energy-title">Estimated Power</div>
            <div className="energy-row">
              <span>Current Output:</span>
              <span className="energy-val large" id="val-power-w">-- W</span>
            </div>
            <div className="energy-row">
              <span>Aerodynamic Eff (Cp):</span>
              <span className="energy-val energy-small" id="val-cp">20%</span>
            </div>
            <div className="energy-row">
              <span>Rotor Speed:</span>
              <span className="energy-val energy-accent" id="val-rpm">-- RPM</span>
            </div>
            <div className="energy-row">
              <span>Annual Yield:</span>
              <span className="energy-val" id="val-power-kwh">-- kWh/yr</span>
            </div>
            <div className="energy-row energy-divider">
              <span>Charges approx:</span>
              <span className="energy-val energy-text" id="val-phones">2.5 phones/day</span>
            </div>
          </div>

          <div className="footnote">
            Estimates based on aerodynamic profile, eta=72% generator efficiency.
          </div>
        </div>
      </div>
    </div>
  );
}