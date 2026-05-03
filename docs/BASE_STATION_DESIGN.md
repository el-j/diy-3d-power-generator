# XXL Base Station Design Reference

**Assembly**: XL Base Station v3.0  
**Source**: `src/base/helix_station.py`  
**Status**: ACTIVE

---

## Design Philosophy

The XXL Base Station solves a deceptively difficult mechanical problem: house a spinning shaft, two tapered roller bearings, a removable stator, a rectifier PCB, and wall-mounting hardware — all in a weatherproof enclosure that fits on a 256×256 mm print bed and does not look like an industrial accident bolted to a wall.

The guiding constraint was radical flatness. Earlier prototypes ran 120 mm tall. The current design is **68 mm** — a 43% reduction achieved by rethinking where the bearing stack sits relative to the stator and by eliminating an internal electronics bay in favour of a front-access service hatch. The result is a low-profile disc that presents minimal wind resistance on its mounting surface and routes cables cleanly through a single port at the base of the hatch.

Serviceability drove the second major decision: the stator must be removable without disturbing the rotor or bearings. Rewinding a stator coil after a fault is a routine maintenance event. Requiring a full teardown for that task is unacceptable in a field-mounted turbine. The solution is a precision U-form opening in the front face that lets the 9 mm stator slide in and out laterally — bearings stay in place, rotor stays in place, downtime is minutes rather than hours.

---

## Key Innovations

### Ultra-Flat 68 mm Profile

Outer diameter is 220 mm (R=110 mm) and total height is 68 mm. The inner chamber runs to R=96 mm, giving exactly 4 mm radial clearance to the rotor at R=92 mm. That clearance is a hard minimum — the rotor must never exceed R=95 mm. The flat profile lowers the aerodynamic shadow behind the mounting surface and simplifies cable exit geometry.

### U-Form Front Opening and Stator Slot

The front face has a full-height U-shaped cutout: 213 mm wide (±106.5 mm from centre), 68 mm tall. This is not a maintenance port — it is a first-class design feature. The stator slides through it horizontally to seat in a precision slot at Z=25.8–35.3 mm. Slot dimensions are 9.5 mm high (9 mm stator + 0.5 mm clearance) at a radius of 99.5 mm. The slot is cut as a 99.5 mm cylindrical channel intersected with a 200×140 mm rectangular box. The service hatch mirrors this with a 199×120 mm passage at the same Z height, so the stator path is clear even with the hatch fitted.

### 3D-Printed Bearing Cup Substitute

Rather than sourcing the metal outer race of the 32005 tapered roller bearing separately, the design includes a printed substitute cup (`Ersatz_Lagerschale_32005`): 50 mm outer diameter, 12 mm tall, with an internal taper from R=19.5 mm at the base to R=23 mm at the top. Only the cup is printed; the roller and cone assembly are standard metal hardware. This removes a sourcing dependency while keeping the load-bearing contact surfaces metal.

---

## Part Reference

| Part ID | FreeCAD Name | Function | Qty |
|---|---|---|---|
| XL-HOUS-01 | `Basis_Gehaeuse_XXL` | Main housing, R=110 mm, H=68 mm | 1 |
| XL-DECK-01 | `Stacking_Lager_Deckel_FLACH` | Top lid with bearing pocket | 1 |
| XL-FLNSH-01 | `Wand_Flansch` | Wall mounting flange | 3 |
| XL-KLAP-01 | `Elektronik_Wartungs_Klappe` | Front service hatch | 1 |
| XL-BODEN-01 | `Wartungsklappen_Boden` | Detachable hatch floor | 1 |
| — | `Ersatz_Lagerschale_32005` | Printed bearing cup substitute | 1 |

### XL-HOUS-01 — Main Housing

Outer radius 110 mm, height 68 mm, inner chamber R=96 mm. U-form opening 213 mm wide × 68 mm tall. Stator slot at Z=25.8 mm, height 9.5 mm, radius 99.5 mm.

### XL-DECK-01 — Stacking Lid

Outer radius 110 mm, height 18 mm. Bearing pocket 50.2 mm diameter × 15 mm deep (32005 bearing). Upper guide lip: R=85–95.5 mm, 6 mm tall, for centering. Six 20 mm weight-relief holes at R=70 mm. Twelve M3 fasteners at R=104 mm, 30° spacing with 15° offset.

### XL-FLNSH-01 — Wall Flange (×3)

L-shaped bracket: vertical face 40×68 mm × 6 mm thick; horizontal arm 50×40 mm × 6 mm thick. Triangular gussets 4.0 mm reinforce the joint. Wall screws: 4× M3 at Z=15 mm and Z=53 mm, Y=±12 mm. Equipment mounting: 2× M6 on arm at Y=±10 mm, 38 mm deep.

### XL-KLAP-01 — Service Hatch

U-shaped, matching 213×150 mm front opening exactly. Wall thickness 6 mm roof and sides. Interior cavity 201×145 mm for PCB and wiring. Four PCB standoffs (4 mm OD, 5 mm tall) at (±25 mm, Z=20 mm) and (±25 mm, Z=50 mm). Cable port 10 mm diameter at X=0, Y=−135 mm, Z=10 mm. Two M3 lock screws at Y=−20 mm, Z=34 mm (left and right faces). Stator slot passage: 199×120 mm at Z=25.8 mm.

### XL-BODEN-01 — Hatch Floor

6 mm thick plate with R=96 mm rotor clearance cutout. Four corner tabs 12×12×8 mm with M3 counterbores for tool-free removal.

---

## Hardware BOM

| Item | Spec | Qty | Notes |
|---|---|---|---|
| Tapered roller bearing | 32005 — 29×50×15 mm | 1 | Dimensions real-measured, not datasheet |
| Hex socket cap screw | M3×10 | 12 | Lid-to-housing |
| Hex socket cap screw | M3×8 | 8 | Hatch lock + floor tabs |
| Hex socket cap screw | M6×40 | 6 | Wall flange equipment bolts (2× per flange) |
| Wood / masonry screw | M4 or M5 | 12 | Wall mounting (4× per flange) |
| Rectifier PCB | — | 1 | Mounts on hatch standoffs |
| Cable gland / sleeve | 10 mm ID | 1 | Hatch cable port |

---

## Print Settings

| Part | Material | Nozzle | Infill | Notes |
|---|---|---|---|---|
| XL-HOUS-01 | PLA-CF | 0.6 mm | 30% | Large print — check bed orientation |
| XL-DECK-01 | PLA-CF | 0.4 mm | 40% | Bearing pocket requires precision |
| XL-FLNSH-01 | PLA-CF | 0.6 mm | 60% | Structural — print all 3 |
| XL-KLAP-01 | PETG | 0.6 mm | 25% | Service part, slight flex acceptable |
| XL-BODEN-01 | PETG | 0.6 mm | 25% | Detachable, does not carry load |

All parts fit within the 256×256×256 mm Bambu P1S envelope. XL-HOUS-01 at 220 mm diameter prints diagonally on the bed. Orient so the U-form opening faces up to avoid internal support in the stator slot cavity.

---

## Critical Dimensions Summary

| Parameter | Value | Constraint |
|---|---|---|
| Outer diameter | 220 mm (R=110) | Print bed diagonal |
| Total height | 68 mm | Flat-profile target |
| Inner chamber | R=96 mm | 4 mm clearance to rotor R=92 |
| U-opening width | 213 mm | Stator insertion path |
| Stator slot Z | 25.8–35.3 mm | Synchronized with hatch |
| Stator slot height | 9.5 mm | 9 mm stator + 0.5 mm clearance |
| Bearing seat | Ø50.2 mm × 15 mm | 32005 press fit |
| Rotor hard limit | R=95 mm max | Geometry enforced in parameters.json |
