export interface LinkItem {
  title: string;
  description: string;
  path: string;
  type?: 'markdown' | 'json' | 'repo';
}

export interface DownloadItem {
  label: string;
  path: string;
  category: 'tower' | 'generator' | 'base' | 'tools' | 'bundle';
}

export const repo = {
  owner: 'el-j',
  name: 'diy-3d-power-generator',
  branch: 'main'
};

export const docsLinks: LinkItem[] = [
  {
    title: 'Architecture Overview',
    description: 'System structure, module responsibilities, and assembly strategy.',
    path: 'docs/ARCHITECTURE.md',
    type: 'markdown'
  },
  {
    title: 'Physical Review',
    description: 'Mechanical validation notes, fit observations, and production constraints.',
    path: 'docs/PHYSICAL_REVIEW.md',
    type: 'markdown'
  },
  {
    title: 'Build Guide Index',
    description: 'Entry point for the step-by-step assembly documentation.',
    path: 'docs/build-guide/README.md',
    type: 'markdown'
  },
  {
    title: 'Master BOM (Markdown)',
    description: 'Human-readable full bill of materials.',
    path: 'docs/bom/master_bom.md',
    type: 'markdown'
  },
  {
    title: 'Master BOM (JSON)',
    description: 'Machine-readable BOM for scripts and integration.',
    path: 'docs/bom/master_bom.json',
    type: 'json'
  }
];

export const buildGuideLinks: LinkItem[] = [
  {
    title: '01 Tower',
    description: 'Helix tower stage assembly and variant setup.',
    path: 'docs/build-guide/01_tower.md',
    type: 'markdown'
  },
  {
    title: '02 Generator',
    description: 'XXL Aero-Fan generator print and assembly flow.',
    path: 'docs/build-guide/02_generator.md',
    type: 'markdown'
  },
  {
    title: '03 Base Station',
    description: 'XXL base station build sequence and mounting notes.',
    path: 'docs/build-guide/03_base_station.md',
    type: 'markdown'
  },
  {
    title: '04 Final Assembly',
    description: 'System integration from turbine stack to electronics.',
    path: 'docs/build-guide/04_final_assembly.md',
    type: 'markdown'
  },
  {
    title: '05 Tools',
    description: 'Winding tools, magnet buffer, and usage workflow.',
    path: 'docs/build-guide/05_tools.md',
    type: 'markdown'
  }
];

export const downloadItems: DownloadItem[] = [
  { label: 'Helix Tower Bundle (.3mf)', path: 'exports/middel-verbinder/HelixWindTower_allInOne.3mf', category: 'bundle' },
  { label: 'Tower Connector Bundle (.3mf)', path: 'exports/middel-verbinder/Savonius_Coreless_Tower-etagen-verbinder+vielzahn.3mf', category: 'bundle' },
  { label: 'Generator Bundle (.3mf)', path: 'exports/generator/helix-generator.3mf', category: 'bundle' },
  { label: 'XXL Base Bundle (.3mf)', path: 'exports/xl_basis/helix-basis.3mf', category: 'bundle' },

  { label: 'Helix Leaf STL', path: 'exports/middel-verbinder/Savonius_Coreless_Tower-Coreless_Helix_Fluegel.stl', category: 'tower' },
  { label: 'Middle Connector STL', path: 'exports/middel-verbinder/Savonius_Coreless_Tower-Mittel_Verbinder_Skelett_FLACH.stl', category: 'tower' },
  { label: 'Spline Plug STL', path: 'exports/middel-verbinder/Savonius_Coreless_Tower-Zwischen_Vielzahn_Plug.stl', category: 'tower' },
  { label: 'Start Disc STL', path: 'exports/flügel/Start_Scheibe_FLACH.stl', category: 'tower' },

  { label: 'Rotor Upper STL', path: 'exports/generator/09_Rotor_AeroFan_TANK_FINAL_Oben.stl', category: 'generator' },
  { label: 'Rotor Lower STL', path: 'exports/generator/05_Rotor_AeroFan_TANK_FINAL_Unten.stl', category: 'generator' },
  { label: 'Backplate Upper STL', path: 'exports/generator/10_Backplate_Ring_FLACH_Oben.stl', category: 'generator' },
  { label: 'Backplate Lower STL', path: 'exports/generator/04_Backplate_Ring_FLACH_Unten.stl', category: 'generator' },
  { label: 'Stator Slide XXL STL', path: 'exports/generator/07_Stator_Schlitten_XXL.stl', category: 'generator' },
  { label: 'Stator Donut Cover STL', path: 'exports/generator/08_Stator_Donut_Deckel_INSET.stl', category: 'generator' },
  { label: 'Clamp Rotor Stack STL', path: 'exports/generator/03_Clamp_Rotor_Stack_Mega_30mm.stl', category: 'generator' },
  { label: 'Clamp Bearing Lower STL', path: 'exports/generator/01_Clamp_Lager_Unten.stl', category: 'generator' },
  { label: 'Clamp Bearing Upper STL', path: 'exports/generator/13_Clamp_Lager_Oben.stl', category: 'generator' },
  { label: 'Bearing Reducer Lower STL', path: 'exports/generator/02_Lager_Reduzierung_Unten.stl', category: 'generator' },
  { label: 'Bearing Reducer Upper STL', path: 'exports/generator/14_Lager_Reduzierung_Oben.stl', category: 'generator' },
  { label: 'Stator Spacer 10mm STL', path: 'exports/generator/11_Stator_Abstands_Spacer_10mm.stl', category: 'generator' },
  { label: 'Magnet Spacer STL', path: 'exports/generator/15_Magnet_Spacer_Kloetzchen.stl', category: 'generator' },

  { label: 'Base Housing XXL STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Basis_Gehaeuse_XXL.stl', category: 'base' },
  { label: 'Stacking Deck Cover STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Stacking_Lager_Deckel_FLACH.stl', category: 'base' },
  { label: 'Wall Flange STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Wand_Flansch.stl', category: 'base' },
  { label: 'Maintenance Hatch STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Elektronik_Wartungs_Klappe.stl', category: 'base' },
  { label: 'Hatch Floor STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Wartungsklappen_Boden.stl', category: 'base' },
  { label: 'Bearing Test Shell STL', path: 'exports/xl_basis/Helix_Base_Station_XXL-Test_Lagerschale_Kompakt.stl', category: 'base' },

  { label: 'Tool Base Compact STL', path: 'exports/tool/prooftool/Wickelmaschine_Ortho_Basis2-Maschinen_Basis_Kompakt.stl', category: 'tools' },
  { label: 'Tool Tower STL', path: 'exports/tool/prooftool/Wickelmaschine_Ortho_Basis2-Turm.stl', category: 'tools' },
  { label: 'Tool Gear 60Z STL', path: 'exports/tool/prooftool/Wickelmaschine_Ortho_Basis2-Z6_Trommel_60Z.stl', category: 'tools' },
  { label: 'Tool Gear 40Z STL', path: 'exports/tool/prooftool/Wickelmaschine_Ortho_Basis2-Z4_Zwischen_In_40Z.stl', category: 'tools' },
  { label: 'Tool Gear 10Z STL', path: 'exports/tool/prooftool/Wickelmaschine_Ortho_Basis2-Z2_Spule_In_10Z.stl', category: 'tools' },
  { label: 'Magnet Buffer Base STL', path: 'exports/tool/prooftool/magenet_spanner/Wickelmaschine_Magnet_Spanner6-Teil1_Basis_Mit_Bremse.stl', category: 'tools' },
  { label: 'Magnet Buffer Slider STL', path: 'exports/tool/prooftool/magenet_spanner/Wickelmaschine_Magnet_Spanner6-Teil3_Magnet_Schlitten.stl', category: 'tools' },

  { label: 'Calibration Template STL', path: 'exports/Savonius_Calibration_Template-Sizing_Schablone_SKELETON.stl', category: 'bundle' }
];

export function toRepoBlobUrl(path: string): string {
  return `https://github.com/${repo.owner}/${repo.name}/blob/${repo.branch}/${encodePath(path)}`;
}

export function toRepoRawUrl(path: string): string {
  return `https://raw.githubusercontent.com/${repo.owner}/${repo.name}/${repo.branch}/${encodePath(path)}`;
}

function encodePath(path: string): string {
  return path
    .split('/')
    .map((part) => encodeURIComponent(part))
    .join('/');
}
