import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';

export function createPostProcessing(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.6, 0.28, 1.0);
  bloomPass.threshold = 0.81;
  bloomPass.strength = 0.24;
  bloomPass.radius = 0.22;
  composer.addPass(bloomPass);

  const outlinePass = new OutlinePass(new THREE.Vector2(window.innerWidth, window.innerHeight), scene, camera);
  outlinePass.edgeStrength = 6.3;
  outlinePass.edgeGlow = 0.38;
  outlinePass.edgeThickness = 2.8;
  outlinePass.pulsePeriod = 0;
  outlinePass.visibleEdgeColor.set('#7ce8ff');
  outlinePass.hiddenEdgeColor.set('#082736');
  composer.addPass(outlinePass);

  function resize(): void {
    composer.setSize(window.innerWidth, window.innerHeight);
  }

  return { composer, outlinePass, resize };
}
