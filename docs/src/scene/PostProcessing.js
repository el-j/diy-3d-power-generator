import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';

export function createPostProcessing(renderer, scene, camera) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    1.0,
    0.4,
    0.85
  );
  bloomPass.threshold = 0.8;
  bloomPass.strength = 0.6;
  bloomPass.radius = 0.5;
  composer.addPass(bloomPass);

  const outlinePass = new OutlinePass(new THREE.Vector2(window.innerWidth, window.innerHeight), scene, camera);
  outlinePass.edgeStrength = 4.0;
  outlinePass.edgeGlow = 1.0;
  outlinePass.edgeThickness = 2.0;
  outlinePass.pulsePeriod = 0;
  outlinePass.visibleEdgeColor.set('#00e5ff');
  outlinePass.hiddenEdgeColor.set('#005566');
  composer.addPass(outlinePass);

  function resize() {
    composer.setSize(window.innerWidth, window.innerHeight);
  }

  return { composer, outlinePass, resize };
}
