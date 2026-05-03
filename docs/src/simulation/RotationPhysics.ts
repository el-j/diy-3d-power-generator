import type { RotorType } from '../types';

const ROTOR_TYPES: Record<RotorType, { cp: number; tsr: number; name: string }> = {
  'savonius-helix': { cp: 0.18, tsr: 1.2, name: 'Helical Savonius' },
  'savonius-straight': { cp: 0.14, tsr: 1.0, name: 'Straight Savonius' },
  lenz2: { cp: 0.22, tsr: 1.5, name: 'Lenz2 Hybrid' },
  'darrieus-h': { cp: 0.28, tsr: 3.5, name: 'H-Rotor Darrieus' },
  gorlov: { cp: 0.32, tsr: 2.2, name: 'Gorlov Helical' }
};

export function computeRPM(rotorType: RotorType, windSpeed: number, radiusMm: number) {
  const rotor = ROTOR_TYPES[rotorType];
  if (windSpeed <= 0 || radiusMm <= 0) {
    return { rpm: 0, cp: rotor.cp };
  }
  const radiusM = radiusMm / 1000;
  const omega = (rotor.tsr * windSpeed) / radiusM;
  const rpm = (omega / (2 * Math.PI)) * 60;
  return { rpm, cp: rotor.cp };
}
