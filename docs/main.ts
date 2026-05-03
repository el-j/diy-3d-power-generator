import * as THREE from 'three';
import { createSceneManager } from './src/scene/SceneManager';
import { createPostProcessing } from './src/scene/PostProcessing';
import { createMaterials, buildTower } from './src/assembly/HelixTower';
import { computeRPM } from './src/simulation/RotationPhysics';
import { computePower } from './src/simulation/PowerCalculator';
import { createWindSystem } from './src/simulation/WindSystem';
import { wireControls, updateEnergyUI } from './src/ui/Controls';
import type { AppState, TurbinePart } from './src/types';

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
const { scene, camera, renderer, controls, resize: resizeScene } = createSceneManager(container);
const { composer, outlinePass, resize: resizeFx } = createPostProcessing(renderer, scene, camera);
const wind = createWindSystem(scene, 1000);
const mats = createMaterials();

const towerGroup = new THREE.Group();
scene.add(towerGroup);

let rotorMeshGroup: THREE.Group | null = null;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const partCard = document.getElementById('part-card') as HTMLDivElement;
let hoveredPart: TurbinePart | null = null;

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

window.addEventListener('mousemove', (event: MouseEvent) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  partCard.style.left = `${event.clientX + 20}px`;
  partCard.style.top = `${event.clientY + 20}px`;
});

window.addEventListener('resize', () => {
  resizeScene();
  resizeFx();
});

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

  wind.update(delta, state.windSpeed);
  controls.update();
  refreshPhysicsUI();
  composer.render();
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
  animate();
}, 1000);
