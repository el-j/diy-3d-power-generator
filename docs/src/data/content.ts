import type { BuildStep, DownloadItem, FeatureCard, NavItem } from '../types/content';

export const REPO_URL = 'https://github.com/el-j/diy-3d-power-generator';
export const RAW_BASE_URL = 'https://raw.githubusercontent.com/el-j/diy-3d-power-generator/main';
export const BLOB_BASE_URL = 'https://github.com/el-j/diy-3d-power-generator/blob/main';

export const navItems: NavItem[] = [
  { href: '#overview', label: 'Overview' },
  { href: '#why', label: 'Why This Build' },
  { href: '#bom', label: 'BOM' },
  { href: '#steps', label: 'Build Steps' },
  { href: '#downloads', label: 'Downloads' }
];

export const featureCards: FeatureCard[] = [
  {
    title: 'Aero-Fan Generator',
    body: '20-pole axial-flux generator with an 11-blade fan integrated directly into the magnetic rotor — cools the coils while generating power. 12 capsule coils, 3-phase AC output.'
  },
  {
    title: '5 Hot-Swap Blade Types',
    body: 'Helix, Savonius, Darrieus H, Gorlov, and Lenz2 — all sharing a unified 12-tooth vielzahn spline. Swap blade types without tools to match your wind conditions.'
  },
  {
    title: 'Ultra-Flat Base Station',
    body: 'XXL base station at only 68 mm height. U-form opening lets the stator slide in and out without disassembly. 3D-printed tapered bearing cup included.'
  },
  {
    title: 'Parametric + Printable',
    body: 'All geometry generated from FreeCAD Python with centralized parameters. Bambu P1S optimized — every part fits the 256×256 mm bed.'
  },
  {
    title: 'Interactive Build Guide',
    body: 'Step-by-step assembly with persistent checkboxes, wing-type comparison, and inline markdown documentation — track your build progress directly in the browser.'
  },
  {
    title: 'Open Hardware Workflow',
    body: 'Assembly manifests, BOM, and build docs are versioned in-repo. FreeCAD Python scripts regenerate any part from parameters.json.'
  }
];

export const buildSteps: BuildStep[] = [
  {
    id: '01',
    title: 'Print Structural Parts',
    detail: 'Print active tower, generator, and base components from exports using PETG or PLA-CF as specified in material docs.'
  },
  {
    id: '02',
    title: 'Assemble Tower Modules',
    detail: 'Build helix stages and connectors first to verify fit tolerance before installing generator stack and wiring.'
  },
  {
    id: '03',
    title: 'Build Generator Stack',
    detail: 'Install rotor/stator plates, magnets, coils, and fasteners in sequence from build guide to preserve air-gap alignment.'
  },
  {
    id: '04',
    title: 'Mount Base + Final Wiring',
    detail: 'Integrate base station internals, bearing support, and final cable routing. Verify mechanical free-spin before load tests.'
  }
];

export const downloads: DownloadItem[] = [
  { label: 'Generator Package (.3mf)', path: 'exports/generator/helix-generator.3mf', category: 'generator' },
  { label: 'Tower Package (.3mf)', path: 'exports/middel-verbinder/HelixWindTower_allInOne.3mf', category: 'tower' },
  { label: 'Base Package (.3mf)', path: 'exports/xl_basis/helix-basis.3mf', category: 'base' },
  { label: 'Tools Folder', path: 'exports/tool', category: 'tools' }
];
