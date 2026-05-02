# WindPower-3D — Agent Handbook

> Helix Helix Wind-Generator: Parametric 3D-printed axial-flux generator + tower.
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
│   ├── generator/          ← ACTIVE: Aero-Fan Generator (v3.0)
│   │   └── helix_generator.py      ← 20-pole Aero-Fan generator (13 parts)
│   ├── base/               ← ACTIVE: XXL Base Station 68mm (v3.0)
│   │   └── helix_station.py        ← XXL base station (Ø220mm, 68mm Höhe)
│   ├── leaf/               ← ACTIVE: Tower blades + connector
│   │   └── helix_leaf+connector.py ← Helix blade, connector, plug, start disc
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
| Aero-Fan Generator | **ACTIVE v3.0** | `src/generator/helix_generator.py` | XLG-ROT-01/02, XLG-BP-01/02, XLG-STAT-01/02, XLG-CLAMP-01..03, XLG-REDUZ-01/02, XLG-SPACER-01, XLG-PLUG-01 |
| XXL Base Station | **ACTIVE v3.0** | `src/base/helix_station.py` | XL-HOUS-01, XL-DECK-01, XL-FLNSH-01×3, XL-KLAP-01, XL-BODEN-01 |
| Tower (Helix) | **ACTIVE** | `src/leaf/helix_leaf+connector.py` | TWR-LEAF-01, TWR-CONN-01, TWR-PLUG-01, TWR-DISC-01 |
| Komplex-Spooler | **ACTIVE v2.1** | `src/tools/komplexSPooler/` | TOOL-KS-01..10 |
| Easy-Tool | **ACTIVE** | `src/tools/easy_tool_big_spools-accuschrauber.py` | TOOL-EASY-01/02 |
| Magnet-Puffer | **ACTIVE** | `src/tools/ magnetPuffer/magnetBuffer.py` | TOOL-MB-01/02/03 |

---

## Key Dimensions (commit them to memory)

| Parameter | Value | Where |
|-----------|-------|-------|
| Vierkant-Achse | 10×10mm | `global.achse_kantenlaenge` |
| Vielzahn | 12-Zahn, R9.0/R7.8 (UNIFIED!) | `global.vielzahn_*` — same for tower + generator |
| Aero-Fan Rotor Radius | Ø184mm (R=92) | `xl_generator.rotor_radius` |
| Rotor-Platte Höhe | 10mm | `xl_generator.rotor_platte_h` |
| Magnet-Kreis Radius | R=74mm = Schrauben-Radius | `xl_generator.mag_kreis_r` |
| Magnete pro Rotor | 20× (20×5×3mm N52) | `xl_generator.anzahl_magnete` |
| Capsule-Spulen | 12× (40×26mm außen, 22×8mm innen) | `xl_generator.spule_*` |
| Stator Radius | R=99mm | `xl_generator.stator_radius` |
| Stator Dicke | 9mm | `xl_generator.stator_dicke` |
| Stator-Schlitz Z-Position | Z=25.8mm | `xl_generator.stator_slot_z` |
| XXL Basis Radius | R=110mm (Ø220mm) | `xl_base_station.fuss_radius` |
| XXL Basis Höhe | **68mm** (war 120mm!) | `xl_base_station.gehaeuse_h` |
| Innenkammer Radius | R=96mm (2mm Luft zum Rotor) | `xl_base_station.inner_chamber_r` |
| Kegelrollenlager | 29×50×15mm (REAL GEMESSEN) | `xl_base_station.lager_*` |
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
#   exec(open("/path/to/windpower-3d/freecad_loader.py").read()); run("generator/helix_generator")
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
3. **Vielzahn is UNIFIED**: `zaehne=12, r_out=9.0, r_in=7.8` — same across tower, generator, tools. Never diverge.
4. **Capsule shapes**: always use `make_capsule()` from freecad_utils — do not reimplement inline
5. **Export naming**: FreeCAD exports use the object name as filename prefix: `DocName-ObjName.stl`
6. **After any geometry fix**: bump the assembly JSON version (patch = 3.0.0 → 3.0.1)
7. **Stator slot**: Gehäuse-Schlitz bei Z=25.8, Höhe 8.4mm → Stator-Dicke 9mm minus 0.6mm Spiel
8. **Rotor clears inner chamber**: Rotor R=92mm, Innenkammer R=96mm → 4mm Luft. Niemals Rotor größer als R=95 machen.

---

## Known Issues / Watch Out

- `exports/flügel/` enthält eine Start-Scheibe-STL, **nicht** ein Flügel — Fehlbenennung des Ordners
- `exports/xl_basis/generator/` enthält **ältere** Backplate-Versionen — neueste STLs liegen in `exports/generator/`
- `src/tools/komplexSPooler/example.aufbau.py` ist ein **virtueller Aufbau** (nur visuelle Referenz, kein Druckteil)
- `src/tools/ magnetPuffer/magnetBuffer.py` — Leerzeichen im Verzeichnisnamen `magnetPuffer` (Filesystem-Typo, nicht umbenennen ohne alle Referenzen zu aktualisieren)
- `exports/basis/` enthält **Legacy**-STLs der alten kleinen Basis (Savonius_Base_Station3/4) — nicht mehr aktiv
