# 🌬️ Interactive Landing Page — Full Design & Orchestration Plan

> Target: GitHub Pages · Technology: Three.js · Goal: Industry-grade immersive 3D experience
> Audience: Makers, engineers, open-source energy enthusiasts worldwide

---

## Vision Statement

A **single-page experience** where the Helix Wind Generator comes to life in the browser. Wind blows, the helix spins, the user builds their own tower and understands how much energy they can harvest. Not a documentation page — a **playground**.

---

## 1. Architecture Overview

```
/docs (GitHub Pages root)
├── index.html              ← single HTML shell
├── main.js                 ← scene orchestration entry point
├── style.css               ← minimal base styles
├── assets/
│   ├── models/
│   │   ├── helix_leaf.glb          ← one blade stage
│   │   ├── connector.glb           ← stage connector
│   │   ├── generator.glb           ← generator assembly
│   │   ├── base_station.glb        ← housing
│   │   └── vielzahn_plug.glb       ← plug detail
│   ├── textures/
│   │   ├── petg_normal.jpg         ← FDM surface normal map
│   │   ├── carbon_fiber.jpg        ← PLA-CF visual
│   │   └── hdri_sky.hdr            ← environment lighting
│   └── data/
│       └── wind_power_curve.json   ← Cp/wind-speed data
├── src/
│   ├── scene/
│   │   ├── SceneManager.js         ← Three.js setup, renderer, camera
│   │   ├── Lighting.js             ← HDRI + directional lights
│   │   └── PostProcessing.js       ← bloom, chromatic aberration
│   ├── assembly/
│   │   ├── HelixTower.js           ← procedural tower builder
│   │   ├── GeneratorStack.js       ← generator assembly
│   │   └── BaseStation.js          ← base housing
│   ├── simulation/
│   │   ├── WindSystem.js           ← particle wind field
│   │   ├── RotationPhysics.js      ← RPM from wind speed
│   │   └── PowerCalculator.js      ← energy output math
│   ├── ui/
│   │   ├── Controls.js             ← floating UI panel
│   │   ├── Tooltip.js              ← part hover labels
│   │   └── EnergyDisplay.js        ← live watt/kWh readout
│   └── export/
│       └── STLExportLink.js        ← deep links to STL files
```

---

## 2. 3D Scene Design

### 2.1 Camera & Environment

- **Camera**: PerspectiveCamera, FOV 45°, near 0.1 / far 500
- **Default view**: Slight angle (15° tilt, 30° yaw) — shows blades AND generator
- **Controls**: OrbitControls with damping (0.05) — smooth, weighted inertia
- **Auto-rotate**: Slow 0.2°/s when idle > 5s, stops on any interaction
- **Environment**: HDR sky — sunny day, light clouds, subtle blue atmosphere
- **Ground plane**: Faint circular concrete pad under base station, dissolves at distance
- **Depth of field**: Subtle — background slightly out of focus (BokehPass)

### 2.2 Materials

All parts use PBR materials matching printed appearance:

| Part group | Material preset | Properties |
|------------|----------------|------------|
| Helix blades (TWR-LEAF) | Translucent PETG, light teal | roughness 0.3, metalness 0.0, transmission 0.15 |
| Connectors, plugs | Matte grey PETG | roughness 0.7, metalness 0.05 |
| Rotors, backplates | Carbon-fiber PLA-CF | roughness 0.4, metalness 0.2, normal map |
| Stator | White/cream PETG | roughness 0.65, metalness 0.0 |
| Base housing | Dark grey PETG | roughness 0.6, metalness 0.05 |
| Metal fasteners | Silver steel | roughness 0.25, metalness 0.9 |
| Generator wiring | Copper lacquered | roughness 0.3, metalness 0.8, emissive orange glow at power |

### 2.3 Animation System

**LayerAnimation** — each part has 3 states:
1. `assembled` — final position
2. `exploded` — radially separated along axis (toggle with E key or UI button)
3. `highlighted` — scale 1.05, outline glow, tooltip visible

**RotationLoop** (always running when wind > 0):
- Driven by `RotationPhysics.getRPM(windSpeed)`
- Helix stages counter-rotate in pairs if tower is >2 stages (authentic VAWT behavior)
- Generator rotors rotate at same RPM
- Smooth acceleration/deceleration curve (exponential ease, τ=1.5s)

---

## 3. Wind Simulation System

### 3.1 Visual Wind Particles

**WindSystem.js** — GPU particle system (InstancedMesh, 2000 particles):

- Particles spawn at random positions in a cylinder above the scene (R=200mm, H=150mm)
- Direction: primarily horizontal, slight Z variance (±15°), swirl component
- Speed multiplied by user `windSpeed` slider (0–15 m/s range)
- Particle length: proportional to velocity (trailing tail via custom ShaderMaterial)
- Color: white → light blue at high speed
- In "randomized wind" mode: speed follows a Weibull distribution k=2, λ=user mean — stochastic bursts with smooth blending

**Wind gust events** (random mode only):
- Every 8–30s, a gust event → wind speed ramps +50% over 2s, holds 3s, drops back
- Particle density increases during gust
- Blades visibly accelerate then return to steady-state

### 3.2 Rotation Physics

```javascript
// RotationPhysics.js
const getTSR = (windSpeed) => 1.8;  // tip-speed ratio for Savonius helix
const getOmega = (windSpeed, bladeRadius = 0.066) => {  // R=66mm
  return (getTSR(windSpeed) * windSpeed) / bladeRadius;  // rad/s
};
const getRPM = (windSpeed) => (getOmega(windSpeed) / (2 * Math.PI)) * 60;
// Result: at 5 m/s wind → ~2340 RPM for a 66mm radius blade (high speed, realistic for VAWT)
// In 3D: scale by visual factor 0.1× for readable animation
```

---

## 4. Energy Calculator

### 4.1 Physics Model

```
P_wind   = 0.5 × ρ × A × v³           (available power in wind)
P_output = Cp × P_wind × η_generator   (harvested power)

Where:
  ρ          = 1.225 kg/m³ (air at sea level)
  A          = swept_area (height × diameter of helix column)
  v          = wind speed (m/s)
  Cp         = power coefficient = 0.25 (Savonius VAWT, realistic)
  η_generator = 0.72 (axial flux generator efficiency estimate)

swept_area = tower_height × (2 × blatt_radius)
           = (num_stages × 240mm) × (2 × 66mm)
           = num_stages × 0.240 × 0.132 m²

Annual energy = P_output × 8760 × capacity_factor
capacity_factor ≈ 0.25 (urban/suburban, Weibull distribution integrated)
```

### 4.2 UI Controls (floating glass panel, right side)

```
┌─────────────────────────────────────┐
│  ⚙️  Tower Configuration            │
│                                     │
│  Stages:  [──●──────] 3  (1–8)      │
│  Height shown:  720mm               │
│                                     │
│  Generators: [──●──] 1  (1–3)       │
│                                     │
│  Wind:  ○ Random  ● Fixed           │
│  Speed: [───●────] 6.0 m/s          │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  ⚡ Estimated Power          │    │
│  │  Current:    14.2 W         │    │
│  │  Annual:     31 kWh/year    │    │
│  │  Charges ~:  2.5 phones/day │    │
│  └─────────────────────────────┘    │
│                                     │
│  Wind Conditions:                   │
│  ○ Urban rooftop  (avg 4 m/s)       │
│  ● Suburban open  (avg 6 m/s)       │
│  ○ Rural exposed  (avg 8 m/s)       │
│  ○ Custom ──────────────────        │
└─────────────────────────────────────┘
```

### 4.3 Real-time Feedback

- Power readout updates on every slider change (<16ms, runs in RAF)
- "Charges phones/day" and "powers LED bulbs" as approachable analogies
- Annual kWh bar chart — tiny sparkline showing seasonal variation (monthly distribution using Weibull)
- Color coding: green (meaningful output), yellow (marginal), grey (insufficient wind)

---

## 5. Interactive Part Explorer

### 5.1 Exploded View Toggle

- Button: "Explore Parts" → triggers staggered explosion animation (300ms offset per group)
- Parts spread outward along assembly axis
- Each part floats with slow bob animation (±3mm, 2.5s period)
- Click any part → zoom camera to it + show part card

### 5.2 Part Card (on click)

```
┌────────────────────────────────────────┐
│  🖨️  XLG-ROT-01                        │
│  Rotor Oben (Aero-Fan)                 │
│  ─────────────────────────────────     │
│  Material: PLA-CF                      │
│  Infill:   30%                         │
│  Print time: ~4h (0.6mm nozzle)        │
│  Key dims: Ø184mm · 10mm thick         │
│  11 fan blades · 20 magnet pockets     │
│  ─────────────────────────────────     │
│  [ ⬇ Download STL ]  [ 📋 View BOM ]  │
└────────────────────────────────────────┘
```

### 5.3 Assembly Sequence Mode

- Button: "Watch Assembly" → animated build sequence
- Parts fly in from below, one at a time, in correct assembly order
- Text annotation appears for each: "Step 3: Press heat-set nuts into clamp collar"
- Duration: ~45 seconds total at normal speed (0.5× and 2× speed options)
- Narrated visually — no audio needed, just text overlays + arrow indicators

---

## 6. Visual Effects Stack

### 6.1 Post-Processing Pipeline (EffectComposer)

```
Renderer → RenderPass
         → SSAOPass        (subtle ambient occlusion between parts)
         → UnrealBloomPass  (bloom on emissive copper wires + LED indicator)
         → FXAAPass        (anti-aliasing)
         → Output
```

### 6.2 Part Glow on Hover

- Custom OutlinePass (Three.js postprocessing) — bright teal outline on hovered part
- Thickness: 2px at any zoom level (screenspace)
- Color: `#00e5ff` (electric blue-teal)

### 6.3 Energy Visualization

When power output > 0W:
- Copper coil wires in stator emit pulsing orange glow (emissive intensity ∝ power)
- Thin animated arcs (custom ShaderMaterial, TextureAnimator) sweep from stator to output cable
- Intensity scales with RPM
- At max power (>20W): slight color temperature shift in scene lighting (warmer)

### 6.4 Atmosphere

- Sky: custom gradient shader, not an HDR texture (loads fast, fully procedural)
  - Zenith: `#0a1628` (deep night blue) → Horizon: `#4a8ab5` (sky blue) with atmospheric scatter
- Subtle lens flare on sun position (LensFlare addon)
- Scene fog: `THREE.FogExp2`, density 0.002 — fades background to sky color

---

## 7. Performance Strategy

| Concern | Approach |
|---------|----------|
| GLB model size | Target <500KB total compressed. Bake AO into vertex colors. |
| Mobile GPU | SSAO off on mobile. Bloom threshold higher. Particle count 500 (vs 2000). |
| First load | Lazy load models after initial paint. Show spinner with "Loading 3D models..." |
| 60fps target | InstancedMesh for blade array. Merge static geometry. Skip RAF frame if tab hidden. |
| Old browsers | Graceful fallback: static hero image if WebGL not available. |
| GLB generation | FreeCAD → export to STL → Blender (script) → apply PBR materials → export GLB |

### LOD Strategy
- Blade stage: 2 LODs (full detail <30m camera dist, simplified >30m)
- Generator: single detail (always visible and close)
- Base station: simplified at >60m distance

---

## 8. Page Structure

```html
<!-- Single page, sections stacked vertically -->

<section id="hero">
  <!-- Full viewport canvas -->
  <!-- Overlay: "Helix Wind Generator" title + one-liner -->
  <!-- Scroll indicator: "↓ Explore" -->
</section>

<section id="playground">
  <!-- 3D canvas stays sticky -->
  <!-- Controls panel slides in from right -->
  <!-- Energy display at bottom left -->
</section>

<section id="how-it-works">
  <!-- Split: 3D exploded view (left) + text steps (right) -->
  <!-- Scrollytelling: each scroll step highlights next assembly stage -->
</section>

<section id="print-it">
  <!-- BOM table with STL download links -->
  <!-- Printer requirements card -->
  <!-- "Start with" recommendation (Easy-Tool first!) -->
</section>

<section id="contribute">
  <!-- GitHub stars widget -->
  <!-- License badge -->
  <!-- Link to CLAUDE.md for agents/contributors -->
</section>
```

### Scrollytelling Engine
Use **Intersection Observer API** (no scroll-jacking, respects accessibility):
- Each `<section>` triggers scene state changes
- `#playground` entry → start wind simulation
- Scroll within `#how-it-works` → step through assembly sequence
- `#print-it` → camera zooms into stator detail

---

## 9. GitHub Pages Setup

### Repository Structure
```
/docs/          ← GitHub Pages source
  index.html
  main.js
  style.css
  assets/...
  src/...
```

### `index.html` Head
```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="Helix Wind Generator — 3D Printable">
<meta property="og:description" content="Open-source axial-flux wind generator. Print, assemble, generate.">
<meta property="og:image" content="assets/og_preview.png"> <!-- static render -->
<title>Helix Wind Generator</title>
```

### Build Process (no build tool needed for GitHub Pages)
- Three.js via **importmap** (no bundler):
```html
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }
}
</script>
```
- All source files as ES modules — native browser import, no webpack
- GLB models loaded via `GLTFLoader` from Three.js addons

---

## 10. GLB Model Generation Pipeline

**Step 1: FreeCAD → STL**
- Run `src/generator/helix_generator.py` in FreeCAD → export individual STLs to `exports/generator/`
- Same for `src/base/helix_station.py` and `src/leaf/helix_leaf+connector.py`

**Step 2: STL → Blender (automated script)**
```python
# docs/scripts/stl_to_glb.py — run in Blender headless
# For each STL: import → assign PBR material → decimate to target polycount → export GLB
# Target: single combined GLB per assembly group
```

**Step 3: Combine into scene GLBs**
- `helix_leaf.glb` — ONE blade stage (replicated procedurally in JS)
- `generator.glb` — full generator assembly (merged)
- `base_station.glb` — housing only
- `connector.glb` — stage connector disc

**Step 4: Check file size**
- Target: all GLBs combined < 2MB (users on mobile connections)
- Use Draco compression (Three.js has DRACOLoader)

---

## 11. Implementation Phases

### Phase 1 — Static 3D Scene (Week 1)
- [ ] Set up `docs/` directory structure
- [ ] Configure GitHub Pages to serve from `docs/`
- [ ] Basic Three.js scene: canvas, camera, lights, OrbitControls
- [ ] Convert one blade STL to GLB (manual Blender workflow)
- [ ] Load and render the blade, apply PETG material
- [ ] Deploy to GitHub Pages — verify HTTPS loads correctly

### Phase 2 — Full Assembly (Week 2)
- [ ] Convert all required STLs to GLBs (Blender script)
- [ ] Build HelixTower.js — procedural stacking of N stages
- [ ] Add GeneratorStack.js and BaseStation.js
- [ ] Implement rotation animation driven by a fixed RPM
- [ ] Smooth OrbitControls with damping

### Phase 3 — Wind Simulation (Week 3)
- [ ] WindSystem.js — particle field
- [ ] RotationPhysics.js — RPM from wind speed
- [ ] Connect slider → wind speed → RPM → particle speed → rotation
- [ ] Random wind mode (Weibull gust events)
- [ ] Post-processing: SSAO, bloom, FXAA

### Phase 4 — UI & Calculator (Week 4)
- [ ] Floating control panel (pure CSS, no framework)
- [ ] Tower stage count slider → rebuild tower procedurally
- [ ] Generator count slider
- [ ] PowerCalculator.js — live energy readout
- [ ] Wind condition presets
- [ ] Mobile responsive layout

### Phase 5 — Part Explorer & Polish (Week 5)
- [ ] Exploded view animation
- [ ] Part click → tooltip card
- [ ] Assembly sequence animation
- [ ] Scrollytelling sections
- [ ] OG image for GitHub/Twitter sharing
- [ ] Performance audit — 60fps on mid-range mobile

### Phase 6 — Launch (Week 6)
- [ ] Cross-browser test (Chrome, Firefox, Safari, Edge)
- [ ] Performance profiling (Lighthouse)
- [ ] Accessibility: keyboard navigation, reduced-motion media query stops animations
- [ ] README updated with landing page link + preview screenshot

---

## 12. Design Tokens (CSS)

```css
:root {
  --color-bg:       #0a0f1e;   /* deep navy */
  --color-surface:  #12192e;   /* card backgrounds */
  --color-accent:   #00e5ff;   /* electric teal — primary accent */
  --color-energy:   #ff6b35;   /* orange — power/energy indicators */
  --color-text:     #e8f0fe;   /* near-white */
  --color-muted:    #8899aa;   /* secondary text */

  --font-display:   'Space Grotesk', system-ui;
  --font-body:      'Inter', system-ui;
  --font-mono:      'JetBrains Mono', monospace;

  --radius-card:    12px;
  --blur-glass:     backdrop-filter: blur(12px);
  --shadow-glow:    0 0 30px rgba(0, 229, 255, 0.15);
}
```

**Control panel**: glass morphism — `background: rgba(18,25,46,0.75)`, backdrop-filter blur, 1px border in accent color at 20% opacity. Feels like a HUD, not a form.

---

## 13. Energy Calculator — Accuracy Notes

The output numbers are **estimates**, not guarantees. Display clearly:

```
⚠️ Estimates based on Cp=0.25 (Savonius VAWT), η=72% generator efficiency.
   Actual output depends on site conditions, bearing friction, wire resistance,
   and air density at your altitude.
```

Real power curve data from literature (Cp vs TSR for Savonius) should be loaded from `assets/data/wind_power_curve.json` to replace the simplified formula in production.

---

## 14. Bonus Delight Details

- **Easter egg**: Konami code (↑↑↓↓←→←→BA) → all blades go max speed + rainbow color mode
- **Magnetic field visualization**: toggle to show simulated B-field lines between rotor magnets (animated sine-wave lines in magenta)
- **X-ray mode**: toggle to see through housing to internal generator components (material opacity → 0.15)
- **Sound**: opt-in Web Audio API wind whoosh — generated via oscillator (no audio file needed), pitch rises with RPM
- **Share button**: generates a URL with config encoded in query params (`?stages=4&generators=2&wind=7.5`) — bookmarkable and shareable
