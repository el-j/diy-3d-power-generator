# WindPower-3D — Agent Handbook

> Savonius Helix Wind-Generator: Parametric 3D-printed axial-flux generator + tower.
> All geometry is FreeCAD Python (Part workbench). Outputs: STL + 3MF for Bambu P1S.

---

## Project Structure

```
windpower-3d/
├── CLAUDE.md               ← YOU ARE HERE
├── freecad_loader.py       ← FreeCAD script runner (exec in FreeCAD console)
├── shared/
│   ├── parameters.json     ← SINGLE SOURCE OF TRUTH for all dimensions
│   ├── freecad_utils.py    ← Shared geometry helpers (import in every script)
│   ├── materials.json      ← Material specs (PETG, PLA)
│   └── fasteners.json      ← Screw/nut catalog
├── src/                    ← FreeCAD Python scripts (component generators)
│   ├── bigBasis/           ← ACTIVE: XXL generator + base station (≥v2.0)
│   │   ├── big_base_generator.py   ← XXL 20-pole generator (9 parts)
│   │   └── big_base_station.py     ← XXL base station (Ø220mm)
│   ├── smalBasis/          ← LEGACY: Small 10/20-pole generator
│   └── tools/              ← Manufacturing tools (winding machines)
│       ├── easy_tool_big_spools-accuschrauber.py
│       ├── firstSpooler/   ← Simple hand-crank spooler
│       ├── komplexSPooler/ ← Professional traversing winding machine
│       │   ├── Traversier-Basis & Skeleton.py
│       │   ├── achsen_zubehoer.py
│       │   ├── easy_tool_big_spools_4kant.py
│       │   ├── traeger_verschraubung.py
│       │   └── example.aufbau.py   ← VIRTUAL ASSEMBLY (visual reference)
│       └── magnetPuffer/
│           └── magnetBuffer.py     ← Magnetic wire tensioner
├── assemblies/             ← Assembly manifests (JSON)
│   ├── xl-generator/       ← ACTIVE generator assembly (v2.1)
│   ├── xl-base-station/    ← ACTIVE base station assembly
│   ├── tower/              ← Tower (helix blades)
│   ├── tools/              ← Tool assemblies (v2.1)
│   ├── generator/          ← LEGACY small generator
│   └── base-station/       ← LEGACY small base station
├── docs/
│   ├── ARCHITECTURE.md     ← System architecture overview
│   ├── bom/
│   │   ├── master_bom.json ← Machine-readable BOM (all assemblies)
│   │   └── master_bom.md   ← Human-readable BOM
│   └── build-guide/        ← Step-by-step assembly instructions (DE)
│       ├── 01_tower.md
│       ├── 02_generator.md ← XXL generator (v2.1)
│       ├── 03_base_station.md
│       ├── 04_final_assembly.md
│       └── 05_tools.md
├── exports/                ← Generated STL/3MF files
│   ├── generator/          ← XXL generator STLs (latest)
│   ├── xl_basis/           ← XXL base station STLs (latest)
│   ├── tool/               ← Tool STLs
│   ├── middel-verbinder/   ← Tower connector STLs
│   ├── basis/              ← Small base station STLs (legacy)
│   └── obsolete/           ← Old exports, keep for reference
└── .agents/
    ├── state.json          ← Orchestrator runtime state
    ├── identities/         ← Agent identity files
    └── workflows/          ← Pipeline definitions
```

---

## Active Assemblies (what to build)

| Assembly | Status | Source Script | Key Part IDs |
|----------|--------|---------------|--------------|
| XXL Generator | **ACTIVE v2.1** | `src/bigBasis/big_base_generator.py` | XLG-ROT-01/02, XLG-BP-01/02, XLG-STAT-01/02, XLG-PLUG-01, XLG-SPACER-01/02 |
| XXL Base Station | **ACTIVE v2.0** | `src/bigBasis/big_base_station.py` | XL-HOUS-01, XL-DECK-01, XL-FLNSH-01×3, XL-ADAPT-01, XL-DISC-01, XL-WANN-01, XL-KLAP-01 |
| Tower (Helix) | **ACTIVE** | `src/Helix_Leaf+Connector.py` | TWR-LEAF-01, TWR-CONN-01, TWR-PLUG-01 |
| Komplex-Spooler | **ACTIVE v2.1** | `src/tools/komplexSPooler/` | TOOL-KS-01..10 |
| Easy-Tool | **ACTIVE** | `src/tools/easy_tool_big_spools-accuschrauber.py` | TOOL-EASY-01/02 |
| Magnet-Puffer | **ACTIVE** | `src/tools/magnetPuffer/magnetBuffer.py` | TOOL-MB-01/02/03 |
| Small Generator | LEGACY | `src/smalBasis/` | GEN-* (do not extend) |
| Small Base Station | LEGACY | `src/smalBasis/Helix_Magnet_Basis_Station.py` | BASE-* (do not extend) |

---

## Key Dimensions (commit them to memory)

| Parameter | Value | Where |
|-----------|-------|-------|
| Vierkant-Achse | 10×10mm | `shared/parameters.json → global.achse_kantenlaenge` |
| XXL Rotor Radius | Ø180mm (R=90) | `xl_generator.rotor_radius` |
| Magnet-Kreis Radius | R=74mm | `xl_generator.mag_kreis_r` |
| Magnete pro Rotor | 20× (20×5×3mm N52) | `xl_generator.anzahl_magnete` |
| Capsule-Spulen | 12× (40×26mm outside, 22×8mm inside) | `xl_generator.spule_*` |
| Stator Radius | R=99mm | `xl_generator.stator_radius` |
| Stator-Deckel Mittelloch | R=16mm (Ø32mm) ← FIXED v2.1 | `big_base_generator.py:make_deckel()` |
| XXL Basis Radius | R=110mm (Ø220mm) | `xl_base_station.fuss_radius` |
| Kegelrollenlager | 29×50×15mm (REAL MEASURED) | `xl_base_station.lager_*` |
| Printer bed | 256×256×256mm | `print_constraints` |

---

## How FreeCAD Scripts Work

Every script in `src/` follows this pattern:

```python
import FreeCAD as App
import Part
import math

# Bootstrap shared utils (two options):
# Option A — exec loader in FreeCAD console first:
#   exec(open("/path/to/windpower-3d/freecad_loader.py").read()); run("bigBasis/big_base_generator")
# Option B — direct import:
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.freecad_utils import *

doc = App.newDocument("MyPart")

# ... geometry code using Part workbench primitives ...

show_obj(doc, shape, "Part_Name")   # uses shared helper
doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")
```

**Shared helpers available** (`shared/freecad_utils.py`):
- `make_square_prism(size, h)` — centered square prism (Vierkant-Achse holes)
- `make_hex_prism(radius, h)` — centered hex prism
- `make_capsule(length, width, h)` — oval/stadium shape (coil pockets)
- `make_centered_box(l, w, h, cx, cy, cz)` — box centered on a point
- `make_vielzahn_prism(r_out, r_in, teeth, h)` — spline coupling
- `create_circular_array(r, item_r, depth, count)` — bolt circle
- `create_rectangular_array(r, l, w, depth, count)` — magnet pockets
- `create_capsule_array(r, l, w, depth, count)` — capsule stator pockets
- `show_obj(doc, shape, name)` — add to FreeCAD document
- `load_parameters(section)` — read from `shared/parameters.json`

---

## Agent Workflow

### When a component changes in src/:

1. **Identify** which assembly JSON it belongs to (`assemblies/<name>/<name>_assembly.json`)
2. **Update assembly JSON**: new components, version bump, changelog entry
3. **Update master BOM** (`docs/bom/master_bom.json` + `master_bom.md`)
4. **Update build guide** (`docs/build-guide/0N_*.md`) — part IDs, steps, dimensions
5. **Update `shared/parameters.json`** if any key dimensions changed
6. **Update `.agents/state.json`** — set `last_run` to today's date

### When adding a new src/ script:

1. Add a `virtual_assembly` entry or update the existing assembly JSON
2. Run the full design-pipeline workflow (`.agents/workflows/design-pipeline.json`)
3. Export STL to `exports/<assembly-name>/`

### Part ID conventions:

| Prefix | Assembly | Status |
|--------|----------|--------|
| `XLG-` | XXL Generator | Active |
| `XL-` | XXL Base Station | Active |
| `TWR-` | Tower | Active |
| `TOOL-KS-` | Komplex-Spooler | Active |
| `TOOL-EASY-` | Easy-Tool | Active |
| `TOOL-MB-` | Magnet-Puffer | Active |
| `GEN-` | Small Generator | **Legacy** |
| `BASE-` | Small Base Station | **Legacy** |

---

## Critical Rules for Code Changes

1. **Never hardcode dimensions** — always reference `shared/parameters.json` via `load_parameters()`
2. **Square-axis holes**: always use `make_square_prism(achse_kantenlaenge + toleranz, h)` (10.5mm, not 10mm)
3. **Capsule shapes**: always use `make_capsule()` from freecad_utils — do not reimplement
4. **Export naming**: FreeCAD exports use the object name as filename prefix: `DocName-ObjName.stl`
5. **After any geometry fix**: bump the assembly JSON version (patch = 2.1.0 → 2.1.1)
6. **Stator-Deckel**: Mittelloch MUST be R=16mm (Ø32mm) — older R=9mm versions will not fit on axis

---

## Known Issues / Watch Out

- `exports/flügel/` accidentally contains a base station STL (misplaced during export) — not a tower blade
- `exports/xl_basis/generator/` contains older backplate versions (without `Abstands_Huelse_Lager.stl`) — use `exports/generator/` for latest
- The `traeger.py` file was renamed to `traeger_verschraubung.py` — update any references
- `src/tools/komplexSPooler/example.aufbau.py` is a **virtual assembly** (visual reference only, not a print-ready part)
- `src/tools/ magnetPuffer/magnetBuffer.py` — note the space in the directory name `magnetPuffer` (typo in filesystem, do not rename without updating all references)
