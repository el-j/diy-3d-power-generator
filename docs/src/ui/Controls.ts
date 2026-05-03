import type { AppState, EnergySnapshot, RotorType } from '../types';

interface Handlers {
  onGeometryChanged: () => void;
  onPhysicsChanged: () => void;
  onExplodeToggle: () => void;
}

export function wireControls(state: AppState, handlers: Handlers): void {
  const rotorSelect = document.getElementById('select-rotor') as HTMLSelectElement;
  const stagesSlider = document.getElementById('slider-stages') as HTMLInputElement;
  const gensSlider = document.getElementById('slider-gens') as HTMLInputElement;
  const radiusSlider = document.getElementById('slider-radius') as HTMLInputElement;
  const windSlider = document.getElementById('slider-wind') as HTMLInputElement;
  const presetBtns = document.querySelectorAll<HTMLButtonElement>('.preset-btn');
  const explodeBtn = document.getElementById('btn-explode') as HTMLButtonElement;

  rotorSelect.addEventListener('change', (e) => {
    state.rotorType = (e.target as HTMLSelectElement).value as RotorType;
    handlers.onGeometryChanged();
  });

  stagesSlider.addEventListener('input', (e) => {
    state.stages = Number.parseInt((e.target as HTMLInputElement).value, 10);
    (document.getElementById('val-stages') as HTMLElement).innerText = String(state.stages);
    (document.getElementById('val-height') as HTMLElement).innerText = String(state.stages * 240);
    handlers.onGeometryChanged();
  });

  gensSlider.addEventListener('input', (e) => {
    state.generators = Number.parseInt((e.target as HTMLInputElement).value, 10);
    (document.getElementById('val-gens') as HTMLElement).innerText = String(state.generators);
    handlers.onGeometryChanged();
  });

  radiusSlider.addEventListener('input', (e) => {
    state.radius = Number.parseInt((e.target as HTMLInputElement).value, 10);
    (document.getElementById('val-radius') as HTMLElement).innerText = `${state.radius} mm`;
    handlers.onGeometryChanged();
  });

  windSlider.addEventListener('input', (e) => {
    state.windSpeed = Number.parseFloat((e.target as HTMLInputElement).value);
    (document.getElementById('val-wind') as HTMLElement).innerText = `${state.windSpeed.toFixed(1)} m/s`;
    presetBtns.forEach((b) => b.classList.remove('active'));
    handlers.onPhysicsChanged();
  });

  presetBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      presetBtns.forEach((b) => b.classList.remove('active'));
      const current = e.target as HTMLButtonElement;
      current.classList.add('active');
      state.windSpeed = Number.parseFloat(current.dataset.wind ?? '6');
      windSlider.value = String(state.windSpeed);
      (document.getElementById('val-wind') as HTMLElement).innerText = `${state.windSpeed.toFixed(1)} m/s`;
      handlers.onPhysicsChanged();
    });
  });

  explodeBtn.addEventListener('click', () => {
    state.exploded = !state.exploded;
    explodeBtn.innerText = state.exploded ? 'Assemble Turbine' : 'Explore Parts (Exploded View)';
    explodeBtn.classList.toggle('active');
    handlers.onExplodeToggle();
  });
}

export function updateEnergyUI({ pOut, annualKwh, phonesPerDay, cp, rpm }: EnergySnapshot): void {
  (document.getElementById('val-power-w') as HTMLElement).innerText = `${pOut.toFixed(1)} W`;
  (document.getElementById('val-cp') as HTMLElement).innerText = `${(cp * 100).toFixed(0)}%`;
  (document.getElementById('val-rpm') as HTMLElement).innerText = `${Math.round(rpm)} RPM`;
  (document.getElementById('val-power-kwh') as HTMLElement).innerText = `${Math.round(annualKwh)} kWh/yr`;
  (document.getElementById('val-phones') as HTMLElement).innerText = `${phonesPerDay.toFixed(1)} phones/day`;
}
