import * as THREE from 'three';
import { marked } from 'marked';
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
type SceneMode = 'inspect' | 'learn' | 'print';

interface BomData {
  totals: Record<string, string | number>;
  assemblies: Record<string, unknown>;
}

const bomData = bomDataRaw as BomData;

const markdownFiles = import.meta.glob('./**/*.md', {
  query: '?raw',
  import: 'default',
  eager: true
}) as Record<string, string>;

marked.setOptions({ gfm: true, breaks: false });

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
let currentSceneMode: SceneMode = 'inspect';
let lightMode: LightMode = 'current-light';
let userLocation: { lat: number; lon: number } | null = null;
let lastLightUpdateMs = 0;
let mobileViewport = window.matchMedia('(max-width: 980px)').matches;
let mobileHintTimer: ReturnType<typeof setTimeout> | null = null;

const MOBILE_HINT_KEY = 'helix-mobile-scene-hint-dismissed-v1';

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const partCard = document.getElementById('part-card') as HTMLDivElement;
let hoveredPart: TurbinePart | null = null;

const PART_CARD_W = 260;
const PART_CARD_H = 80;

const desiredCamera = new THREE.Vector3(60, 40, 80);
const desiredTarget = new THREE.Vector3(0, 30, 0);
const mobileSceneHintEl = document.getElementById('mobile-scene-hint') as HTMLDivElement | null;
const mobileSceneHintDismissEl = document.getElementById('mobile-scene-hint-dismiss') as HTMLButtonElement | null;

function setControlPanelCollapsed(collapsed: boolean): void {
  const controlPanel = document.querySelector<HTMLElement>('.control-panel');
  const panelChevron = document.getElementById('panel-chevron');
  if (!controlPanel) return;

  controlPanel.classList.toggle('collapsed', collapsed);
  if (panelChevron) panelChevron.textContent = collapsed ? '▼' : '▲';
}

function hideMobileSceneHint(persist = false): void {
  if (!mobileSceneHintEl) return;
  if (mobileHintTimer !== null) {
    clearTimeout(mobileHintTimer);
    mobileHintTimer = null;
  }

  mobileSceneHintEl.classList.remove('visible');
  if (persist) {
    localStorage.setItem(MOBILE_HINT_KEY, '1');
  }
}

function maybeShowMobileSceneHint(): void {
  if (!mobileSceneHintEl || !mobileViewport || currentRoute !== 'playground') {
    hideMobileSceneHint(false);
    return;
  }

  if (localStorage.getItem(MOBILE_HINT_KEY) === '1') {
    return;
  }

  if (mobileHintTimer !== null) {
    clearTimeout(mobileHintTimer);
  }

  mobileHintTimer = setTimeout(() => {
    if (mobileViewport && currentRoute === 'playground') {
      mobileSceneHintEl.classList.add('visible');
    }
  }, 700);
}

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

function applySceneMode(mode: SceneMode): void {
  currentSceneMode = mode;
  document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((button) => {
    button.classList.toggle('active', button.dataset.sceneMode === mode);
  });

  if (mode === 'inspect') {
    state.exploded = false;
    controls.autoRotate = false;
    if (mobileViewport) {
      desiredCamera.set(45, 30, 60);
    } else {
      desiredCamera.set(60, 40, 80);
    }
  }

  if (mode === 'learn') {
    state.exploded = true;
    controls.autoRotate = false;
    if (mobileViewport) {
      desiredCamera.set(48, 32, 62);
    } else {
      desiredCamera.set(52, 36, 65);
    }
  }

  if (mode === 'print') {
    state.exploded = false;
    controls.autoRotate = false;
    if (mobileViewport) {
      desiredCamera.set(36, 22, 43);
    } else {
      desiredCamera.set(42, 26, 48);
    }
  }

  refreshPhysicsUI();
}

function setSectionMode(sectionId: string): void {
  if (currentRoute !== 'playground' || mobileViewport) {
    return;
  }

  if (sectionId === 'hero') {
    controls.autoRotate = true;
    state.exploded = false;
    desiredCamera.set(70, 48, 94);
  }

  if (sectionId === 'playground') {
    applySceneMode('inspect');
  }

  if (sectionId === 'how-it-works') {
    applySceneMode('learn');
  }

  if (sectionId === 'print-it') {
    applySceneMode('print');
  }

  if (sectionId === 'contribute') {
    controls.autoRotate = true;
    state.exploded = false;
    desiredCamera.set(66, 44, 90);
  }

  refreshPhysicsUI();
}

function setupScrollytelling(): void {
  if (mobileViewport) {
    return;
  }

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
    applySceneMode(currentSceneMode);
    if (!mobileViewport) {
      controls.autoRotate = true;
    }
    maybeShowMobileSceneHint();
  } else {
    controls.autoRotate = false;
    state.exploded = false;
    partCard.style.opacity = '0';
    desiredCamera.set(54, 34, 66);
    hideMobileSceneHint(false);
  }

  if (mobileViewport) {
    setControlPanelCollapsed(true);
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function repoPathToLocalMarkdown(path: string): string {
  return path.startsWith('docs/') ? path.slice(5) : path;
}

function renderMarkdownInto(el: HTMLElement, markdown: string): void {
  el.innerHTML = marked.parse(markdown, { async: false }) as string;
}

function getMarkdown(path: string): string {
  const localPath = repoPathToLocalMarkdown(path);
  return markdownFiles[`./${localPath}`] ?? `# Missing File\n\nCould not find ${path} in bundled docs.`;
}

function renderDocsReader(): void {
  const list = document.getElementById('docs-list');
  const viewer = document.getElementById('docs-viewer');
  if (!list || !viewer) return;

  list.innerHTML = '';
  docsLinks.forEach((item, index) => {
    const button = document.createElement('button');
    button.textContent = item.title;
    button.classList.toggle('active', index === 0);
    button.addEventListener('click', () => {
      list.querySelectorAll('button').forEach((node) => node.classList.remove('active'));
      button.classList.add('active');
      renderMarkdownInto(viewer, getMarkdown(item.path));
    });
    list.appendChild(button);
  });

  renderMarkdownInto(viewer, getMarkdown(docsLinks[0].path));
}

function renderBuildGuideReader(): void {
  const list = document.getElementById('guide-list');
  const viewer = document.getElementById('guide-viewer');
  if (!list || !viewer) return;

  list.innerHTML = '';
  buildGuideLinks.forEach((item, index) => {
    const button = document.createElement('button');
    button.textContent = item.title;
    button.classList.toggle('active', index === 0);
    button.addEventListener('click', () => {
      list.querySelectorAll('button').forEach((node) => node.classList.remove('active'));
      button.classList.add('active');
      renderMarkdownInto(viewer, getMarkdown(item.path));
    });
    list.appendChild(button);
  });

  renderMarkdownInto(viewer, getMarkdown(buildGuideLinks[0].path));
}

function buildBomSummaryHtml(): string {
  const rows = Object.entries(bomData.assemblies)
    .map(([assemblyName, assemblyValue]) => {
      const count = countEntries(assemblyValue);
      return `<tr><td>${formatKey(assemblyName)}</td><td>${count}</td></tr>`;
    })
    .join('');

  return `
    <h3>BOM Summary</h3>
    <p>Live summary generated from docs/bom/master_bom.json.</p>
    <table>
      <thead><tr><th>Assembly</th><th>Entries</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderBom(): void {
  const totalsEl = document.getElementById('bom-totals');
  const viewer = document.getElementById('bom-viewer');
  const tabs = document.getElementById('bom-tabs');
  if (!totalsEl || !viewer || !tabs) return;

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

  const tabDefs = [
    {
      id: 'summary',
      label: 'Summary',
      render: () => {
        viewer.innerHTML = buildBomSummaryHtml();
      }
    },
    {
      id: 'markdown',
      label: 'BOM Markdown',
      render: () => {
        renderMarkdownInto(viewer, getMarkdown('docs/bom/master_bom.md'));
      }
    },
    {
      id: 'json',
      label: 'BOM JSON',
      render: () => {
        viewer.innerHTML = `<pre><code>${escapeHtml(JSON.stringify(bomDataRaw, null, 2))}</code></pre>`;
      }
    }
  ];

  tabs.innerHTML = '';
  tabDefs.forEach((tab, index) => {
    const button = document.createElement('button');
    button.textContent = tab.label;
    button.classList.toggle('active', index === 0);
    button.addEventListener('click', () => {
      tabs.querySelectorAll('button').forEach((node) => node.classList.remove('active'));
      button.classList.add('active');
      tab.render();
    });
    tabs.appendChild(button);
  });

  tabDefs[0].render();
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
  const modeBias = lightMode === 'studio' ? 0.1 : lightMode === 'night' ? 0.12 : 0;
  renderer.toneMappingExposure = Math.min(1.18, 0.86 + snapshot.brightness * 0.32 + modeBias);
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
      currentSceneMode = 'learn';
    } else {
      currentSceneMode = 'inspect';
      refreshPhysicsUI();
    }

    document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((button) => {
      button.classList.toggle('active', button.dataset.sceneMode === currentSceneMode);
    });
  }
});

const lightModeSelect = document.getElementById('select-light-mode') as HTMLSelectElement | null;
if (lightModeSelect) {
  lightModeSelect.addEventListener('change', () => {
    lightMode = lightModeSelect.value as LightMode;
    updateLighting(true);
  });
}

document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((button) => {
  button.addEventListener('click', () => {
    const mode = (button.dataset.sceneMode ?? 'inspect') as SceneMode;
    applySceneMode(mode);
    hideMobileSceneHint(true);
  });
});

if (mobileSceneHintDismissEl) {
  mobileSceneHintDismissEl.addEventListener('click', () => {
    hideMobileSceneHint(true);
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
  mobileViewport = window.matchMedia('(max-width: 980px)').matches;
  resizeScene();
  resizeFx();

  if (mobileViewport && currentRoute === 'playground') {
    applySceneMode(currentSceneMode);
    setControlPanelCollapsed(true);
    maybeShowMobileSceneHint();
  } else {
    hideMobileSceneHint(false);
  }
});

const panelHeaderToggle = document.getElementById('panel-header-toggle');
const controlPanelEl = document.querySelector<HTMLElement>('.control-panel');
if (panelHeaderToggle && controlPanelEl) {
  panelHeaderToggle.addEventListener('click', () => {
    const collapsed = !controlPanelEl.classList.contains('collapsed');
    setControlPanelCollapsed(collapsed);
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

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
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
  renderDocsReader();
  renderBom();
  renderDownloads();
  renderBuildGuideReader();

  if (mobileViewport) {
    setControlPanelCollapsed(true);
    maybeShowMobileSceneHint();
  }

  applyRoute(getRouteFromHash());
  applySceneMode('inspect');
  updateLighting(true);

  getUserLocation().then((location) => {
    if (location) {
      userLocation = location;
      updateLighting(true);
    }
  });

  animate();
}, 900);
