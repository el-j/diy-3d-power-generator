import * as THREE from 'three';

export type RotorType = 'savonius-helix' | 'savonius-straight' | 'lenz2' | 'darrieus-h' | 'gorlov';

export interface PartUserData {
  name: string;
  desc: string;
  assembledY: number;
  explodedY: number;
}

export type TurbinePart = THREE.Mesh<THREE.BufferGeometry, THREE.Material> & {
  userData: PartUserData;
};

export interface AppState {
  rotorType: RotorType;
  stages: number;
  generators: number;
  radius: number;
  windSpeed: number;
  targetRPM: number;
  currentRPM: number;
  exploded: boolean;
  parts: TurbinePart[];
}

export interface EnergySnapshot {
  pOut: number;
  annualKwh: number;
  phonesPerDay: number;
  cp: number;
  rpm: number;
}
