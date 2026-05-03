export function computePower({
  windSpeed,
  stages,
  radiusMm,
  cp,
  generators
}: {
  windSpeed: number;
  stages: number;
  radiusMm: number;
  cp: number;
  generators: number;
}) {
  const rho = 1.225;
  const radiusM = radiusMm / 1000;
  const sweptArea = stages * 0.240 * (2 * radiusM);
  const eff = Math.min(0.9, 0.65 + generators * 0.07);

  const pWind = 0.5 * rho * sweptArea * Math.pow(windSpeed, 3);
  const pOut = pWind * cp * eff;
  const annualKwh = (pOut * 8760 * 0.25) / 1000;
  const phonesPerDay = (pOut * 24) / 15;

  return {
    pOut,
    annualKwh,
    phonesPerDay,
    efficiency: eff
  };
}
