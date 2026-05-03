import * as THREE from 'three';
import type { AppState, TurbinePart } from '../types';

const STAGE_HEIGHT = 24.0;
const HUB_RADIUS = 1.2;

export interface MaterialSet {
  petgTeal: THREE.MeshPhysicalMaterial;
  carbon: THREE.MeshStandardMaterial;
  stator: THREE.MeshStandardMaterial;
  base: THREE.MeshStandardMaterial;
  copper: THREE.MeshStandardMaterial;
}

export function createMaterials(): MaterialSet {
  return {
    petgTeal: new THREE.MeshPhysicalMaterial({
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
      side: THREE.DoubleSide
    }),
    carbon: new THREE.MeshStandardMaterial({ color: 0x2a3138, roughness: 0.56, metalness: 0.24 }),
    stator: new THREE.MeshStandardMaterial({ color: 0xf0f3f8, roughness: 0.52, metalness: 0.06 }),
    base: new THREE.MeshStandardMaterial({ color: 0x141a22, roughness: 0.86, metalness: 0.08 }),
    copper: new THREE.MeshStandardMaterial({
      color: 0xff6b35,
      roughness: 0.26,
      metalness: 0.8,
      emissive: 0xff6b35,
      emissiveIntensity: 0.0
    })
  };
}

function createPart(
  geometry: THREE.BufferGeometry,
  material: THREE.Material,
  name: string,
  desc: string,
  assembledY: number,
  explodedY: number
): TurbinePart {
  const mesh = new THREE.Mesh(geometry, material) as TurbinePart;
  mesh.userData = { name, desc, assembledY, explodedY };
  return mesh;
}

function twistGeometry(geometry: THREE.CylinderGeometry, totalAngle: number): void {
  const pos = geometry.attributes.position;
  const vec = new THREE.Vector3();
  geometry.computeBoundingBox();
  const minY = geometry.boundingBox!.min.y;
  const maxY = geometry.boundingBox!.max.y;
  const height = maxY - minY;

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

export function buildTower(group: THREE.Group, state: AppState, mats: MaterialSet) {
  while (group.children.length > 0) {
    group.remove(group.children[0]);
  }

  const parts: TurbinePart[] = [];
  const rotorMeshGroup = new THREE.Group();
  let currentY = 0;
  const bladeRadius = state.radius / 10.0;

  const baseHeight = 15;
  const baseMesh = createPart(
    new THREE.CylinderGeometry(8, 10, baseHeight, 32),
    mats.base,
    'Base Station Housing',
    'Material: Dark Grey PETG\nHouses the power electronics, rectifier, and grid-tie interface.',
    baseHeight / 2,
    -10
  );
  baseMesh.castShadow = true;
  baseMesh.receiveShadow = true;
  baseMesh.position.y = baseHeight / 2;
  parts.push(baseMesh);
  group.add(baseMesh);
  currentY += baseHeight;

  const genHeight = 6;
  for (let g = 0; g < state.generators; g += 1) {
    const genCenterY = currentY + genHeight / 2;

    const stator = createPart(
      new THREE.CylinderGeometry(9, 9, 2, 32),
      mats.stator,
      `Stator (Gen ${g + 1})`,
      'Material: White PETG\nHolds 9 copper wire coils. Static.',
      genCenterY - 2,
      genCenterY - 2 - 15 - g * 5
    );
    stator.position.y = genCenterY - 2;
    group.add(stator);
    parts.push(stator);

    const coils = createPart(
      new THREE.TorusGeometry(6, 1.5, 16, 32),
      mats.copper,
      `Copper Coils (Gen ${g + 1})`,
      'Material: Enamelled Copper Wire\n3-phase configuration.',
      genCenterY - 2,
      genCenterY - 2 - 15 - g * 5
    );
    coils.rotation.x = Math.PI / 2;
    coils.position.y = genCenterY - 2;
    group.add(coils);
    parts.push(coils);

    const rotorDisk = createPart(
      new THREE.CylinderGeometry(9, 9, 2, 32),
      mats.carbon,
      `Rotor Disk (Gen ${g + 1})`,
      'Material: PLA-CF\nHolds 12 neodymium magnets.',
      genCenterY + 2,
      genCenterY + 2 - 5 + g * 5
    );
    rotorDisk.position.y = genCenterY + 2;
    rotorMeshGroup.add(rotorDisk);
    parts.push(rotorDisk);

    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, genHeight, 16), mats.carbon);
    shaft.position.y = genCenterY;
    rotorMeshGroup.add(shaft);

    currentY += genHeight;
  }

  let bladeGeometry: THREE.CylinderGeometry;
  if (state.rotorType === 'savonius-helix' || state.rotorType === 'savonius-straight') {
    bladeGeometry = new THREE.CylinderGeometry(bladeRadius, bladeRadius, STAGE_HEIGHT, 16, 16, true, 0, Math.PI * 0.85);
    if (state.rotorType === 'savonius-helix') {
      twistGeometry(bladeGeometry, Math.PI * 0.6);
    }
  } else if (state.rotorType === 'darrieus-h') {
    bladeGeometry = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, STAGE_HEIGHT, 16);
    bladeGeometry.scale(0.2, 1, 1);
  } else if (state.rotorType === 'gorlov') {
    bladeGeometry = new THREE.CylinderGeometry(HUB_RADIUS * 2.5, HUB_RADIUS * 0.5, STAGE_HEIGHT, 16, 16);
    bladeGeometry.scale(0.2, 1, 1);
    bladeGeometry.translate(bladeRadius, 0, 0);
    twistGeometry(bladeGeometry, Math.PI * 0.6);
  } else {
    bladeGeometry = new THREE.CylinderGeometry(bladeRadius * 0.35, bladeRadius * 0.35, STAGE_HEIGHT, 16, 1, false, 0, Math.PI * 1.2);
  }

  const stageGroup = new THREE.Group();
  stageGroup.position.y = currentY;
  const useDisks = ['savonius-helix', 'savonius-straight', 'gorlov', 'lenz2'].includes(state.rotorType);
  const useShaft = ['darrieus-h', 'gorlov', 'lenz2'].includes(state.rotorType);
  const useStruts = state.rotorType === 'darrieus-h';

  for (let s = 0; s < state.stages; s += 1) {
    const stageCenterY = s * STAGE_HEIGHT + STAGE_HEIGHT / 2;

    if (useShaft) {
      const stageShaft = createPart(
        new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, STAGE_HEIGHT, 16),
        mats.carbon,
        `Center Shaft (Stage ${s + 1})`,
        'Material: Carbon Fiber Tube\nCentral axis supporting the structure.',
        stageCenterY,
        stageCenterY + s * 15
      );
      stageShaft.position.y = stageCenterY;
      stageGroup.add(stageShaft);
      parts.push(stageShaft);
    }

    if (useDisks) {
      const connectorY = stageCenterY - STAGE_HEIGHT / 2;
      const connector = createPart(
        new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32),
        mats.carbon,
        `Connector Ring (Stage ${s + 1})`,
        'Material: PLA-CF\nInterlocking ring joining vertical stages and maintaining blade rigidity.',
        connectorY,
        connectorY + s * 15
      );
      connector.position.y = connectorY;
      stageGroup.add(connector);
      parts.push(connector);
    }

    for (let b = 0; b < 3; b += 1) {
      const angle = b * (Math.PI * 2 / 3);
      const bx = Math.cos(angle) * bladeRadius;
      const bz = Math.sin(angle) * bladeRadius;

      const blade = createPart(
        bladeGeometry,
        mats.petgTeal,
        'Blade',
        'Rotor blade segment.',
        stageCenterY,
        stageCenterY + s * 15 + 5
      );
      blade.castShadow = true;
      blade.receiveShadow = true;

      if (state.rotorType.startsWith('savonius')) {
        blade.position.y = stageCenterY;
        blade.rotation.y = angle + (state.rotorType === 'savonius-helix' ? s * Math.PI * 0.6 : 0);
        blade.userData = {
          name: 'Savonius Blade',
          desc: 'Drag-based profile. High starting torque, limited top speed.',
          assembledY: stageCenterY,
          explodedY: stageCenterY + s * 15 + 5
        };
      } else if (state.rotorType === 'gorlov') {
        blade.position.set(0, stageCenterY, 0);
        blade.rotation.y = angle + s * Math.PI * 0.6;
        blade.userData = {
          name: 'Gorlov Helical Airfoil',
          desc: 'Lift-based helical profile. Smooth rotation and highest efficiency.',
          assembledY: stageCenterY,
          explodedY: stageCenterY + s * 15 + 5
        };
      } else if (state.rotorType === 'lenz2') {
        blade.position.set(bx * 0.8, stageCenterY, bz * 0.8);
        blade.rotation.y = -angle + Math.PI * 0.75;
        blade.userData = {
          name: 'Lenz2 Blade',
          desc: 'Hybrid lift/drag profile. Great starting torque and good efficiency.',
          assembledY: stageCenterY,
          explodedY: stageCenterY + s * 15 + 5
        };
      } else {
        blade.position.set(bx, stageCenterY, bz);
        blade.rotation.y = -angle;
        blade.userData = {
          name: 'Darrieus Airfoil',
          desc: 'Lift-based airfoil. Generates forward lift, cutting through wind.',
          assembledY: stageCenterY,
          explodedY: stageCenterY + s * 15 + 5
        };
      }

      stageGroup.add(blade);
      parts.push(blade);

      if (useStruts) {
        const strutGeo = new THREE.CylinderGeometry(0.4, 0.4, bladeRadius, 8);
        strutGeo.rotateZ(Math.PI / 2);

        const strutTop = createPart(strutGeo, mats.carbon, 'Strut', 'Material: PLA-CF', stageCenterY + STAGE_HEIGHT / 2 - 2, stageCenterY + STAGE_HEIGHT / 2 - 2 + s * 15 + 5);
        strutTop.position.set(bx / 2, stageCenterY + STAGE_HEIGHT / 2 - 2, bz / 2);
        strutTop.rotation.y = -angle;
        stageGroup.add(strutTop);
        parts.push(strutTop);

        const strutBottom = createPart(strutGeo, mats.carbon, 'Strut', 'Material: PLA-CF', stageCenterY - STAGE_HEIGHT / 2 + 2, stageCenterY - STAGE_HEIGHT / 2 + 2 + s * 15 + 5);
        strutBottom.position.set(bx / 2, stageCenterY - STAGE_HEIGHT / 2 + 2, bz / 2);
        strutBottom.rotation.y = -angle;
        stageGroup.add(strutBottom);
        parts.push(strutBottom);
      }
    }
  }

  const topCapY = state.stages * STAGE_HEIGHT;
  const topCap = createPart(
    new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32),
    mats.carbon,
    'Top Cap & Bearing',
    'Material: PLA-CF\nSeals the tower and holds the upper bearing.',
    topCapY,
    topCapY + state.stages * 15 + 10
  );
  topCap.position.y = topCapY;
  stageGroup.add(topCap);
  parts.push(topCap);

  rotorMeshGroup.add(stageGroup);
  group.add(rotorMeshGroup);

  return {
    parts,
    rotorMeshGroup,
    targetY: currentY + (state.stages * STAGE_HEIGHT) / 2
  };
}
