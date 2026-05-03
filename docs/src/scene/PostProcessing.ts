import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';

export function createPostProcessing(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 0.8, 0.35, 0.9);
  bloomPass.threshold = 0.72;
  bloomPass.strength = 0.42;
  bloomPass.radius = 0.34;
  composer.addPass(bloomPass);

  const outlinePass = new OutlinePass(new THREE.Vector2(window.innerWidth, window.innerHeight), scene, camera);
  outlinePass.edgeStrength = 5.2;
  outlinePass.edgeGlow = 0.65;
  outlinePass.edgeThickness = 2.4;
  outlinePass.pulsePeriod = 0;
  outlinePass.visibleEdgeColor.set('#7ce8ff');
  outlinePass.hiddenEdgeColor.set('#0d3f56');
  composer.addPass(outlinePass);

  function resize(): void {
    composer.setSize(window.innerWidth, window.innerHeight);
  }

  return { composer, outlinePass, resize };
}
