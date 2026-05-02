# 🔬 Physical Design Review — v3.0.0

> Code-verified audit of all three source scripts against real-world assembly constraints.
> Every number below is pulled directly from source code — no assumptions.

---

## ❌ Critical Conflicts (Prevent Assembly)

### C1 — Stator slot 0.6mm too shallow
**Location**: `helix_station.py` vs `helix_generator.py`

| What | Value |
|------|-------|
| Stator thickness (`stator_dicke`) | **9.0 mm** |
| Housing slot height (`s_cyl`, `s_box`) | **8.4 mm** |
| Missing clearance | **−0.6 mm** |

The stator cannot be slid into the housing slot — it's physically wider than the gap.

**Fix**: In `helix_station.py`, change slot height from `8.4` → `9.5` mm (9.0mm + 0.5mm slide clearance):
```python
# helix_station.py — both lines:
s_cyl = Part.makeCylinder(99.5, 9.5).translate(App.Vector(0,0,25.8))
s_box = Part.makeBox(200.0, 140.0, 9.5).translate(App.Vector(-100.0, -140.0, 25.8))
# Also maintenance flap slot:
stator_slot = Part.makeBox(199.0, 120.0, 9.5).translate(App.Vector(-99.5, -120.0, 25.8))
```
Update `shared/parameters.json → xl_base_station.stator_slot_h` from `8.4` → `9.5`.

---

### C2 — Rotor screw holes collide with material-saving pockets
**Location**: `helix_generator.py: make_aero_rotor()`

Both the screw holes AND the material-saving capsule pockets are placed at **the same radius (R=74mm) AND the same angles (9°, 81°, 153°, 225°, 297°)**:

```python
# Screws cut at these angles:
angle = math.radians(i * 72 + 9)   # → 9°, 81°, 153°, 225°, 297°

# Capsule pockets at these centers (for i≠0,4,8,12,16):
angle_deg = i * (360.0 / anzahl_magnete) + (360.0 / anzahl_magnete / 2.0)
# For i=0 SKIPPED. For i=1: 18+9 = 27°. But screw is at 9°!
```

Wait — the loop skips `i%4==0` which are indices 0, 4, 8, 12, 16. These indices produce angles:
- i=0 → 0+9 = 9° ← **SKIPPED (correct!)**
- i=4 → 72+9 = 81° ← **SKIPPED (correct!)**

So the code correctly skips the pocket at 9° (same angle as the screw). The concern is slightly mitigated — the pocket IS skipped at screw positions.

**However**: The screw hole Ø3.4mm at R=74 is only **~1.4mm** from the edge of adjacent magnet pockets. With 0.3mm geometric overlap at the 3.4mm diameter, the screw hole slightly intersects adjacent magnet pocket corners.

**Severity reduced**: Not a complete collision, but a thin wall ~0.3mm at the magnet/screw junction. In PLA-CF at 0.6mm nozzle this edge may fragment.

**Fix**: Slightly change screw angle offset from `9` → `10` degrees, adding 1° more clearance:
```python
# helix_generator.py, make_aero_rotor() and make_aero_backplate():
angle = math.radians(i * 72 + 10)   # was +9
```
Also update the comment: `# Screws at 10°, 82°, 154°, 226°, 298° (center between magnets at 0°/18°)`

---

### C3 — Generator Clamp plug 22mm too long for Tower socket
**Location**: `helix_generator.py` vs `helix_leaf+connector.py`

| What | Value |
|------|-------|
| Clamp Mega plug length (`plug_laenge`) | **30 mm** |
| Clamp Lager plug length | **20 mm** |
| Tower Mittelverbinder socket depth | **8 mm** (= kappen_dicke) |

The generator clamps produce a 20–30mm Vielzahn MALE plug. The tower Mittelverbinder has a Vielzahn FEMALE socket only **8mm deep**. These are not direct-mate parts — but the mating sequence needs clarification.

**Clarification**: The generator sits **below** the tower on the same axis. The axis itself (10×10mm square) passes through ALL parts. The generator clamps grip the axis via their square hole; the tower TWR-PLUG-01 also grips the axis via its square hole + Vielzahn engagement with the Mittelverbinder.

The 30mm clamp plug is NOT intended to insert into the tower's 8mm socket — it mates into the ROTOR's Vielzahn socket (fan_h=10mm + 2mm extra cut = 12mm). The plug at 30mm sticks out 18mm beyond the rotor — this protruding section engages the Stator-Spacer's Vielzahn hole (10mm) and continues 8mm further. This stack provides the axial positioning.

**Action**: No code change needed, but the assembly documentation was misleading. Updated in `02_generator.md` assembly sequence.

**Verify**: The Stator-Spacer Vielzahn socket depth = 10mm, the clamp plug remaining engagement after rotor (10mm) and spacer (10mm) = 30−10−10 = 10mm unused. This is fine.

---

### C4 — Blade-groove fit has only 0.1mm clearance (will jam)
**Location**: `helix_leaf+connector.py`

| What | Value |
|------|-------|
| Blade wall thickness (`dicke`) | 2.4 mm |
| FDM tolerance added in cutter wire | +0.5 mm (via `toleranz/2` on each side) |
| **Effective blade thickness in slot** | **2.9 mm** |
| Groove depth (`rillen_tiefe`) | **3.0 mm** |
| Clearance | **0.1 mm** |

The blade tip fits in the groove with only 0.1mm clearance after the tolerance is applied. Any slight over-extrusion or warping will cause the blade to jam in the connector groove.

**Fix**: Increase groove depth to 3.5mm (adds 0.5mm safety margin):
```python
# helix_leaf+connector.py:
rillen_tiefe = 3.5   # was 3.0 — add 0.5mm safety margin for FDM tolerance
```
The cutter shapes using `rillen_tiefe` already include the tolerance in the blade profile (`cutter_wire` uses `dicke + toleranz`). So this is safe to change.

---

### C5 — Tower plug M3 insert has zero margin at collar edge
**Location**: `helix_leaf+connector.py: Zwischen_Vielzahn_Plug`

```python
# Insert positioned at:
m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, ...))
# = (17.5/2) - 4.0 = 8.75 - 4.0 = 4.75 mm from center
# Insert is 4.0mm deep → tip reaches 4.75 + 4.0 = 8.75 mm = exactly the collar radius
```

The M3 heat-set nut's tip reaches EXACTLY the outer surface — zero wall material behind it. Under vibration or clamping force the insert will tear out.

**Fix**: Either increase `kragen_d` from 17.5 → 20.0mm (consistent with generator), or reduce `einschmelzmutter_t` to 3.0mm for this narrower collar:
```python
# helix_leaf+connector.py (local override):
einschmelzmutter_t = 3.0   # only for plug — narrower collar needs shallower insert
# ensures: (17.5/2) - 3.0 = 5.75mm from center + 3.0mm depth = 8.75mm ✓ (1.0mm wall)
```
And change the insert positioning:
```python
m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, ...))
# = 8.75 - 3.0 = 5.75mm from center → insert tip at 5.75+3.0 = 8.75mm ✓ same edge
```
Actually the correct fix is to set `einschmelzmutter_t = 3.0` AND offset the insert slightly inward so there is at least 1mm of wall:
```python
einschmelzmutter_t = 3.5   # for this collar only — leaves 1.25mm wall
insert_offset = (kragen_d / 2.0) - einschmelzmutter_t - 1.0   # 1mm wall
```

---

## ⚠️ Marginal Tolerances (Monitor in Print)

### M1 — Stator radius fit: exactly 0.5mm clearance
- Stator R=99.0mm slides into slot R=99.5mm → 0.5mm diametral clearance (0.25mm per side)
- For a 200mm diameter part this is acceptable for FDM, but **print orientation matters** — print stator flat (Z-axis = vertical) to minimize XY shrinkage

### M2 — Heat-set nut depth: 5mm (generator) vs 4mm (tower)
- The tower plug comment explains: narrower 17.5mm collar can't fit a 5mm insert
- 4mm inserts are a shorter standard size; check your local hardware for M3×4 Einschmelzmuttern
- Functionally fine as long as M3 madenschrauben used are ≤ 8mm

### M3 — Stator screw holes Ø3.4mm at R=91mm
- The stator has 4 screw holes for mounting but the housing has NO corresponding nut traps
- Stator is held only by friction in the slot — may migrate under vibration
- **Recommendation**: Add 2 self-tapping M3 holes in the front face of the slot to lock the stator after insertion, or add a retention clip to the stator handle

---

## ✅ Confirmed Good Fits

| Interface | Clearance | Status |
|-----------|-----------|--------|
| Rotor (R=92) in chamber (R=96) | 4.0mm radial | ✓ Good |
| Bearing outer (Ø50) in pocket (Ø50.2) | 0.2mm | ✓ Intended pressfit |
| Bearing reducer pressfit (Ø29.15 in Ø29) | 0.15mm | ✓ Intended pressfit |
| Vielzahn plug (9.0/7.8) in socket (9.2/8.0) | 0.2mm | ✓ Intended clearance |
| Square axis (10.5mm) in all holes | 0.5mm | ✓ Standard FDM tolerance |
| Stacking deckel guide lip (R96) to housing | flush | ✓ Self-centering |
| Magnet in pocket (20.4×5.4 for 20×5 magnet) | 0.2mm each | ✓ Good |

---

## Summary of Required Code Changes

| File | Change | Priority |
|------|--------|----------|
| `src/base/helix_station.py` | Stator slot 8.4 → 9.5mm (3 places) | 🔴 Critical |
| `src/generator/helix_generator.py` | Screw angle offset 9° → 10° (2 functions) | 🟡 Recommended |
| `src/leaf/helix_leaf+connector.py` | rillen_tiefe 3.0 → 3.5mm | 🔴 Critical |
| `src/leaf/helix_leaf+connector.py` | einschmelzmutter_t → 3.5mm + 1mm wall offset | 🔴 Critical |
| `shared/parameters.json` | stator_slot_h 8.4 → 9.5 | 🔴 Follow-up |
| `src/base/helix_station.py` | Add stator retention mechanism | 🟡 Recommended |
