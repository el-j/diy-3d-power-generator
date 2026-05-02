# ⚡ Bauanleitung: Aero-Fan Generator v3.0 (20-Pol)

> Sandwich-Generator mit 2 Aero-Fan Rotoren (Ø184mm), 12 Capsule-Spulen, Vielzahn-Clamp-System.
> Quelle: `src/generator/helix_generator.py` · Material: PLA-CF für Rotoren/Clamps, PETG für Stator

---

## Benötigte Druckteile

| ID | STL-Datei (exports/generator/) | Menge | Material | Infill |
|----|-------------------------------|:-----:|----------|:------:|
| XLG-ROT-01 | 09_Rotor_AeroFan_TANK_FINAL_Oben | 1 | PLA-CF | 30% |
| XLG-ROT-02 | 05_Rotor_AeroFan_TANK_FINAL_Unten | 1 | PLA-CF | 30% |
| XLG-BP-01 | 10_Backplate_Ring_FLACH_Oben | 1 | PLA-CF | 25% |
| XLG-BP-02 | 04_Backplate_Ring_FLACH_Unten | 1 | PLA-CF | 25% |
| XLG-STAT-01 | 07_Stator_Schlitten_XXL | 1 | PETG | 25% |
| XLG-STAT-02 | 08_Stator_Donut_Deckel_INSET | 1 | PETG | 20% |
| XLG-CLAMP-01 | 03_Clamp_Rotor_Stack_Mega_30mm | 1 | PLA-CF | 80% |
| XLG-CLAMP-02 | 01_Clamp_Lager_Unten | 1 | PLA-CF | 80% |
| XLG-CLAMP-03 | 13_Clamp_Lager_Oben | 1 | PLA-CF | 80% |
| XLG-REDUZ-01 | 02_Lager_Reduzierung_Unten | 1 | PLA-CF | 80% |
| XLG-REDUZ-02 | 14_Lager_Reduzierung_Oben | 1 | PLA-CF | 80% |
| XLG-SPACER-01 | 11_Stator_Abstands_Spacer_10mm | 1 | PETG | 100% |
| XLG-PLUG-01 | 15_Magnet_Spacer_Kloetzchen | 20 | PETG | 100% |

## Benötigte Kaufteile

- [ ] 20× Neodym-Magnet **20×5×3mm N52** (vernickelt)
- [ ] 12× M3 Einschmelzmutter Ø4.2×5mm (3 Clamps × 4)
- [ ] 5× M5×20 Senkkopfschraube (Backplate auf Rotor)
- [ ] 4× M3×8 Zylinderkopfschraube (Stator-Deckel)
- [ ] ~100m Kupferlackdraht Ø0.5mm

---

## Schritt 1: Clamps vorbereiten — Einschmelzmuttern

Alle 3 Universal-Clamps (XLG-CLAMP-01/02/03) haben je 4× M3 Einschmelzmuttern **radial** im Kragen.

1. Lötkolben auf ~250°C, Muttern von außen in die radialen Taschen eindrücken
2. Jede Mutter sitzt in einer 4.2mm Bohrung, bündig mit der Kragen-Außenfläche

> 💡 Die Muttern fixieren später Madenschrauben (M3×5) zum Klemmen auf der Vielzahn-Achse.

---

## Schritt 2: Magnete einsetzen

> ⚠️ **KRITISCH: Polarität!** Beide Rotoren müssen sich **anziehen** (N-Pol von Rotor Oben zu S-Pol von Rotor Unten).

1. Alle N-Pole mit Edding markieren, bevor du anfängst
2. Je 20 Magnete abwechselnd N/S in die Taschen (radial ausgerichtet, R=74mm)
3. **Magnet-Spacer** (XLG-PLUG-01, 20 Stk.) über jeden Magneten setzen — hält Magnete höhenbündig
4. Test: Rotor Oben und Unten gegenüberhalten → müssen sich **anziehen**

---

## Schritt 3: Backplate-Ringe montieren

1. **XLG-BP-01** auf **XLG-ROT-01** (Oben) aufsetzen
2. 5× M5×20 Senkkopfschrauben durch die Backplate → Rotor → Einschmelzmuttern (R=74mm, 72° Abstand)
3. Gleiches für **XLG-BP-02** + **XLG-ROT-02** (Unten)

> Die Backplate ist ein flacher Donut R62–86mm mit 15 Material-Einspar-Taschen — kein Plug-Array mehr.

---

## Schritt 4: Spulen wickeln (12 Stück)

### Capsule-Wickeldaten

| Parameter | Wert |
|-----------|------|
| Spulenform | Oval / Capsule |
| Außenmaß Tasche | 40.4×26.4mm |
| Innen-Kern | 22×8mm |
| Taschen-Tiefe | 6mm (+ 0.5mm Kragen oben) |
| Draht | Kupferlackdraht Ø0.5mm |
| Windungen | ~120–150 pro Spule |

> 💡 Verwende den **Komplex-Spooler** (1:24 Übersetzung) für gleichmäßige Lagen.
> Alternativ: **Easy-Tool** mit Akkuschrauber. → [05_tools.md](05_tools.md)

---

## Schritt 5: Stator bestücken und verdrahten

1. 12 Spulen in die Capsule-Taschen des **XLG-STAT-01** einsetzen (R=74mm, je 30° Abstand)
2. **3-Phasen Stern-Schaltung** verdrahten:
   - Phase A: Spulen 1, 4, 7, 10
   - Phase B: Spulen 2, 5, 8, 11
   - Phase C: Spulen 3, 6, 9, 12
3. Kabel durch den **Ring-Kanal** (R82–88mm, Z=6.5, 1mm tief) und den radialen Kabelkanal nach außen
4. **XLG-STAT-02** (Donut-Deckel, 1.5mm dünn) auflegen — passt bündig in die Lid-Pocket des Stators
5. 4× M3×8 durch Deckel-Bohrungen (R=91mm, 45° versetzt) anziehen

---

## Schritt 6: Aufbau auf der Achse

Reihenfolge auf der Vielzahn-Achse **von unten nach oben**:

```
Basis-Station (Lager)
  → XLG-REDUZ-01  (Lager-Reduzierung Unten, Pressfit Ø29.15mm)
  → XLG-CLAMP-02  (Clamp Lager Unten, 180° gespiegelt)
  → XLG-CLAMP-01  (Clamp Rotor-Stack, 30mm Plug nach oben)
  → XLG-ROT-02    (Rotor Unten, Magnete zeigen nach oben)
  → XLG-SPACER-01 (Stator-Abstands-Spacer, 10mm, Vielzahn-Loch)
  → XLG-STAT-01   (Stator-Schlitten, wird in Basis-Schlitz eingefahren)
  → XLG-ROT-01    (Rotor Oben, Magnete zeigen nach unten)
  → XLG-CLAMP-03  (Clamp Lager Oben)
  → XLG-REDUZ-02  (Lager-Reduzierung Oben, 180° gespiegelt)
  → Turm-Vielzahn-Plug (TWR-PLUG-01)
```

---

## Schritt 7: Funktionstest

1. Von Hand drehen → leichtgängig, kein Schleifen am Stator
2. Multimeter an die 3 Phasen-Ausgänge (Stern-Mittelpunkt als Null)
3. Bei flotter Handdrehung: **>3V AC** pro Phase erwartet

> ⚠️ **<1V**: Magnetpolarität oder Phasen-Verschaltung prüfen. Rotor Oben und Unten müssen sich **anziehen**.

---

## ✅ Fertig!

**Weiter mit**: [🏗️ XXL Basis-Station](03_base_station.md)
