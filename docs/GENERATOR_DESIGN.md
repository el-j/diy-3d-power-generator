# Aero-Fan Generator — Design Document

**Project**: WindPower-3D | **Assembly**: XL Generator v3.0 | **Status**: Active

---

## Overview

The Aero-Fan generator is a 3D-printable **axial-flux permanent magnet generator (AFPMG)** designed for small-scale wind power applications. It is built around a TORUS-NS dual-rotor topology and introduces two notable mechanical innovations: a dual-function fan/magnet rotor and a unified spline coupling system that eliminates tool dependencies during blade changes.

---

## Key Innovations

> **Dual-function rotor**: The rotor plates (`XLG-ROT-01`, `XLG-ROT-02`) carry both the permanent magnets and 11 aerodynamic fan blades in a single printed part. As the rotor spins, it simultaneously generates electricity through rotating magnetic fields and forces cooling airflow across the stator coils via centrifugal action — removing the need for a separate cooling fan while keeping the assembly compact.

> **Capsule coils**: The stator (`XLG-STAT-01`) uses oval (stadium-shaped) coil pockets rather than round ones, aligning coil geometry with the arc of the magnet circle (R=74 mm). This reduces end-winding waste and improves copper fill in the radial space available.

> **Unified Vielzahn spline**: Every rotary connection in the system uses the same 12-tooth spline profile — tower blades, generator rotor, and tools all share `r_out=9.0 mm`, `r_in=7.8 mm`, 12 teeth. This gives 30° indexing resolution and enables tool-free hot-swap of components.

---

## Design Philosophy

The generator is sized to fit a 256×256×256 mm Bambu P1S print bed and targets a reliable 10–50 W output range at low wind speeds (6–12 m/s). Every dimensional choice reflects a compromise between magnetic performance and printability:

- **Axial-flux topology** keeps the generator thin and flat — ideal for integration into a vertical tower without adding height.
- **20-pole, 12-coil configuration** (TORUS-NS) gives a 3-phase output at usable frequencies even at low RPM. At 100 RPM the electrical frequency is approximately 33 Hz (`100 RPM × 20 poles / 60`).
- **N52 neodymium magnets** (20×5×3 mm) were chosen as a standard stocked size. The magnet circle radius of R=74 mm also doubles as the rotor fastening radius, reducing the number of unique drill positions.
- **4 mm rotor-to-chamber clearance** (`rotor R=92 mm`, inner chamber `R=96 mm`) is maintained as a hard constraint — the rotor must never exceed R=95 mm.
- **PLA-CF for structural parts**, PETG for the stator: carbon-fiber PLA provides stiffness at the rotor and bearing interfaces; PETG tolerates the heat generated in the stator coils.

---

## How It Works

**Faraday's law** states that a changing magnetic flux through a coil induces a voltage proportional to the rate of change. In an axial-flux machine, the magnets are oriented with their poles facing axially (parallel to the shaft), and the coils sit in a flat disk (the stator) between two rotor plates. As each magnet passes over a coil, the flux through that coil changes sign (N→S polarity), inducing an AC voltage.

The dual-rotor arrangement (one rotor plate above and one below the stator) doubles the flux linkage per coil compared to a single-sided design, increasing output for the same rotor diameter.

The 12 stator coils are wired in a **3-phase star (Y) configuration** with 4 coils per phase. At 100 RPM with 20 pole pairs the phase voltage frequency is `f = n × p / 60 = 100 × 10 / 60 ≈ 16.7 Hz` electrical. The output is rectified to DC for battery charging or direct LED load testing. Design efficiency target is η=72%.

---

## Generator Topology

| Parameter | Value |
|---|---|
| Type | Axial-flux, dual-rotor, single-stator (TORUS-NS) |
| Poles | 20 (10 pole pairs) |
| Coils | 12 capsule-shaped (4 per phase, 3-phase AC) |
| Magnet spec | 20×5×3 mm N52 neodymium |
| Magnet circle radius | R=74 mm (= rotor screw radius) |
| Design output | 10–50 W at 6–12 m/s |
| Efficiency target | η=72% |

---

## The Aero-Fan Rotor (`XLG-ROT-01` / `XLG-ROT-02`)

| Parameter | Value |
|---|---|
| Total radius | 92 mm (Ø184 mm) |
| Hub radius | 16.5 mm |
| Outer structural rim | R=92–102 mm |
| Fan blades | 11 aerodynamic blades (lofted profile) |
| Inner blade profile | R=11.5 mm, chord=22 mm, pitch angle=75° |
| Outer blade profile | R=107 mm, chord=32 mm, pitch angle=50°, sweep=45° |
| Weight-relief pockets | 15 capsule pockets (18×10 mm), avoiding 5 screw positions |
| Fastening | 5× M3 heat-set inserts at R=74 mm: 10°, 82°, 154°, 226°, 298° |
| Magnet lip | 0.6 mm retaining edge per pocket |

The **backplates** (`XLG-BP-01` / `XLG-BP-02`) are thin structural rings (R=62–86 mm, 4 mm height) with synchronized magnet pockets that close the magnet retention from the opposite side.

---

## The Stator (`XLG-STAT-01` / `XLG-STAT-02`)

| Parameter | Value |
|---|---|
| Outer radius | 99 mm |
| Thickness | 9 mm |
| Base bore | R=16 mm (shaft clearance) |
| Coil pocket (outer) | 40.4×26.4 mm (0.4 mm clearance) |
| Coil winding core | 22×8 mm |
| Coil depth | 6 mm |
| Coil count | 12 at R=74 mm |
| Winding | 120–150 turns, 0.5 mm enameled copper wire |
| Weight-relief holes | 6× at R=35 mm |
| Cable channel | Ring channel R=82–88 mm at Z=6.5 mm + radial handle channel |

The stator lid (`XLG-STAT-02`) is a thin cover ring (R=50.5–95.5 mm, 1.5 mm thick) with cutouts matching the coil pockets, allowing wire routing after winding.

---

## Assembly Stack (bottom to top)

| Z position | Part | Part ID |
|---|---|---|
| −80 mm | Bearing reducer (bottom) | `XLG-REDUZ-01` |
| −60 mm | Bearing clamp (bottom, rotated 180°) | `XLG-CLAMP-02` |
| −50 mm | Rotor stack clamp (30 mm plug) | `XLG-CLAMP-01` |
| −30 mm | Backplate (bottom) | `XLG-BP-01` |
| −20 mm | Aero-Fan Rotor (bottom) | `XLG-ROT-01` |
| −5 mm | Stator spacer 10 mm | `XLG-SPACER-01` |
| 0–9 mm | Stator housing | `XLG-STAT-01` |
| 10–25 mm | Stator lid (inset) | `XLG-STAT-02` |
| 35 mm | Aero-Fan Rotor (top) | `XLG-ROT-02` |
| 50 mm | Backplate (top) | `XLG-BP-02` |
| 90 mm | Bearing clamp (top) | `XLG-CLAMP-03` |
| 110 mm | Bearing reducer (top, rotated 180°) | `XLG-REDUZ-02` |

---

## Bearing System

- **Type**: Tapered roller bearing 32005 — 29×50×15 mm (real measured dimensions)
- **Press fit**: 0.15 mm interference fit for shaft coupling
- **Bearing reducer** (`XLG-REDUZ-01` / `XLG-REDUZ-02`): Conical adapter tapering 27.5→29.3 mm over 2 mm taper length, with a 34 mm collar

---

## Vielzahn Coupling System

All rotary connections throughout the system (tower blades, generator rotor, tools) share a single unified spline profile to avoid mismatched parts:

| Parameter | Value |
|---|---|
| Teeth | 12 (30° indexing) |
| Outer radius | 9.0 mm |
| Inner radius | 7.8 mm |
| Orientation offset | +15° (aligns teeth to square shaft corners) |
| Square shaft bore | 10×10 mm + 0.5 mm tolerance |

---

## Print Settings

| Part | Material | Nozzle | Infill | Notes |
|---|---|---|---|---|
| `XLG-ROT-01` / `XLG-ROT-02` | PLA-CF | 0.6 mm | 40% | Carbon fiber for stiffness |
| `XLG-STAT-01` | PETG | 0.6 mm | 30% | Heat-resistant for coil area |
| `XLG-BP-01` / `XLG-BP-02` | PLA-CF | 0.6 mm | 40% | Thin ring, needs strength |
| `XLG-CLAMP-*` | PLA-CF | 0.4 mm | 100% | Bearing contact surface |
| `XLG-REDUZ-*` | PLA-CF | 0.4 mm | 100% | Press-fit precision required |

---

## Estimated Electrical Output

| Condition | Value |
|---|---|
| Electrical frequency at 100 RPM | ~16.7 Hz (100 × 10 pole pairs / 60) |
| Design wind speed range | 6–12 m/s |
| Design output range | 10–50 W |
| Output type | 3-phase AC → rectified DC |
| Use cases | Battery charging, LED load testing |
| Efficiency target | η=72% |

---

*Source script*: `src/generator/helix_generator.py` | *Parameters*: `shared/parameters.json` § `xl_generator`
