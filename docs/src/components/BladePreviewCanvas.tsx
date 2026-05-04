import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import type { RotorType } from '../types';
import { makeBladeGeometry } from '../utils/bladeGeometry';

const STAGE_HEIGHT = 24.0;
const BLADE_RADIUS = 6.6; // default 66 mm / 10

/**
 * Compact auto-rotating 3D preview of a single blade stage.
 * Renders one representative stage for the given rotorType.
 */
export function BladePreviewCanvas({ rotorType }: { rotorType: RotorType }): React.JSX.Element {
  const containerRef = useRef<HTMLDivElement>(null);
  const rebuildRef = useRef<((type: RotorType) => void) | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const w = container.clientWidth || 320;
    const h = 200;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(48, w / h, 0.1, 500);
    camera.position.set(22, 14, 28);
    camera.lookAt(0, 12, 0);

    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
    const sun = new THREE.DirectionalLight(0x9bd7ff, 1.3);
    sun.position.set(12, 20, 12);
    scene.add(sun);
    const rim = new THREE.DirectionalLight(0xff9950, 0.35);
    rim.position.set(-10, 4, -12);
    scene.add(rim);

    const bladeGroup = new THREE.Group();
    scene.add(bladeGroup);

    const bladeMat = new THREE.MeshPhysicalMaterial({
      color: 0x0ccde0,
      metalness: 0.08,
      roughness: 0.24,
      transmission: 0.34,
      thickness: 0.8,
      ior: 1.5,
      transparent: true,
      opacity: 0.94,
      clearcoat: 0.38,
      clearcoatRoughness: 0.3,
      side: THREE.DoubleSide,
    });
    const connectorMat = new THREE.MeshStandardMaterial({ color: 0x2a3138, roughness: 0.56, metalness: 0.24 });

    function buildBlades(type: RotorType): void {
      while (bladeGroup.children.length > 0) {
        bladeGroup.remove(bladeGroup.children[0]);
      }

      const bladeGeo = makeBladeGeometry(type, BLADE_RADIUS, STAGE_HEIGHT);
      const stageCenterY = STAGE_HEIGHT / 2;

      // Bottom connector ring
      const connGeo = new THREE.CylinderGeometry(BLADE_RADIUS + 0.5, BLADE_RADIUS + 0.5, 1, 32);
      bladeGroup.add(new THREE.Mesh(connGeo, connectorMat));

      // 3 blade instances (all types use a 3-blade arrangement in preview)
      for (let b = 0; b < 3; b += 1) {
        const angle = b * (Math.PI * 2 / 3);
        const bx = Math.cos(angle) * BLADE_RADIUS;
        const bz = Math.sin(angle) * BLADE_RADIUS;
        const blade = new THREE.Mesh(bladeGeo, bladeMat);
        blade.castShadow = true;

        if (type === 'savonius-helix' || type === 'savonius-straight') {
          blade.position.y = stageCenterY;
          blade.rotation.y = angle;
        } else if (type === 'gorlov') {
          // radius baked into geometry via translate()
          blade.position.set(0, stageCenterY, 0);
          blade.rotation.y = angle;
        } else if (type === 'lenz2') {
          blade.position.set(bx * 0.8, stageCenterY, bz * 0.8);
          blade.rotation.y = -angle + Math.PI * 0.75;
        } else {
          // darrieus-h
          blade.position.set(bx, stageCenterY, bz);
          blade.rotation.y = -angle;
        }

        bladeGroup.add(blade);
      }

      // Top connector ring
      const topConn = new THREE.Mesh(
        new THREE.CylinderGeometry(BLADE_RADIUS + 0.5, BLADE_RADIUS + 0.5, 1, 32),
        connectorMat,
      );
      topConn.position.y = STAGE_HEIGHT;
      bladeGroup.add(topConn);
    }

    rebuildRef.current = buildBlades;

    let animId = 0;
    const clock = new THREE.Clock();

    function animate(): void {
      animId = requestAnimationFrame(animate);
      bladeGroup.rotation.y -= clock.getDelta() * 0.55;
      renderer.render(scene, camera);
    }
    animate();

    function onResize(): void {
      const newW = container?.clientWidth || 320;
      renderer.setSize(newW, h);
      camera.aspect = newW / h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', onResize);
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Rebuild blades whenever rotorType changes (first render handled by [] effect via rebuildRef)
  useEffect(() => {
    rebuildRef.current?.(rotorType);
  }, [rotorType]);

  return (
    <div
      ref={containerRef}
      aria-label={`3D preview of ${rotorType} blade type`}
      style={{
        width: '100%',
        height: 200,
        borderRadius: 10,
        overflow: 'hidden',
        background: 'rgba(6,14,26,0.7)',
        border: '1px solid rgba(115,203,238,0.18)',
        marginBottom: '1rem',
      }}
    />
  );
}
