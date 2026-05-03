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
    title: 'Parametric + Printable',
    body: 'All geometry is generated from FreeCAD Python and centralized parameters, so dimensions stay consistent across parts.'
  },
  {
    title: 'Open Build Workflow',
    body: 'Assembly manifests, BOM, and step-by-step build docs are in-repo and versioned for transparent iterations.'
  },
  {
    title: 'Field-Ready System',
    body: 'Tower, generator, and base station are split for practical printing, transport, and maintenance.'
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
