import type { RotorType } from '../types';

export interface BladeTypeSpec {
  key: RotorType;
  name: string;
  principle: string;
  blades: number;
  twist: string;
  tsrRange: string;
  tsrValue: number;
  cpDisplay: string;
  cpValue: number;
  selfStarting: boolean;
  bestFor: string;
  partId: string;
  color: string;
  sourceFile: string;
}

export const BLADE_TYPES: Record<RotorType, BladeTypeSpec> = {
  'savonius-helix': {
    key: 'savonius-helix',
    name: 'Helix (Coreless)',
    principle: 'Hybrid drag/lift',
    blades: 1,
    twist: '90°',
    tsrRange: '1.0–1.5',
    tsrValue: 1.2,
    cpDisplay: '~18%',
    cpValue: 0.18,
    selfStarting: true,
    bestFor: 'Variable/gusty wind, urban, low cut-in speed',
    partId: 'TWR-LEAF-01',
    color: '#6ce0ff',
    sourceFile: 'src/leaf/helix_leaf+connector.py',
  },
  'savonius-straight': {
    key: 'savonius-straight',
    name: 'Savonius Straight',
    principle: 'Pure drag',
    blades: 2,
    twist: '0°',
    tsrRange: '0.8–1.0',
    tsrValue: 1.0,
    cpDisplay: '~14%',
    cpValue: 0.14,
    selfStarting: true,
    bestFor: 'Very low wind, highest torque, pumping',
    partId: 'TWR-STR-01',
    color: '#ffd08b',
    sourceFile: 'src/leaf/savonius_straight_leaf.py',
  },
  'lenz2': {
    key: 'lenz2',
    name: 'Lenz2 Cup',
    principle: 'Drag + vortex lift',
    blades: 3,
    twist: '0°',
    tsrRange: '1.2–1.8',
    tsrValue: 1.5,
    cpDisplay: '~22%',
    cpValue: 0.22,
    selfStarting: true,
    bestFor: 'Urban turbulence, moderate efficiency',
    partId: 'TWR-LEN-01',
    color: '#a8ff78',
    sourceFile: 'src/leaf/lenz2_leaf.py',
  },
  'darrieus-h': {
    key: 'darrieus-h',
    name: 'Darrieus H-Rotor',
    principle: 'Pure lift',
    blades: 3,
    twist: '0°',
    tsrRange: '3.0–4.0',
    tsrValue: 3.5,
    cpDisplay: '~28%',
    cpValue: 0.28,
    selfStarting: false,
    bestFor: 'Consistent wind, efficiency priority',
    partId: 'TWR-DAR-01',
    color: '#ff8a3d',
    sourceFile: 'src/leaf/darrieus_h_leaf.py',
  },
  'gorlov': {
    key: 'gorlov',
    name: 'Gorlov Helical',
    principle: 'Lift-drag hybrid',
    blades: 3,
    twist: '120°',
    tsrRange: '2.0–3.0',
    tsrValue: 2.2,
    cpDisplay: '~32%',
    cpValue: 0.32,
    selfStarting: true,
    bestFor: 'Best efficiency + smooth power output',
    partId: 'TWR-GOR-01',
    color: '#c084fc',
    sourceFile: 'src/leaf/gorlov_leaf.py',
  },
};

export const BETZ_LIMIT = 59.3;

export const ROTOR_TYPE_KEYS = Object.keys(BLADE_TYPES) as RotorType[];
