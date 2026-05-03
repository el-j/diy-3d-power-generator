import * as THREE from 'three';
import { createSceneManager } from '../scene/SceneManager';
import { createPostProcessing } from '../scene/PostProcessing';
import { createMaterials } from '../assembly/HelixTower';
import { createWindSystem } from '../simulation/WindSystem';
import { wireControls } from '../ui/Controls';
import { getUserLocation, setLightingMode, type LightMode } from '../scene/EnvironmentLighting';
import type { AppState, PartUserData, TurbinePart } from '../types';

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

  const { scene, camera, renderer, controls, lightRig, resize: resizeScene } = createSceneManager(container);
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
  let isLerpingCamera = true; // Added for free view fix

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
  const mobileSceneHintDismissEl = document.getElementById('mobile-scene-hint-dismiss') as HTMLButtonElement | null;

  // FIX: Disable forced lerping on user drag to allow free camera view
  controls.addEventListener('start', () => {
    isLerpingCamera = false;
    controls.autoRotate = false;
  });

  const ROTOR_TYPES: Record<string, any> = {
    'savonius-helix': { cp: 0.18, tsr: 1.2 },
    'savonius-straight': { cp: 0.14, tsr: 1.0 },
    'lenz2': { cp: 0.22, tsr: 1.5 },
    'darrieus-h': { cp: 0.28, tsr: 3.5 },
    'gorlov': { cp: 0.32, tsr: 2.2 }
  };

  function twistGeometry(geometry: THREE.BufferGeometry, totalAngle: number) {
    const pos = geometry.attributes.position;
    const vec = new THREE.Vector3();
    geometry.computeBoundingBox();
    const minY = geometry.boundingBox!.min.y;
    const height = geometry.boundingBox!.max.y - minY;
    for (let i = 0; i < pos.count; i++) {
      vec.fromBufferAttribute(pos, i);
      const ratio = (vec.y - minY) / height;
      const angle = ratio * totalAngle;
      const x = vec.x * Math.cos(angle) - vec.z * Math.sin(angle);
      const z = vec.x * Math.sin(angle) + vec.z * Math.cos(angle);
      pos.setXYZ(i, x, vec.y, z);
    }
    geometry.computeVertexNormals();
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
    while (towerGroup.children.length > 0) {
      towerGroup.remove(towerGroup.children[0]);
    }
    state.parts = [];
    rotorMeshGroup = new THREE.Group();
    
    let currentY = 0;
    const bladeRadius = state.radius / 10.0;
    const STAGE_HEIGHT = 24.0;
    const HUB_RADIUS = 1.2;

    // 1. Base Station
    const baseHeight = 15;
    const baseMesh = new THREE.Mesh(new THREE.CylinderGeometry(8, 10, baseHeight, 32), mats.base);
    baseMesh.position.y = baseHeight / 2;
    baseMesh.castShadow = true; baseMesh.receiveShadow = true;
    baseMesh.userData = { name: "Base Station Housing", desc: "Houses power electronics.", assembledY: baseMesh.position.y, explodedY: -10 }
    state.parts.push(baseMesh);
    towerGroup.add(baseMesh);
    currentY += baseHeight;

    // 2. Generators Array
    const genHeight = 6;
    for (let g = 0; g < state.generators; g++) {
      const genCenterY = currentY + genHeight/2;
      const stator = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 2, 32), mats.stator);
      stator.position.y = genCenterY - 2;
      stator.userData = { name: `Stator (Gen ${g+1})`, desc: "Holds 9 copper wire coils.", assembledY: stator.position.y, explodedY: stator.position.y - 15 - (g*5) };
      towerGroup.add(stator); state.parts.push(stator);

      const coils = new THREE.Mesh(new THREE.TorusGeometry(6, 1.5, 16, 32), mats.copper);
      coils.rotation.x = Math.PI / 2; coils.position.y = genCenterY - 2;
      coils.userData = { name: `Copper Coils (Gen ${g+1})`, desc: "3-phase configuration.", assembledY: coils.position.y, explodedY: coils.position.y - 15 - (g*5) };
      towerGroup.add(coils); state.parts.push(coils);

      const rotorDisk = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 2, 32), mats.carbon);
      rotorDisk.position.y = genCenterY + 2;
      rotorDisk.userData = { name: `Rotor Disk (Gen ${g+1})`, desc: "Holds magnets.", assembledY: rotorDisk.position.y, explodedY: rotorDisk.position.y - 5 + (g*5) };
      
      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, genHeight, 16), mats.carbon);
      shaft.position.y = genCenterY;
      rotorMeshGroup.add(rotorDisk); rotorMeshGroup.add(shaft);
      state.parts.push(rotorDisk);
      currentY += genHeight;
    }

    // 3. Rotor Stages Setup
    const stageGroup = new THREE.Group();
    stageGroup.position.y = currentY;

    let bladeGeo: THREE.BufferGeometry | null = null;
    if (state.rotorType === 'savonius-helix' || state.rotorType === 'savonius-straight') {
      bladeGeo = new THREE.CylinderGeometry(bladeRadius, bladeRadius, STAGE_HEIGHT, 16, 16, true, 0, Math.PI * 0.85);
      if (state.rotorType === 'savonius-helix') twistGeometry(bladeGeo, Math.PI * 0.6);
    } else if (state.rotorType === 'darrieus-h') {
      bladeGeo = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, STAGE_HEIGHT, 16);
      bladeGeo.scale(0.2, 1, 1); 
    } else if (state.rotorType === 'gorlov') {
      bladeGeo = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, STAGE_HEIGHT, 16, 16);
      bladeGeo.scale(0.2, 1, 1);
      bladeGeo.translate(bladeRadius, 0, 0); 
      twistGeometry(bladeGeo, Math.PI * 0.6); 
    } else if (state.rotorType === 'lenz2') {
      bladeGeo = new THREE.CylinderGeometry(bladeRadius * 0.35, bladeRadius * 0.35, STAGE_HEIGHT, 16, 1, false, 0, Math.PI * 1.2);
    }

    const useDisks = ['savonius-helix', 'savonius-straight', 'gorlov', 'lenz2'].includes(state.rotorType);
    const useShaft = ['darrieus-h', 'gorlov', 'lenz2'].includes(state.rotorType);
    const useStruts = ['darrieus-h'].includes(state.rotorType);

    for (let s = 0; s < state.stages; s++) {
      const stageCenterY = s * STAGE_HEIGHT + (STAGE_HEIGHT / 2);
      
      if (useShaft) {
        const stageShaft = new THREE.Mesh(new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, STAGE_HEIGHT, 16), mats.carbon);
        stageShaft.position.y = stageCenterY;
        stageShaft.userData = { name: `Center Shaft (Stage ${s+1})`, desc: "Carbon Fiber Tube.", assembledY: stageCenterY, explodedY: stageCenterY + (s*15) };
        stageGroup.add(stageShaft); state.parts.push(stageShaft);
      }

      if (useDisks) {
        const connector = new THREE.Mesh(new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32), mats.carbon);
        connector.position.y = stageCenterY - STAGE_HEIGHT/2;
        connector.userData = { name: `Connector Ring (Stage ${s+1})`, desc: "PLA-CF interlocking ring.", assembledY: connector.position.y, explodedY: connector.position.y + (s*15) };
        stageGroup.add(connector); state.parts.push(connector);
      }

      for(let b = 0; b < 3; b++) {
        const angle = (b * (Math.PI * 2 / 3));
        const bx = Math.cos(angle) * bladeRadius;
        const bz = Math.sin(angle) * bladeRadius;
        const blade = new THREE.Mesh(bladeGeo!, mats.petgTeal);
        blade.castShadow = true; blade.receiveShadow = true;

        if (state.rotorType.startsWith('savonius')) {
            blade.position.y = stageCenterY;
            blade.rotation.y = angle + (state.rotorType === 'savonius-helix' ? s * Math.PI * 0.6 : 0);
            blade.userData = { name: `Savonius Blade`, desc: "Drag-based profile.", assembledY: stageCenterY, explodedY: stageCenterY + (s*15) + 5 };
        } 
        else if (state.rotorType === 'gorlov') {
            blade.position.set(0, stageCenterY, 0);
            blade.rotation.y = angle + (s * Math.PI * 0.6); 
            blade.userData = { name: `Gorlov Airfoil`, desc: "Lift-based helical profile.", assembledY: stageCenterY, explodedY: stageCenterY + (s*15) + 5 };
        } 
        else if (state.rotorType === 'lenz2') {
            blade.position.set(bx * 0.8, stageCenterY, bz * 0.8);
            blade.rotation.y = -angle + Math.PI * 0.75;
            blade.userData = { name: `Lenz2 Blade`, desc: "Hybrid lift/drag profile.", assembledY: stageCenterY, explodedY: stageCenterY + (s*15) + 5 };
        } 
        else if (state.rotorType === 'darrieus-h') {
            blade.position.set(bx, stageCenterY, bz);
            blade.rotation.y = -angle; 
            blade.userData = { name: `Darrieus Airfoil`, desc: "Lift-based airfoil.", assembledY: stageCenterY, explodedY: stageCenterY + (s*15) + 5 };
        }

        stageGroup.add(blade); state.parts.push(blade);

        if (useStruts) {
            const strutGeo = new THREE.CylinderGeometry(0.4, 0.4, bladeRadius, 8);
            strutGeo.rotateZ(Math.PI/2);
            const strut1 = new THREE.Mesh(strutGeo, mats.carbon);
            strut1.position.set(bx/2, stageCenterY + STAGE_HEIGHT/2 - 2, bz/2);
            strut1.rotation.y = -angle;
            strut1.userData = { name: `Strut`, desc: "PLA-CF", assembledY: strut1.position.y, explodedY: strut1.position.y + (s*15) + 5 };
            stageGroup.add(strut1); state.parts.push(strut1);

            const strut2 = new THREE.Mesh(strutGeo, mats.carbon);
            strut2.position.set(bx/2, stageCenterY - STAGE_HEIGHT/2 + 2, bz/2);
            strut2.rotation.y = -angle;
            strut2.userData = { name: `Strut`, desc: "PLA-CF", assembledY: strut2.position.y, explodedY: strut2.position.y + (s*15) + 5 };
            stageGroup.add(strut2); state.parts.push(strut2);
        }
      }
    }
    
    const topCap = new THREE.Mesh(new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32), mats.carbon);
    topCap.position.y = state.stages * STAGE_HEIGHT;
    topCap.userData = { name: "Top Cap", desc: "Seals tower, holds bearing.", assembledY: topCap.position.y, explodedY: topCap.position.y + (state.stages*15) + 10 };
    stageGroup.add(topCap); state.parts.push(topCap);

    if (rotorMeshGroup) {
      rotorMeshGroup.add(stageGroup);
      towerGroup.add(rotorMeshGroup);
    }

    desiredTarget.set(0, currentY + (state.stages * STAGE_HEIGHT)/2, 0);
  }

  function refreshPhysicsUI(): void {
    const typeData = ROTOR_TYPES[state.rotorType] || ROTOR_TYPES['savonius-helix'];
    const R = state.radius / 1000;
    const v = state.windSpeed;
    const omega = (typeData.tsr * v) / R;
    state.targetRPM = state.exploded || v === 0 ? 0 : (omega / (2 * Math.PI)) * 60;

    const sweptArea = state.stages * 0.240 * (2 * R);
    const eff = Math.min(0.9, 0.65 + (state.generators * 0.07));
    const pWind = 0.5 * 1.225 * sweptArea * Math.pow(v, 3);
    const pOut = pWind * typeData.cp * eff;
    const annualKwh = (pOut * 8760 * 0.25) / 1000;
    const phonesPerDay = (pOut * 24) / 15;

    mats.copper.emissiveIntensity = Math.min(2.0, pOut / 20.0);

    const wEl = document.getElementById('val-power-w');
    if (wEl) wEl.innerText = pOut.toFixed(1) + ' W';
    const cpEl = document.getElementById('val-cp');
    if (cpEl) cpEl.innerText = (typeData.cp * 100).toFixed(0) + '%';
    const rpmEl = document.getElementById('val-rpm');
    if (rpmEl) rpmEl.innerText = Math.round(state.currentRPM) + ' RPM';
    const kwhEl = document.getElementById('val-power-kwh');
    if (kwhEl) kwhEl.innerText = Math.round(annualKwh) + ' kWh/yr';
    const phonesEl = document.getElementById('val-phones');
    if (phonesEl) phonesEl.innerText = phonesPerDay.toFixed(1) + ' phones/day';
    const heightEl = document.getElementById('val-height');
    if (heightEl) heightEl.innerText = String(state.stages * 240);
    const radiusEl = document.getElementById('val-radius');
    if (radiusEl) radiusEl.innerText = state.radius + ' mm';
    const gensEl = document.getElementById('val-gens');
    if (gensEl) gensEl.innerText = state.generators.toString();
    const stagesEl = document.getElementById('val-stages');
    if (stagesEl) stagesEl.innerText = state.stages.toString();
  }

  function applySceneMode(mode: SceneMode): void {
    currentSceneMode = mode;
    isLerpingCamera = true;
    document.querySelectorAll<HTMLButtonElement>('.scene-mode-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.sceneMode === mode);
    });
    if (mode === 'inspect') {
      state.exploded = false;
      controls.autoRotate = true;
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
      desiredCamera.set(mobileViewport ? 36 : 40, mobileViewport ? 22 : 20, mobileViewport ? 43 : 45);
      desiredTarget.set(0, 15, 0); // Focus on generator
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

  // Bind new config inputs
  const rotorSelect = document.getElementById('select-rotor') as HTMLSelectElement | null;
  const gensSlider = document.getElementById('slider-gens') as HTMLInputElement | null;
  const radiusSlider = document.getElementById('slider-radius') as HTMLInputElement | null;
  const stagesSlider = document.getElementById('slider-stages') as HTMLInputElement | null;
  const windSlider = document.getElementById('slider-wind') as HTMLInputElement | null;
  const presetBtns = document.querySelectorAll('.preset-btn');

  if (rotorSelect) rotorSelect.addEventListener('change', (e) => { state.rotorType = (e.target as HTMLSelectElement).value; rebuildTower(); refreshPhysicsUI(); });
  if (gensSlider) gensSlider.addEventListener('input', (e) => { state.generators = parseInt((e.target as HTMLInputElement).value); rebuildTower(); refreshPhysicsUI(); });
  if (radiusSlider) radiusSlider.addEventListener('input', (e) => { state.radius = parseInt((e.target as HTMLInputElement).value); rebuildTower(); refreshPhysicsUI(); });
  if (stagesSlider) stagesSlider.addEventListener('input', (e) => { state.stages = parseInt((e.target as HTMLInputElement).value); rebuildTower(); refreshPhysicsUI(); });
  if (windSlider) {
    windSlider.addEventListener('input', (e) => { 
        state.windSpeed = parseFloat((e.target as HTMLInputElement).value); 
        presetBtns.forEach(b => b.classList.remove('active'));
        refreshPhysicsUI(); 
    });
  }

  presetBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      presetBtns.forEach(b => b.classList.remove('active'));
      const target = e.target as HTMLButtonElement;
      target.classList.add('active');
      state.windSpeed = parseFloat(target.dataset.wind || '6');
      if (windSlider) windSlider.value = state.windSpeed.toString();
      refreshPhysicsUI();
    });
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

    if (isLerpingCamera) {
        camera.position.lerp(desiredCamera, 0.04);
        controls.target.lerp(desiredTarget, 0.04);
        if (camera.position.distanceTo(desiredCamera) < 0.5) {
            isLerpingCamera = false;
        }
    }

    state.currentRPM += (state.targetRPM - state.currentRPM) * delta * 0.5;
    if (rotorMeshGroup && !state.exploded) {
      const visualRps = (state.currentRPM / 60) * 0.2;
      rotorMeshGroup.rotation.y -= visualRps * Math.PI * 2 * delta;
    }

    state.parts.forEach((part: TurbinePart) => {
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