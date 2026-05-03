import * as THREE from 'three';
import { createSceneManager } from '../scene/SceneManager';
import { createPostProcessing } from '../scene/PostProcessing';
import { createMaterials, buildTower } from '../assembly/HelixTower';
import { computeRPM } from '../simulation/RotationPhysics';
import { computePower } from '../simulation/PowerCalculator';
import { createWindSystem } from '../simulation/WindSystem';
import { wireControls, updateEnergyUI } from '../ui/Controls';
import { getUserLocation, setLightingMode, type LightMode } from '../scene/EnvironmentLighting';
import type { AppState, TurbinePart } from '../types';

type SceneMode = 'inspect' | 'learn' | 'print';

export function initPlaygroundScene(container: HTMLDivElement): () => void {
  const state: AppState = {
    rotorType: 'savonius-helix',
    stages: 3,
    generators: 1,
    radius: 66,
    windSpeed: 6.0,
    targetRPM: 0,
    currentRPM: 0,
    exploded: false,
    parts: [],
  };

  const { scene, camera, renderer, controls, lightRig, resize: resizeScene } =
    createSceneManager(container);
  const { composer, outlinePass, resize: resizeFx } = createPostProcessing(renderer, scene, camera);
  const wind = createWindSystem(scene, 1200);
  const mats = createMaterials();

  const towerGroup = new THREE.Group();
  scene.add(towerGroup);

  let rotorMeshGroup: THREE.Group | null = null;
  let currentSceneMode: SceneMode = 'inspect';
  let lightMode: LightMode = 'current-light';
  let userLocation: { lat: number; lon: number } | null = null;
  let lastLightUpdateMs = 0;
  let mobileViewport = window.matchMedia('(max-width: 980px)').matches;
  let animId = 0;
  let mobileHintTimer: ReturnType<typeof setTimeout> | null = null;
  let partCardHideTimer: ReturnType<typeof setTimeout> | null = null;
  let cleanedUp = false;

  const MOBILE_HINT_KEY = 'helix-mobile-scene-hint-dismissed-v1';
  const PART_CARD_W = 260;
  const PART_CARD_H = 80;

  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredPart: TurbinePart | null = null;

  const partCard = document.getElementById('part-card') as HTMLDivElement | null;
  const desiredCamera = new THREE.Vector3(60, 40, 80);
  const desiredTarget = new THREE.Vector3(0, 30, 0);
  const mobileSceneHintEl = document.getElementById('mobile-scene-hint') as HTMLDivElement | null;
  const mobileSceneHintDismissEl = document.getElementById(
    'mobile-scene-hint-dismiss',
  ) as HTMLButtonElement | null;

  function setControlPanelCollapsed(collapsed: boolean): void {
    const panel = document.querySelector<HTMLElement>('.control-panel');
    const chevron = document.getElementById('panel-chevron');
    if (!panel) return;
    panel.classList.toggle('collapsed', collapsed);
    if (chevron) chevron.textContent = collapsed ? '▼' : '▲';
  }

  function hideMobileSceneHint(persist = false): void {
    if (!mobileSceneHintEl) return;
    if (mobileHintTimer !== null) {
      clearTimeout(mobileHintTimer);
      mobileHintTimer = null;
    }
    mobileSceneHintEl.classList.remove('visible');
    if (persist) localStorage.setItem(MOBILE_HINT_KEY, '1');
  }

  function maybeShowMobileSceneHint(): void {
    if (!mobileSceneHintEl || !mobileViewport) {
      hideMobileSceneHint(false);
      return;
    }
    if (localStorage.getItem(MOBILE_HINT_KEY) === '1') return;
    if (mobileHintTimer !== null) clearTimeout(mobileHintTimer);
    mobileHintTimer = setTimeout(() => {
      if (mobileViewport) mobileSceneHintEl.classList.add('visible');
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
    if (!rpmInfo) return;
    state.targetRPM = state.exploded ? 0 : rpmInfo.rpm;
    const power = computePower({
      windSpeed: state.windSpeed,
      stages: state.stages,
      radiusMm: state.radius,
      cp: rpmInfo.cp,
      generators: state.generators,
    });
    mats.copper.emissiveIntensity = Math.min(2.0, power.pOut / 20.0);
    updateEnergyUI({
      pOut: power.pOut,
      annualKwh: power.annualKwh,
      phonesPerDay: power.phonesPerDay,
      cp: rpmInfo.cp,
      rpm: state.currentRPM,
    });
  }

  function applySceneMode(mode: SceneMode): void {
    currentSceneMode = mode;
    document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.sceneMode === mode);
    });
    if (mode === 'inspect') {
      state.exploded = false;
      controls.autoRotate = false;
      desiredCamera.set(mobileViewport ? 45 : 60, mobileViewport ? 30 : 40, mobileViewport ? 60 : 80);
    }
    if (mode === 'learn') {
      state.exploded = true;
      controls.autoRotate = false;
      desiredCamera.set(mobileViewport ? 48 : 52, mobileViewport ? 32 : 36, mobileViewport ? 62 : 65);
    }
    if (mode === 'print') {
      state.exploded = false;
      controls.autoRotate = false;
      desiredCamera.set(mobileViewport ? 36 : 42, mobileViewport ? 22 : 26, mobileViewport ? 43 : 48);
    }
    refreshPhysicsUI();
  }

  function updateLighting(force = false): void {
    const nowMs = performance.now();
    if (!force && nowMs - lastLightUpdateMs < 1000) return;
    lastLightUpdateMs = nowMs;
    const snapshot = setLightingMode(scene, lightRig, lightMode, new Date(), userLocation);
    const modeBias = lightMode === 'studio' ? 0.1 : lightMode === 'night' ? 0.12 : 0;
    renderer.toneMappingExposure = Math.min(1.18, 0.86 + snapshot.brightness * 0.32 + modeBias);
    document.body.dataset.sunPhase = snapshot.phase;
    const statusEl = document.getElementById('sun-status');
    if (statusEl) {
      const region = userLocation ? `lat ${userLocation.lat.toFixed(1)}` : 'timezone fallback';
      statusEl.textContent = `${snapshot.phase.toUpperCase()} | ${(snapshot.brightness * 100).toFixed(0)}% | ${region}`;
    }
  }

  wireControls(state, {
    onGeometryChanged: () => {
      rebuildTower();
      refreshPhysicsUI();
    },
    onPhysicsChanged: refreshPhysicsUI,
    onExplodeToggle: () => {
      currentSceneMode = state.exploded ? 'learn' : 'inspect';
      if (!state.exploded) refreshPhysicsUI();
      document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.sceneMode === currentSceneMode);
      });
    },
  });

  const lightModeSelect = document.getElementById('select-light-mode') as HTMLSelectElement | null;
  if (lightModeSelect) {
    lightModeSelect.addEventListener('change', () => {
      lightMode = lightModeSelect.value as LightMode;
      updateLighting(true);
    });
  }

  document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      applySceneMode((btn.dataset.sceneMode ?? 'inspect') as SceneMode);
      hideMobileSceneHint(true);
    });
  });

  if (mobileSceneHintDismissEl) {
    mobileSceneHintDismissEl.addEventListener('click', () => hideMobileSceneHint(true));
  }

  const panelHeaderToggle = document.getElementById('panel-header-toggle');
  const controlPanelEl = document.querySelector<HTMLElement>('.control-panel');
  if (panelHeaderToggle && controlPanelEl) {
    panelHeaderToggle.addEventListener('click', () => {
      setControlPanelCollapsed(!controlPanelEl.classList.contains('collapsed'));
    });
  }

  function onMouseMove(event: MouseEvent): void {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    if (partCard) {
      partCard.style.left = `${Math.min(event.clientX + 20, window.innerWidth - PART_CARD_W)}px`;
      partCard.style.top = `${Math.min(event.clientY + 20, window.innerHeight - PART_CARD_H)}px`;
    }
  }

  function onTouchEnd(event: TouchEvent): void {
    if (event.changedTouches.length === 0 || !partCard) return;
    const touch = event.changedTouches[0];
    mouse.x = (touch.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(touch.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(state.parts, false);
    if (hits.length > 0) {
      const hit = hits[0].object as TurbinePart;
      hoveredPart = hit;
      outlinePass.selectedObjects = [hoveredPart];
      const titleEl = document.getElementById('pc-title');
      const descEl = document.getElementById('pc-desc');
      if (titleEl) titleEl.innerText = hoveredPart.userData.name;
      if (descEl) descEl.innerText = hoveredPart.userData.desc;
      partCard.style.left = `${Math.min(touch.clientX + 20, window.innerWidth - PART_CARD_W)}px`;
      partCard.style.top = `${Math.min(touch.clientY + 20, window.innerHeight - PART_CARD_H)}px`;
      partCard.style.opacity = '1';
      if (partCardHideTimer !== null) clearTimeout(partCardHideTimer);
      partCardHideTimer = setTimeout(() => {
        if (partCard) partCard.style.opacity = '0';
        hoveredPart = null;
        outlinePass.selectedObjects = [];
      }, 3000);
    }
  }

  function onResize(): void {
    mobileViewport = window.matchMedia('(max-width: 980px)').matches;
    resizeScene();
    resizeFx();
    if (mobileViewport) {
      applySceneMode(currentSceneMode);
      setControlPanelCollapsed(true);
      maybeShowMobileSceneHint();
    } else {
      hideMobileSceneHint(false);
    }
  }

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('touchend', onTouchEnd);
  window.addEventListener('resize', onResize);

  const clock = new THREE.Clock();

  function animate(): void {
    if (cleanedUp) return;
    animId = requestAnimationFrame(animate);
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

    raycaster.setFromCamera(mouse, camera);
    const hits = raycaster.intersectObjects(state.parts, false);
    const titleEl = document.getElementById('pc-title');
    const descEl = document.getElementById('pc-desc');
    if (hits.length > 0) {
      const next = hits[0].object as TurbinePart;
      if (hoveredPart !== next) {
        hoveredPart = next;
        outlinePass.selectedObjects = [hoveredPart];
        if (titleEl) titleEl.innerText = hoveredPart.userData.name;
        if (descEl) descEl.innerText = hoveredPart.userData.desc;
        if (partCard) partCard.style.opacity = '1';
      }
    } else if (hoveredPart) {
      hoveredPart = null;
      outlinePass.selectedObjects = [];
      if (partCard) partCard.style.opacity = '0';
    }

    updateLighting();
    wind.update(delta, state.windSpeed);
    controls.update();
    refreshPhysicsUI();
    composer.render();
  }

  setTimeout(() => {
    if (cleanedUp) return;
    const loader = document.getElementById('loader') as HTMLDivElement | null;
    if (loader) {
      loader.style.opacity = '0';
      setTimeout(() => {
        if (!cleanedUp && loader) loader.style.display = 'none';
      }, 500);
    }
    rebuildTower();
    refreshPhysicsUI();
    if (mobileViewport) {
      setControlPanelCollapsed(true);
      maybeShowMobileSceneHint();
    }
    controls.autoRotate = true;
    applySceneMode('inspect');
    updateLighting(true);
    getUserLocation().then((loc) => {
      if (loc && !cleanedUp) {
        userLocation = loc;
        updateLighting(true);
      }
    });
    animate();
  }, 900);

  return () => {
    cleanedUp = true;
    cancelAnimationFrame(animId);
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('touchend', onTouchEnd);
    window.removeEventListener('resize', onResize);
    renderer.dispose();
    if (container.contains(renderer.domElement)) {
      container.removeChild(renderer.domElement);
    }
  };
}
