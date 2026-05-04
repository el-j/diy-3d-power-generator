import * as THREE from 'three';
import type { RotorType } from '../types';
import { twistGeometry } from './math';

const HUB_RADIUS = 1.2;

/**
 * Creates a blade BufferGeometry for the given rotor type and radius.
 *
 * For Gorlov the radial offset is baked into the geometry via translate(),
 * so the mesh should be positioned at (0, y, 0) and rotated around Y.
 * For all other types the mesh should be positioned at the blade orbit radius.
 *
 * @param rotorType  One of the five supported rotor types.
 * @param bladeRadius  Orbit radius of the blade in Three.js units (mm / 10).
 * @param stageHeight  Height of one tower stage (default 24.0).
 */
export function makeBladeGeometry(
  rotorType: RotorType,
  bladeRadius: number,
  stageHeight = 24.0,
): THREE.BufferGeometry {
  if (rotorType === 'savonius-helix' || rotorType === 'savonius-straight') {
    const geo = new THREE.CylinderGeometry(bladeRadius, bladeRadius, stageHeight, 16, 16, true, 0, Math.PI * 0.85);
    if (rotorType === 'savonius-helix') twistGeometry(geo, Math.PI * 0.6);
    return geo;
  }
  if (rotorType === 'darrieus-h') {
    const geo = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, stageHeight, 16);
    geo.scale(0.2, 1, 1);
    return geo;
  }
  if (rotorType === 'gorlov') {
    const geo = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, stageHeight, 16, 16);
    geo.scale(0.2, 1, 1);
    geo.translate(bladeRadius, 0, 0);
    twistGeometry(geo, Math.PI * 0.6);
    return geo;
  }
  // lenz2
  return new THREE.CylinderGeometry(bladeRadius * 0.35, bladeRadius * 0.35, stageHeight, 16, 1, false, 0, Math.PI * 1.2);
}
