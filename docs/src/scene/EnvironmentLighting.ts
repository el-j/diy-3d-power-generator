import * as THREE from 'three';

export type LightMode = 'current-light' | 'day' | 'night' | 'studio';

export interface LightRig {
  ambientLight: THREE.AmbientLight;
  hemiLight: THREE.HemisphereLight;
  sunLight: THREE.DirectionalLight;
  rimLight: THREE.DirectionalLight;
  ground: THREE.Mesh<THREE.CircleGeometry, THREE.MeshStandardMaterial>;
  sunGlow: THREE.Mesh<THREE.SphereGeometry, THREE.MeshBasicMaterial>;
}

export interface GeoPoint {
  lat: number;
  lon: number;
}

export interface LightSnapshot {
  phase: 'night' | 'dawn' | 'day' | 'dusk';
  brightness: number;
  sunHeight: number;
}

export function createEnvironmentLighting(scene: THREE.Scene): LightRig {
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.36);
  scene.add(ambientLight);

  const hemiLight = new THREE.HemisphereLight(0xc8e2ff, 0x232a31, 0.62);
  scene.add(hemiLight);

  const sunLight = new THREE.DirectionalLight(0xfff0cc, 2.2);
  sunLight.position.set(68, 96, 42);
  sunLight.castShadow = true;
  sunLight.shadow.camera.top = 140;
  sunLight.shadow.camera.bottom = -120;
  sunLight.shadow.camera.left = -120;
  sunLight.shadow.camera.right = 120;
  sunLight.shadow.mapSize.width = 2048;
  sunLight.shadow.mapSize.height = 2048;
  scene.add(sunLight);

  const rimLight = new THREE.DirectionalLight(0x83c5ff, 0.92);
  rimLight.position.set(-85, 35, -75);
  scene.add(rimLight);

  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(420, 96),
    new THREE.MeshStandardMaterial({
      color: 0x3f6a3e,
      roughness: 0.97,
      metalness: 0.03
    })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.2;
  ground.receiveShadow = true;
  scene.add(ground);

  const sunGlow = new THREE.Mesh(
    new THREE.SphereGeometry(4.6, 24, 24),
    new THREE.MeshBasicMaterial({
      color: 0xffd98f,
      transparent: true,
      opacity: 0.68
    })
  );
  sunGlow.position.set(74, 120, -40);
  scene.add(sunGlow);

  return { ambientLight, hemiLight, sunLight, rimLight, ground, sunGlow };
}

export function setLightingMode(
  scene: THREE.Scene,
  rig: LightRig,
  mode: LightMode,
  now: Date,
  userLocation: GeoPoint | null
): LightSnapshot {
  if (mode === 'day') {
    return applyPreset(scene, rig, 1.0, 0.95, 'day', 1.0);
  }

  if (mode === 'night') {
    return applyPreset(scene, rig, 0.12, 0.15, 'night', -0.5);
  }

  if (mode === 'studio') {
    return applyPreset(scene, rig, 0.74, 0.62, 'day', 0.4);
  }

  const sun = getSolarPosition(now, userLocation);
  const daylight = Math.max(0, Math.sin(sun.altitude));
  const twilight = smoothstep(-0.12, 0.1, Math.sin(sun.altitude));
  const brightness = clamp(daylight * 0.92 + twilight * 0.2 + 0.08, 0.08, 1.0);

  const phase = sun.altitude < -0.07 ? 'night' : sun.altitude < 0.08 ? (sun.hourAngle <= 0 ? 'dawn' : 'dusk') : 'day';
  applyPreset(scene, rig, brightness, brightness * 0.8, phase, sun.altitude);
  setSunDirection(rig, sun.altitude, sun.azimuth);

  return {
    phase,
    brightness,
    sunHeight: sun.altitude
  };
}

function applyPreset(
  scene: THREE.Scene,
  rig: LightRig,
  brightness: number,
  skyMix: number,
  phase: 'night' | 'dawn' | 'day' | 'dusk',
  sunHeight: number
): LightSnapshot {
  const skyTop = new THREE.Color().lerpColors(new THREE.Color(0x08111f), new THREE.Color(0x96d7ff), skyMix);
  const skyBottom = new THREE.Color().lerpColors(new THREE.Color(0x0b1727), new THREE.Color(0xe6f5ff), skyMix);
  const fogColor = new THREE.Color().lerpColors(new THREE.Color(0x0b1422), new THREE.Color(0xa2d2f0), skyMix * 0.88);

  scene.background = skyTop;
  if (scene.fog instanceof THREE.FogExp2) {
    scene.fog.color = fogColor;
    scene.fog.density = 0.0022 - brightness * 0.001;
  }

  rig.ambientLight.intensity = 0.16 + brightness * 0.5;
  rig.hemiLight.intensity = 0.2 + brightness * 0.76;
  rig.sunLight.intensity = 0.55 + brightness * 2.35;
  rig.rimLight.intensity = 0.26 + (1 - brightness) * 1.08;

  rig.hemiLight.color.set(phase === 'night' ? 0x8ab8ff : phase === 'dawn' ? 0xffd5a1 : 0xcce9ff);
  rig.hemiLight.groundColor.set(phase === 'night' ? 0x18212d : 0x3f4e3f);

  rig.sunLight.color.set(phase === 'night' ? 0x9eb7ff : phase === 'dawn' || phase === 'dusk' ? 0xffc47d : 0xfff2d2);
  rig.rimLight.color.set(phase === 'night' ? 0x70a8ff : 0x8dc9ff);

  rig.ground.material.color.set(phase === 'night' ? 0x18261f : phase === 'day' ? 0x3f6640 : 0x5b5f3f);

  rig.sunGlow.material.color.set(phase === 'night' ? 0x7aa1ff : 0xffcf87);
  rig.sunGlow.material.opacity = phase === 'night' ? 0.28 : 0.62;

  const bottomMix = 0.42 + skyMix * 0.42;
  rig.ground.material.emissive = new THREE.Color().lerpColors(skyBottom, new THREE.Color(0x111111), bottomMix);
  rig.ground.material.emissiveIntensity = 0.05 + brightness * 0.07;

  if (scene.fog instanceof THREE.FogExp2) {
    scene.fog.density = clamp(0.00195 - brightness * 0.00075, 0.0011, 0.00205);
  }

  return { phase, brightness, sunHeight };
}

function setSunDirection(rig: LightRig, altitude: number, azimuth: number): void {
  const distance = 165;
  const y = Math.sin(altitude) * distance;
  const horizontal = Math.cos(altitude) * distance;
  const x = Math.sin(azimuth) * horizontal;
  const z = Math.cos(azimuth) * horizontal;

  rig.sunLight.position.set(x, Math.max(15, y), z);
  rig.sunGlow.position.set(x * 0.95, Math.max(20, y * 1.07), z * 0.95);
}

export async function getUserLocation(): Promise<GeoPoint | null> {
  if (!('geolocation' in navigator)) {
    return null;
  }

  try {
    return await new Promise<GeoPoint | null>((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        () => resolve(null),
        {
          enableHighAccuracy: false,
          timeout: 4500,
          maximumAge: 60 * 60 * 1000
        }
      );
    });
  } catch {
    return null;
  }
}

function getSolarPosition(now: Date, userLocation: GeoPoint | null): { altitude: number; azimuth: number; hourAngle: number } {
  const minutes = now.getHours() * 60 + now.getMinutes() + now.getSeconds() / 60;
  const hour = minutes / 60;
  const dayOfYear = getDayOfYear(now);
  const lat = userLocation?.lat ?? 48.0;

  const declination = (23.44 * Math.PI) / 180 * Math.sin(((2 * Math.PI) / 365) * (dayOfYear - 81));
  const latitude = (lat * Math.PI) / 180;

  const hourAngle = ((hour - 12) * 15 * Math.PI) / 180;
  const altitude = Math.asin(
    Math.sin(latitude) * Math.sin(declination) +
      Math.cos(latitude) * Math.cos(declination) * Math.cos(hourAngle)
  );

  const azimuth = Math.atan2(
    -Math.sin(hourAngle),
    Math.tan(declination) * Math.cos(latitude) - Math.sin(latitude) * Math.cos(hourAngle)
  );

  return { altitude, azimuth, hourAngle };
}

function getDayOfYear(date: Date): number {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff = date.getTime() - start.getTime();
  return Math.floor(diff / 86400000);
}

function smoothstep(min: number, max: number, value: number): number {
  const x = clamp((value - min) / (max - min), 0, 1);
  return x * x * (3 - 2 * x);
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
