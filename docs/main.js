import * as THREE from 'three';
import { createSceneManager } from './src/scene/SceneManager.js';
import { createPostProcessing } from './src/scene/PostProcessing.js';
import { createMaterials, buildTower } from './src/assembly/HelixTower.js';
import { computeRPM } from './src/simulation/RotationPhysics.js';
import { computePower } from './src/simulation/PowerCalculator.js';
import { createWindSystem } from './src/simulation/WindSystem.js';
import { wireControls, updateEnergyUI } from './src/ui/Controls.js';

const state = {
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

const container = document.getElementById('canvas-container');
const { scene, camera, renderer, controls, resize: resizeScene } = createSceneManager(container);
const { composer, outlinePass, resize: resizeFx } = createPostProcessing(renderer, scene, camera);
const wind = createWindSystem(scene, 1000);
const mats = createMaterials();

const towerGroup = new THREE.Group();
scene.add(towerGroup);

let rotorMeshGroup = null;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const partCard = document.getElementById('part-card');
let hoveredPart = null;

function rebuildTower() {
  const result = buildTower(towerGroup, state, mats);
  state.parts = result.parts;
  rotorMeshGroup = result.rotorMeshGroup;
  controls.target.set(0, result.targetY, 0);
}

function refreshPhysicsUI() {
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

wireControls(state, {
  onGeometryChanged: () => {
    rebuildTower();
    refreshPhysicsUI();
  },
  onPhysicsChanged: () => {
    refreshPhysicsUI();
  },
  onExplodeToggle: () => {
    if (!state.exploded) {
      refreshPhysicsUI();
    } else {
      state.targetRPM = 0;
    }
  }
});

window.addEventListener('mousemove', (event) => {
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
function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();

  state.currentRPM += (state.targetRPM - state.currentRPM) * delta * 0.5;

  if (rotorMeshGroup && !state.exploded) {
    const visualRps = (state.currentRPM / 60) * 0.2;
    rotorMeshGroup.rotation.y -= visualRps * Math.PI * 2 * delta;
  }

  state.parts.forEach((part) => {
    if (part.userData) {
      const targetY = state.exploded ? part.userData.explodedY : part.userData.assembledY;
      part.position.y += (targetY - part.position.y) * delta * 5.0;
    }
  });

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(state.parts, false);

  if (intersects.length > 0) {
    const obj = intersects[0].object;
    if (hoveredPart !== obj) {
      hoveredPart = obj;
      outlinePass.selectedObjects = [hoveredPart];
      if (hoveredPart.userData && hoveredPart.userData.name) {
        document.getElementById('pc-title').innerText = hoveredPart.userData.name;
        document.getElementById('pc-desc').innerText = hoveredPart.userData.desc;
        partCard.style.opacity = '1';
      }
      controls.autoRotate = false;
    }
  } else if (hoveredPart) {
    hoveredPart = null;
    outlinePass.selectedObjects = [];
    partCard.style.opacity = '0';
    controls.autoRotate = true;
  }

  wind.update(delta, state.windSpeed);
  controls.update();
  refreshPhysicsUI();
  composer.render();
}

setTimeout(() => {
  const loader = document.getElementById('loader');
  loader.style.opacity = '0';
  setTimeout(() => {
    loader.style.display = 'none';
  }, 500);

  rebuildTower();
  refreshPhysicsUI();
  animate();
}, 1000);
