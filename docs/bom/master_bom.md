# 📋 Stückliste / Bill of Materials

> **Projekt**: Helix Helix Wind-Generator
> **Version**: 3.1.0
> **Stand**: 2026-05-02
> **Konfiguration**: XXL Basis (68mm) + Aero-Fan Generator (20-Pol) + Helix-Turm

---

## 🖨️ Druckteile / Printed Parts

### 🗼 Turm-Assembly (pro Etage × Anzahl Etagen)

| # | ID | Bauteil | STL-Name | Material | Menge/Etage | Infill |
|---|-----|---------|----------|----------|:-----------:|:------:|
| 1 | TWR-LEAF-01 | Helix-Flügel | Coreless_Helix_Fluegel | PETG | 2 | 15% |
| 2 | TWR-LEAF-02 | Savonius Straight Blade Set | Savonius_Straight_Blade_A/B | PETG | 2 | 20% |
| 3 | TWR-LEAF-03 | Lenz2 Rotor Stage | Lenz2_Rotor_Stage | PETG | 1 | 25% |
| 4 | TWR-LEAF-04 | Darrieus H Rotor Stage | Darrieus_H_Rotor_Stage | PETG | 1 | 30% |
| 5 | TWR-LEAF-05 | Gorlov Helical Rotor Stage | Gorlov_Helical_Rotor_Stage | PETG | 1 | 30% |
| 6 | TWR-CONN-01 | Mittelverbinder Skelett | Mittel_Verbinder_Skelett_FLACH | PETG | 1 | 40% |
| 7 | TWR-PLUG-01 | Vielzahn-Plug | Zwischen_Vielzahn_Plug | PETG | 1 | 60% |
| 8 | TWR-DISC-01 | Start-Scheibe Flach | Start_Scheibe_FLACH | PETG | 1 (gesamt) | 30% |

> 💡 **Turm ist modular** — wähle pro Build genau ein Rotorprinzip (Helix, Straight, Lenz2, Darrieus-H, Gorlov). Start-Scheibe nur 1× ganz unten.

---

### ⚡ Aero-Fan Generator (20-Pol)

| # | ID | Bauteil | STL-Name | Material | Menge | Infill |
|---|-----|---------|----------|----------|:-----:|:------:|
| 5  | XLG-ROT-01   | Rotor Oben (Aero-Fan)         | 09_Rotor_AeroFan_TANK_FINAL_Oben   | PLA-CF | 1  | 30% |
| 6  | XLG-ROT-02   | Rotor Unten (Aero-Fan)        | 05_Rotor_AeroFan_TANK_FINAL_Unten  | PLA-CF | 1  | 30% |
| 7  | XLG-BP-01    | Backplate Ring Oben           | 10_Backplate_Ring_FLACH_Oben       | PLA-CF | 1  | 25% |
| 8  | XLG-BP-02    | Backplate Ring Unten          | 04_Backplate_Ring_FLACH_Unten      | PLA-CF | 1  | 25% |
| 9  | XLG-STAT-01  | Stator-Schlitten XXL          | 07_Stator_Schlitten_XXL            | PETG   | 1  | 25% |
| 10 | XLG-STAT-02  | Stator Donut-Deckel           | 08_Stator_Donut_Deckel_INSET       | PETG   | 1  | 20% |
| 11 | XLG-CLAMP-01 | Clamp Rotor-Stack (30mm Plug) | 03_Clamp_Rotor_Stack_Mega_30mm     | PLA-CF | 1  | 80% |
| 12 | XLG-CLAMP-02 | Clamp Lager Unten (20mm)      | 01_Clamp_Lager_Unten               | PLA-CF | 1  | 80% |
| 13 | XLG-CLAMP-03 | Clamp Lager Oben (20mm)       | 13_Clamp_Lager_Oben                | PLA-CF | 1  | 80% |
| 14 | XLG-REDUZ-01 | Lager-Reduzierung Unten       | 02_Lager_Reduzierung_Unten         | PLA-CF | 1  | 80% |
| 15 | XLG-REDUZ-02 | Lager-Reduzierung Oben        | 14_Lager_Reduzierung_Oben          | PLA-CF | 1  | 80% |
| 16 | XLG-SPACER-01| Stator-Abstands-Spacer 10mm   | 11_Stator_Abstands_Spacer_10mm     | PETG   | 1  | 100% |
| 17 | XLG-PLUG-01  | Magnet-Spacer Klötzchen       | 15_Magnet_Spacer_Kloetzchen        | PETG   | 20 | 100% |

> 💡 **PLA-CF** (Carbon-Fiber) für Rotoren, Backplates und Clamps — höhere Steifigkeit bei Drehzahl.
> PETG für Stator-Teile — wärmebeständiger beim Wickeln.

---

### 🏗️ XXL Basis-Station (68mm)

| # | ID | Bauteil | STL-Name | Material | Menge | Infill |
|---|-----|---------|----------|----------|:-----:|:------:|
| 18 | XL-HOUS-01  | Basis-Gehäuse XXL          | Basis_Gehaeuse_XXL              | PETG | 1 | 25% |
| 19 | XL-DECK-01  | Stacking Lager-Deckel      | Stacking_Lager_Deckel_FLACH     | PETG | 1 | 40% |
| 20 | XL-FLNSH-01 | Wand-Flansch               | Wand_Flansch                    | PETG | 3 | 50% |
| 21 | XL-KLAP-01  | Elektronik Wartungs-Klappe | Elektronik_Wartungs_Klappe      | PETG | 1 | 20% |
| 22 | XL-BODEN-01 | Wartungsklappen-Boden      | Wartungsklappen_Boden           | PETG | 1 | 30% |

---

### 🔧 Werkzeuge (optional)

#### Easy-Tool (Akkuschrauber-Aufsatz)
| # | ID | Bauteil | Menge |
|---|-----|---------|:-----:|
| – | TOOL-EASY-01 | Winder Basis Bit | 1 |
| – | TOOL-EASY-02 | Winder Deckel Kern | 1 |

#### Komplex-Spooler (Traversier-Wickelmaschine, 1:24)
| # | ID | Bauteil | Menge |
|---|-----|---------|:-----:|
| – | TOOL-KS-01 | Maschinen-Basis Skeleton | 1 |
| – | TOOL-KS-02 | Steck-Türme | 8 |
| – | TOOL-KS-03..07 | Zahnräder (40Z, 10Z×3, 60Z) | 6 |
| – | TOOL-KS-08..10 | Achsen-Zubehör, Wickler, Träger | 3 |

#### Magnet-Puffer (Drahtspanner)
| # | ID | Bauteil | Menge |
|---|-----|---------|:-----:|
| – | TOOL-MB-01 | Basis mit Bremse | 1 |
| – | TOOL-MB-02 | Endblock (Magnet-Halter) | 1 |
| – | TOOL-MB-03 | Magnet-Schlitten (Pilz) | 1 |

---

## 🔩 Kaufteile / Purchased Parts

### Generator

| ID | Bauteil | Spezifikation | Menge |
|----|---------|--------------|:-----:|
| MAG-20x5x3 | Neodym-Magnet | 20×5×3mm, N52, vernickelt | **20** |
| F-M3-HI | M3 Einschmelzmutter | Ø4.2×5mm, Messing | 12 |
| F-M5x20-SK | M5×20 Senkkopf | DIN 7991, Edelstahl A2 | 5 |
| F-M3x8-ZK | M3×8 Zylinderkopf | DIN 912, Edelstahl A2 | 4 |

### Basis-Station

| ID | Bauteil | Spezifikation | Menge |
|----|---------|--------------|:-----:|
| B-29x50x15 | Kegelrollenlager | 29×50×15mm (REAL GEMESSEN!) | 1 |
| F-M3-HI | M3 Einschmelzmutter | Ø4.2×5mm | 24 |
| F-M3x16-SK | M3×16 Senkkopf | DIN 7991 | 6 |
| F-M6x30-SK | M6×30 Senkkopf | DIN 7991 | 6 |

### Achse & Elektronik

| Bauteil | Spezifikation | Menge |
|---------|--------------|:-----:|
| Vierkant-Alu-Profil | 10×10mm, L≈800–1200mm | 1 |
| Kupferlackdraht | Ø0.5mm (AWG 24), PU-isoliert | ~100m |
| Drehstrom-Gleichrichter | 3-Phasen Brücke, 35A | 1 |

> ⚠️ **MAGNETE**: N52 Neodym sind extrem stark — Fingerschutz beim Einsetzen!

---

## 📊 Zusammenfassung (3-Etagen Turm)

| Kategorie | Anzahl |
|-----------|:------:|
| Druckteile Generator | 13 |
| Druckteile Basis | 5 |
| Druckteile Turm (3 Etagen) | 10 |
| Druckteile Werkzeuge (Komplex-Set) | 15 |
| Neodym-Magnete 20×5×3mm N52 | 20 |
| Einschmelzmuttern M3 | ~36 |
| Kegelrollenlager 29×50×15 | 1 |
| Kupferlackdraht Ø0.5mm | ~100m |
| Geschätzte Druckzeit | ~60h |
| Geschätztes Filament | ~1.2kg |

---

## 📝 Änderungshistorie

| Version | Datum | Änderungen |
|---------|-------|------------|
| 3.1.0 | 2026-05-02 | Rotorvariantenset ergänzt (Savonius Straight, Lenz2, Darrieus-H, Gorlov) + Landing-Page Playground Struktur |
| 3.0.0 | 2026-05-02 | Aero-Fan Rotor v3, Clamp-System, Lager-Reduzierung, 68mm Basis, neue src/ Struktur |
| 2.1.0 | 2026-04-30 | XLG-PLUG-01, XLG-SPACER-01/02, Stator-Deckel Lochfix |
| 2.0.0 | 2026-04-29 | XXL Basis 220mm, XXL Generator Capsule-Spulen |
| 1.0.0 | 2026-04-28 | Erstversion |
