import * as THREE from 'three';
import { createSceneManager } from './src/scene/SceneManager';
import { createPostProcessing } from './src/scene/PostProcessing';
import { createMaterials, buildTower } from './src/assembly/HelixTower';
import { computeRPM } from './src/simulation/RotationPhysics';
import { computePower } from './src/simulation/PowerCalculator';
import { createWindSystem } from './src/simulation/WindSystem';
import { wireControls, updateEnergyUI } from './src/ui/Controls';
import { getUserLocation, setLightingMode, type LightMode } from './src/scene/EnvironmentLighting';
import { buildGuideLinks, docsLinks, downloadItems, toRepoBlobUrl, toRepoRawUrl } from './src/content/siteContent';
import type { AppState, TurbinePart } from './src/types';
import bomDataRaw from './bom/master_bom.json';

type RouteId = 'playground' | 'docs' | 'bom' | 'downloads' | 'build-guide';

interface BomData {
  totals: Record<string, string | number>;
  assemblies: Record<string, unknown>;
}

const bomData = bomDataRaw as BomData;

const state: AppState = {
  rotorType: 'savonius-helix',
  stages: 3,
  generators: 1,
  radius: 66,
  windSpeed: 6.0,
  targetRPM: 0,
  currentRPM: 0,
  exploded: false,
  parts: []
};

const container = document.getElementById('canvas-container') as HTMLDivElement;
const { scene, camera, renderer, controls, lightRig, resize: resizeScene } = createSceneManager(container);
const { composer, outlinePass, resize: resizeFx } = createPostProcessing(renderer, scene, camera);
const wind = createWindSystem(scene, 1200);
const mats = createMaterials();

const towerGroup = new THREE.Group();
scene.add(towerGroup);

let rotorMeshGroup: THREE.Group | null = null;
let currentRoute: RouteId = 'playground';
let lightMode: LightMode = 'current-light';
let userLocation: { lat: number; lon: number } | null = null;
let lastLightUpdateMs = 0;

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const partCard = document.getElementById('part-card') as HTMLDivElement;
let hoveredPart: TurbinePart | null = null;

const PART_CARD_W = 260;
const PART_CARD_H = 80;

const desiredCamera = new THREE.Vector3(60, 40, 80);
const desiredTarget = new THREE.Vector3(0, 30, 0);

function rebuildTower(): void {
  const result = buildTower(towerGroup, state, mats);
  state.parts = result.parts;
  rotorMeshGroup = result.rotorMeshGroup;
  desiredTarget.set(0, result.targetY, 0);
}

function refreshPhysicsUI(): void {
  const rpmInfo = computeRPM(state.rotorType, state.windSpeed, state.radius);
  state.targetRPM = state.exploded ? 0 : rpmInfo.rpm;

  const power = computePower({
    windSpeed: state.windSpeed,
    stages: state.stages,
    radiusMm: state.radius,
    cp: rpmInfo.cp,
    generators: state.generators
  });

  mats.copper.emissiveIntensity = Math.min(2.0, power.pOut / 20.0);
  updateEnergyUI({
    pOut: power.pOut,
    annualKwh: power.annualKwh,
    phonesPerDay: power.phonesPerDay,
    cp: rpmInfo.cp,
    rpm: state.currentRPM
  });
}

function setSectionMode(sectionId: string): void {
  if (currentRoute !== 'playground') {
    return;
  }

  if (sectionId === 'hero') {
    controls.autoRotate = true;
    state.exploded = false;
    desiredCamera.set(70, 48, 94);
  }

  if (sectionId === 'playground') {
    controls.autoRotate = false;
    state.exploded = false;
    desiredCamera.set(60, 40, 80);
  }

  if (sectionId === 'how-it-works') {
    controls.autoRotate = false;
    state.exploded = true;
    desiredCamera.set(52, 36, 65);
  }

  if (sectionId === 'print-it') {
    controls.autoRotate = false;
    state.exploded = false;
    desiredCamera.set(42, 26, 48);
  }

  if (sectionId === 'contribute') {
    controls.autoRotate = true;
    state.exploded = false;
    desiredCamera.set(66, 44, 90);
  }

  refreshPhysicsUI();
}

function setupScrollytelling(): void {
  const sections = Array.from(document.querySelectorAll<HTMLElement>('section.scene-section'));
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setSectionMode((entry.target as HTMLElement).id);
        }
      });
    },
    { threshold: 0.55 }
  );
  sections.forEach((section) => observer.observe(section));
}

function getRouteFromHash(): RouteId {
  const normalized = location.hash.replace(/^#\/?/, '').trim().toLowerCase();
  if (normalized === 'docs') return 'docs';
  if (normalized === 'bom') return 'bom';
  if (normalized === 'downloads') return 'downloads';
  if (normalized === 'build-guide') return 'build-guide';
  return 'playground';
}

function applyRoute(route: RouteId): void {
  currentRoute = route;
  document.body.dataset.route = route;

  document.querySelectorAll<HTMLElement>('[data-route]').forEach((section) => {
    section.classList.toggle('route-visible', section.dataset.route === route);
  });

  document.querySelectorAll<HTMLAnchorElement>('a[data-nav-link]').forEach((link) => {
    const href = link.getAttribute('href') ?? '';
    const active = href === `#/${route}`;
    link.classList.toggle('active', active);
  });

  if (route === 'playground') {
    controls.autoRotate = true;
    desiredCamera.set(66, 44, 90);
  } else {
    controls.autoRotate = false;
    state.exploded = false;
    partCard.style.opacity = '0';
    desiredCamera.set(54, 34, 66);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderDocsLinks(): void {
  const docsGrid = document.getElementById('docs-link-grid');
  if (!docsGrid) return;

  docsGrid.innerHTML = docsLinks
    .map((item) => {
      const href = toRepoBlobUrl(item.path);
      return `
        <article class="link-card">
          <h4>${item.title}</h4>
          <p>${item.description}</p>
          <a href="${href}" target="_blank" rel="noreferrer">Open source file</a>
        </article>
      `;
    })
    .join('');

  const guideGrid = document.getElementById('guide-link-grid');
  if (!guideGrid) return;

  guideGrid.innerHTML = buildGuideLinks
    .map((item) => {
      const href = toRepoBlobUrl(item.path);
      return `
        <article class="link-card">
          <h4>${item.title}</h4>
          <p>${item.description}</p>
          <a href="${href}" target="_blank" rel="noreferrer">Open guide file</a>
        </article>
      `;
    })
    .join('');
}

function renderBom(): void {
  const totalsEl = document.getElementById('bom-totals');
  const breakdownEl = document.getElementById('bom-breakdown');
  if (!totalsEl || !breakdownEl) return;

  totalsEl.innerHTML = Object.entries(bomData.totals)
    .map(([key, value]) => {
      return `
        <article class="metric-card">
          <p>${formatKey(key)}</p>
          <strong>${value}</strong>
        </article>
      `;
    })
    .join('');

  const assemblyCards = Object.entries(bomData.assemblies)
    .map(([assemblyName, assemblyValue]) => {
      const count = countEntries(assemblyValue);
      return `
        <article class="link-card">
          <h4>${formatKey(assemblyName)}</h4>
          <p>Registered entries: ${count}</p>
          <a href="${toRepoBlobUrl(`assemblies/${assemblyName}`)}" target="_blank" rel="noreferrer">Open assembly folder</a>
        </article>
      `;
    })
    .join('');

  breakdownEl.innerHTML =
    assemblyCards +
    `
      <article class="link-card">
        <h4>Master BOM Source</h4>
        <p>Use markdown for reading and JSON for automation, scripts, and external integrations.</p>
        <a href="${toRepoBlobUrl('docs/bom/master_bom.md')}" target="_blank" rel="noreferrer">Open BOM markdown</a>
      </article>
      <article class="link-card">
        <h4>Machine-Readable BOM</h4>
        <p>Structured inventory data with assembly-specific part definitions.</p>
        <a href="${toRepoRawUrl('docs/bom/master_bom.json')}" target="_blank" rel="noreferrer">Download BOM JSON</a>
      </article>
    `;
}

function renderDownloads(): void {
  const grid = document.getElementById('download-grid');
  if (!grid) return;

  const cards = downloadItems
    .map((item) => {
      const category = item.category.toUpperCase();
      return `
        <article class="download-card">
          <span class="download-tag">${category}</span>
          <h4>${item.label}</h4>
          <p>${item.path}</p>
          <a href="${toRepoRawUrl(item.path)}" target="_blank" rel="noreferrer">Direct Download</a>
          <br>
          <a href="${toRepoBlobUrl(item.path)}" target="_blank" rel="noreferrer">View in GitHub</a>
        </article>
      `;
    })
    .join('');

  grid.innerHTML =
    cards +
    `
      <article class="download-card">
        <span class="download-tag">FULL EXPORTS</span>
        <h4>Complete Exports Directory</h4>
        <p>Browse all generated STL/3MF artifacts directly in the repository tree.</p>
        <a href="${toRepoBlobUrl('exports')}" target="_blank" rel="noreferrer">Open exports folder</a>
      </article>
    `;
}

function updateLighting(force = false): void {
  const nowMs = performance.now();
  if (!force && nowMs - lastLightUpdateMs < 1000) {
    return;
  }
  lastLightUpdateMs = nowMs;

  const snapshot = setLightingMode(scene, lightRig, lightMode, new Date(), userLocation);
  renderer.toneMappingExposure = 0.9 + snapshot.brightness * 0.35;
  document.body.dataset.sunPhase = snapshot.phase;

  const statusEl = document.getElementById('sun-status');
  if (statusEl) {
    const region = userLocation ? `lat ${userLocation.lat.toFixed(1)}` : 'timezone fallback';
    statusEl.textContent = `${snapshot.phase.toUpperCase()} | brightness ${(snapshot.brightness * 100).toFixed(0)}% | ${region}`;
  }
}

wireControls(state, {
  onGeometryChanged: () => {
    rebuildTower();
    refreshPhysicsUI();
  },
  onPhysicsChanged: refreshPhysicsUI,
  onExplodeToggle: () => {
    if (state.exploded) {
      state.targetRPM = 0;
    } else {
      refreshPhysicsUI();
    }
  }
});

const lightModeSelect = document.getElementById('select-light-mode') as HTMLSelectElement | null;
if (lightModeSelect) {
  lightModeSelect.addEventListener('change', () => {
    lightMode = lightModeSelect.value as LightMode;
    updateLighting(true);
  });
}

window.addEventListener('hashchange', () => {
  applyRoute(getRouteFromHash());
});

window.addEventListener('mousemove', (event: MouseEvent) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  partCard.style.left = `${Math.min(event.clientX + 20, window.innerWidth - PART_CARD_W)}px`;
  partCard.style.top = `${Math.min(event.clientY + 20, window.innerHeight - PART_CARD_H)}px`;
});

let partCardHideTimer: ReturnType<typeof setTimeout> | null = null;
window.addEventListener('touchend', (event: TouchEvent) => {
  if (event.changedTouches.length === 0 || currentRoute !== 'playground') return;
  const touch = event.changedTouches[0];
  mouse.x = (touch.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(touch.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersections = raycaster.intersectObjects(state.parts, false);
  if (intersections.length > 0) {
    const hit = intersections[0].object as TurbinePart;
    hoveredPart = hit;
    outlinePass.selectedObjects = [hoveredPart];
    (document.getElementById('pc-title') as HTMLElement).innerText = hoveredPart.userData.name;
    (document.getElementById('pc-desc') as HTMLElement).innerText = hoveredPart.userData.desc;

    partCard.style.left = `${Math.min(touch.clientX + 20, window.innerWidth - PART_CARD_W)}px`;
    partCard.style.top = `${Math.min(touch.clientY + 20, window.innerHeight - PART_CARD_H)}px`;
    partCard.style.opacity = '1';

    if (partCardHideTimer !== null) clearTimeout(partCardHideTimer);
    partCardHideTimer = setTimeout(() => {
      partCard.style.opacity = '0';
      hoveredPart = null;
      outlinePass.selectedObjects = [];
    }, 3000);
  }
});

window.addEventListener('resize', () => {
  resizeScene();
  resizeFx();
});

const panelHeaderToggle = document.getElementById('panel-header-toggle');
const controlPanelEl = document.querySelector<HTMLElement>('.control-panel');
const panelChevronEl = document.getElementById('panel-chevron');
if (panelHeaderToggle && controlPanelEl) {
  panelHeaderToggle.addEventListener('click', () => {
    const collapsed = controlPanelEl.classList.toggle('collapsed');
    if (panelChevronEl) panelChevronEl.textContent = collapsed ? '▼' : '▲';
  });
}

const clock = new THREE.Clock();
function animate(): void {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();

  camera.position.lerp(desiredCamera, 0.04);
  controls.target.lerp(desiredTarget, 0.04);

  state.currentRPM += (state.targetRPM - state.currentRPM) * delta * 0.5;
  if (rotorMeshGroup && !state.exploded) {
    const visualRps = (state.currentRPM / 60) * 0.2;
    rotorMeshGroup.rotation.y -= visualRps * Math.PI * 2 * delta;
  }

  state.parts.forEach((part) => {
    const targetY = state.exploded ? part.userData.explodedY : part.userData.assembledY;
    part.position.y += (targetY - part.position.y) * delta * 5.0;
  });

  if (currentRoute === 'playground') {
    raycaster.setFromCamera(mouse, camera);
    const intersections = raycaster.intersectObjects(state.parts, false);
    if (intersections.length > 0) {
      const next = intersections[0].object as TurbinePart;
      if (hoveredPart !== next) {
        hoveredPart = next;
        outlinePass.selectedObjects = [hoveredPart];
        (document.getElementById('pc-title') as HTMLElement).innerText = hoveredPart.userData.name;
        (document.getElementById('pc-desc') as HTMLElement).innerText = hoveredPart.userData.desc;
        partCard.style.opacity = '1';
      }
    } else if (hoveredPart) {
      hoveredPart = null;
      outlinePass.selectedObjects = [];
      partCard.style.opacity = '0';
    }
  }

  updateLighting();
  wind.update(delta, state.windSpeed);
  controls.update();
  refreshPhysicsUI();
  composer.render();
}

function formatKey(key: string): string {
  return key
    .replaceAll('_', ' ')
    .replace(/(^|\s)\S/g, (letter) => letter.toUpperCase());
}

function countEntries(value: unknown): number {
  if (Array.isArray(value)) return value.length;
  if (value && typeof value === 'object') {
    return Object.values(value).reduce((sum, child) => sum + countEntries(child), 0);
  }
  return 0;
}

setTimeout(() => {
  const loader = document.getElementById('loader') as HTMLDivElement;
  loader.style.opacity = '0';
  setTimeout(() => {
    loader.style.display = 'none';
  }, 500);

  rebuildTower();
  refreshPhysicsUI();
  setupScrollytelling();
  renderDocsLinks();
  renderBom();
  renderDownloads();

  applyRoute(getRouteFromHash());
  updateLighting(true);

  getUserLocation().then((location) => {
    if (location) {
      userLocation = location;
      updateLighting(true);
    }
  });

  animate();
}, 900);
