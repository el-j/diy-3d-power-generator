import * as THREE from 'three';

interface ParticleData {
  x: number;
  y: number;
  z: number;
  speed: number;
  offset: number;
}

export function createWindSystem(scene: THREE.Scene, particleCount = 1000) {
  const geometry = new THREE.BoxGeometry(0.1, 0.1, 4);
  const material = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.3 });
  const instanced = new THREE.InstancedMesh(geometry, material, particleCount);
  scene.add(instanced);

  const dummy = new THREE.Object3D();
  const particles: ParticleData[] = [];

  for (let i = 0; i < particleCount; i += 1) {
    const x = (Math.random() - 0.5) * 150;
    const y = Math.random() * 150;
    const z = (Math.random() - 0.5) * 150;
    dummy.position.set(x, y, z);
    dummy.updateMatrix();
    instanced.setMatrixAt(i, dummy.matrix);
    particles.push({ x, y, z, speed: 1.0 + Math.random(), offset: Math.random() * Math.PI * 2 });
  }

  function update(_delta: number, windSpeed: number): void {
    const speedMultiplier = windSpeed * 1.5;
    for (let i = 0; i < particleCount; i += 1) {
      const p = particles[i];
      p.z -= p.speed * speedMultiplier;

      if (Math.abs(p.x) < 20 && p.y < 100) {
        p.x += Math.sin(p.z * 0.1 + p.offset) * 0.2;
      }

      if (p.z < -80) {
        p.z = 80;
        p.x = (Math.random() - 0.5) * 150;
        p.y = Math.random() * 150;
      }

      dummy.position.set(p.x, p.y, p.z);
      dummy.scale.set(1, 1, Math.max(1, windSpeed * 0.5));
      dummy.updateMatrix();
      instanced.setMatrixAt(i, dummy.matrix);
    }

    instanced.instanceMatrix.needsUpdate = true;
    const intensity = Math.min(1.0, windSpeed / 15.0);
    material.color.setHSL(0.55, 0.8, 0.5 + intensity * 0.5);
    material.opacity = 0.1 + intensity * 0.4;
  }

  return { update };
}
