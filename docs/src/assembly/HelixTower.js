import * as THREE from 'three';

const STAGE_HEIGHT = 24.0;
const HUB_RADIUS = 1.2;

export function createMaterials() {
  return {
    petgTeal: new THREE.MeshPhysicalMaterial({
      color: 0x00e5ff,
      metalness: 0.1,
      roughness: 0.3,
      transmission: 0.6,
      thickness: 1.0,
      ior: 1.5,
      transparent: true,
      opacity: 0.9,
      side: THREE.DoubleSide
    }),
    carbon: new THREE.MeshStandardMaterial({ color: 0x222222, roughness: 0.7, metalness: 0.3 }),
    stator: new THREE.MeshStandardMaterial({ color: 0xe0e0e0, roughness: 0.6, metalness: 0.1 }),
    base: new THREE.MeshStandardMaterial({ color: 0x1a1c23, roughness: 0.8, metalness: 0.2 }),
    copper: new THREE.MeshStandardMaterial({
      color: 0xff6b35,
      roughness: 0.3,
      metalness: 0.8,
      emissive: 0xff6b35,
      emissiveIntensity: 0.0
    })
  };
}

function twistGeometry(geometry, totalAngle) {
  const pos = geometry.attributes.position;
  const vec = new THREE.Vector3();
  geometry.computeBoundingBox();
  const minY = geometry.boundingBox.min.y;
  const maxY = geometry.boundingBox.max.y;
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

export function buildTower(group, state, mats) {
  while (group.children.length > 0) {
    group.remove(group.children[0]);
  }

  const parts = [];
  const rotorMeshGroup = new THREE.Group();
  let currentY = 0;
  const bladeRadius = state.radius / 10.0;

  const baseHeight = 15;
  const baseMesh = new THREE.Mesh(new THREE.CylinderGeometry(8, 10, baseHeight, 32), mats.base);
  baseMesh.position.y = baseHeight / 2;
  baseMesh.castShadow = true;
  baseMesh.receiveShadow = true;
  baseMesh.userData = {
    name: 'Base Station Housing',
    desc: 'Material: Dark Grey PETG\nHouses the power electronics, rectifier, and grid-tie interface.',
    assembledY: baseMesh.position.y,
    explodedY: -10
  };
  parts.push(baseMesh);
  group.add(baseMesh);
  currentY += baseHeight;

  const genHeight = 6;
  for (let g = 0; g < state.generators; g += 1) {
    const genCenterY = currentY + genHeight / 2;

    const stator = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 2, 32), mats.stator);
    stator.position.y = genCenterY - 2;
    stator.userData = {
      name: `Stator (Gen ${g + 1})`,
      desc: 'Material: White PETG\nHolds 9 copper wire coils. Static.',
      assembledY: stator.position.y,
      explodedY: stator.position.y - 15 - g * 5
    };
    group.add(stator);
    parts.push(stator);

    const coils = new THREE.Mesh(new THREE.TorusGeometry(6, 1.5, 16, 32), mats.copper);
    coils.rotation.x = Math.PI / 2;
    coils.position.y = genCenterY - 2;
    coils.userData = {
      name: `Copper Coils (Gen ${g + 1})`,
      desc: 'Material: Enamelled Copper Wire\n3-phase configuration.',
      assembledY: coils.position.y,
      explodedY: coils.position.y - 15 - g * 5
    };
    group.add(coils);
    parts.push(coils);

    const rotorDisk = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 2, 32), mats.carbon);
    rotorDisk.position.y = genCenterY + 2;
    rotorDisk.userData = {
      name: `Rotor Disk (Gen ${g + 1})`,
      desc: 'Material: PLA-CF\nHolds 12 neodymium magnets.',
      assembledY: rotorDisk.position.y,
      explodedY: rotorDisk.position.y - 5 + g * 5
    };

    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, genHeight, 16), mats.carbon);
    shaft.position.y = genCenterY;

    rotorMeshGroup.add(rotorDisk);
    rotorMeshGroup.add(shaft);
    parts.push(rotorDisk);
    currentY += genHeight;
  }

  let bladeGeometry;
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
      const stageShaft = new THREE.Mesh(new THREE.CylinderGeometry(HUB_RADIUS, HUB_RADIUS, STAGE_HEIGHT, 16), mats.carbon);
      stageShaft.position.y = stageCenterY;
      stageShaft.userData = {
        name: `Center Shaft (Stage ${s + 1})`,
        desc: 'Material: Carbon Fiber Tube\nCentral axis supporting the structure.',
        assembledY: stageCenterY,
        explodedY: stageCenterY + s * 15
      };
      stageGroup.add(stageShaft);
      parts.push(stageShaft);
    }

    if (useDisks) {
      const connector = new THREE.Mesh(new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32), mats.carbon);
      connector.position.y = stageCenterY - STAGE_HEIGHT / 2;
      connector.userData = {
        name: `Connector Ring (Stage ${s + 1})`,
        desc: 'Material: PLA-CF\nInterlocking ring joining vertical stages and maintaining blade rigidity.',
        assembledY: connector.position.y,
        explodedY: connector.position.y + s * 15
      };
      stageGroup.add(connector);
      parts.push(connector);
    }

    for (let b = 0; b < 3; b += 1) {
      const angle = b * (Math.PI * 2 / 3);
      const bx = Math.cos(angle) * bladeRadius;
      const bz = Math.sin(angle) * bladeRadius;

      const blade = new THREE.Mesh(bladeGeometry, mats.petgTeal);
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

        const strutTop = new THREE.Mesh(strutGeo, mats.carbon);
        strutTop.position.set(bx / 2, stageCenterY + STAGE_HEIGHT / 2 - 2, bz / 2);
        strutTop.rotation.y = -angle;
        strutTop.userData = {
          name: 'Strut',
          desc: 'Material: PLA-CF',
          assembledY: strutTop.position.y,
          explodedY: strutTop.position.y + s * 15 + 5
        };
        stageGroup.add(strutTop);
        parts.push(strutTop);

        const strutBottom = new THREE.Mesh(strutGeo, mats.carbon);
        strutBottom.position.set(bx / 2, stageCenterY - STAGE_HEIGHT / 2 + 2, bz / 2);
        strutBottom.rotation.y = -angle;
        strutBottom.userData = {
          name: 'Strut',
          desc: 'Material: PLA-CF',
          assembledY: strutBottom.position.y,
          explodedY: strutBottom.position.y + s * 15 + 5
        };
        stageGroup.add(strutBottom);
        parts.push(strutBottom);
      }
    }
  }

  const topCapY = state.stages * STAGE_HEIGHT;
  const topCap = new THREE.Mesh(new THREE.CylinderGeometry(bladeRadius + 0.5, bladeRadius + 0.5, 1, 32), mats.carbon);
  topCap.position.y = topCapY;
  topCap.userData = {
    name: 'Top Cap & Bearing',
    desc: 'Material: PLA-CF\nSeals the tower and holds the upper bearing.',
    assembledY: topCap.position.y,
    explodedY: topCap.position.y + state.stages * 15 + 10
  };
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
