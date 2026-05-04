import * as THREE from 'three';

/**
 * Twists a BufferGeometry along the Y axis by the given total angle (radians).
 * Used for Savonius-Helix and Gorlov blade profiles.
 */
export function twistGeometry(geometry: THREE.BufferGeometry, totalAngle: number): void {
  const pos = geometry.attributes.position;
  const vec = new THREE.Vector3();
  geometry.computeBoundingBox();
  const minY = geometry.boundingBox!.min.y;
  const height = geometry.boundingBox!.max.y - minY;

  for (let i = 0; i < pos.count; i += 1) {
    vec.fromBufferAttribute(pos, i);
    const ratio = (vec.y - minY) / height;
    const angle = ratio * totalAngle;
    const x = vec.x * Math.cos(angle) - vec.z * Math.sin(angle);
    const z = vec.x * Math.sin(angle) + vec.z * Math.cos(angle);
    pos.setXYZ(i, x, vec.y, z);
  }
  geometry.computeVertexNormals();
}
