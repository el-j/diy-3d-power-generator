export function wireControls(state, handlers) {
  const rotorSelect = document.getElementById('select-rotor');
  const stagesSlider = document.getElementById('slider-stages');
  const gensSlider = document.getElementById('slider-gens');
  const radiusSlider = document.getElementById('slider-radius');
  const windSlider = document.getElementById('slider-wind');
  const presetBtns = document.querySelectorAll('.preset-btn');
  const explodeBtn = document.getElementById('btn-explode');

  rotorSelect.addEventListener('change', (e) => {
    state.rotorType = e.target.value;
    handlers.onGeometryChanged();
  });

  stagesSlider.addEventListener('input', (e) => {
    state.stages = Number.parseInt(e.target.value, 10);
    document.getElementById('val-stages').innerText = String(state.stages);
    document.getElementById('val-height').innerText = String(state.stages * 240);
    handlers.onGeometryChanged();
  });

  gensSlider.addEventListener('input', (e) => {
    state.generators = Number.parseInt(e.target.value, 10);
    document.getElementById('val-gens').innerText = String(state.generators);
    handlers.onGeometryChanged();
  });

  radiusSlider.addEventListener('input', (e) => {
    state.radius = Number.parseInt(e.target.value, 10);
    document.getElementById('val-radius').innerText = `${state.radius} mm`;
    handlers.onGeometryChanged();
  });

  windSlider.addEventListener('input', (e) => {
    state.windSpeed = Number.parseFloat(e.target.value);
    document.getElementById('val-wind').innerText = `${state.windSpeed.toFixed(1)} m/s`;
    presetBtns.forEach((b) => b.classList.remove('active'));
    handlers.onPhysicsChanged();
  });

  presetBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      presetBtns.forEach((b) => b.classList.remove('active'));
      e.target.classList.add('active');
      state.windSpeed = Number.parseFloat(e.target.dataset.wind);
      windSlider.value = String(state.windSpeed);
      document.getElementById('val-wind').innerText = `${state.windSpeed.toFixed(1)} m/s`;
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

export function updateEnergyUI({ pOut, annualKwh, phonesPerDay, cp, rpm }) {
  document.getElementById('val-power-w').innerText = `${pOut.toFixed(1)} W`;
  document.getElementById('val-cp').innerText = `${(cp * 100).toFixed(0)}%`;
  document.getElementById('val-rpm').innerText = `${Math.round(rpm)} RPM`;
  document.getElementById('val-power-kwh').innerText = `${Math.round(annualKwh)} kWh/yr`;
  document.getElementById('val-phones').innerText = `${phonesPerDay.toFixed(1)} phones/day`;
}
