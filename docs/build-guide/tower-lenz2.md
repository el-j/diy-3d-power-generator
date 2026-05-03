# 🗼 Bauanleitung: Lenz2-Turm

> Der Lenz2-Rotor kombiniert das hohe Anlaufdrehmoment des Savonius mit Vortex-Auftrieb am Öffnungsrand — 3 Flügel à 210° Bogenwinkel ergeben eine kompakte Turbine mit überraschendem Wirkungsgrad für Stadtwind.

---

## Benötigte Teile (pro Etage)

- [ ] 3× Lenz2-Flügel (TWR-LEN-01)
- [ ] 1× Mittelverbinder Skelett 3-Arm (TWR-CONN-03)
- [ ] 1× Vielzahn-Plug (TWR-PLUG-01)
- [ ] 4× M3 Einschmelzmutter (F-M3-HI)
- [ ] 4× M3×8 Madenschraube (F-M3x8-MDS)

### Zusätzlich für den kompletten Turm

- [ ] 1× Vierkant-Achse 10×10mm, Länge je nach Etagenanzahl (A-SQ10)

---

## Schritt 1: Lenz2-Flügel drucken

### Druckeinstellungen

| Parameter | Wert |
|-----------|------|
| Material | PETG oder PLA-CF |
| Schichthöhe | 0.2mm |
| Füllung | 30% |
| Wände | 3 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Stehend (Höhe 240mm = Z-Achse) |

### Durchführung

1. Lade `exports/middel-verbinder/Lenz2_Fluegel.stl` in deinen Slicer
2. Flügel stehend auf dem Druckbett platzieren — die 240mm Blatthöhe ist die Z-Achse
3. Kein Support nötig — der 210°-Bogen ist geometrisch selbsttragend in vertikaler Ausrichtung
4. Drucke **3 Stück** pro Etage (alle Flügel sind identisch)

> 💡 **TIPP**: PLA-CF (Carbon-gefülltes PLA) erzeugt besonders steife Flügel bei geringem Gewicht — empfohlen für Türme ab 4 Etagen. Standard-PETG reicht für 1–3 Etagen vollständig aus. Innenwandradius: ≈38.5mm (66mm × 0.62 − 2.4mm Wandstärke).

---

## Schritt 2: Mittelverbinder 3-Arm drucken

### Druckeinstellungen

| Parameter | Wert |
|-----------|------|
| Material | PETG |
| Schichthöhe | 0.2mm |
| Füllung | 40% |
| Wände | 4 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Flach (8mm Höhe = Z-Achse) |

### Durchführung

1. Lade `exports/middel-verbinder/Mittel_Verbinder_Skelett_FLACH_3arm.stl`
2. Flach drucken — die 8mm Kappenhöhe ist die Z-Achse
3. Der 3-Arm-Verbinder hat **3 Flügelrillen im 120°-Raster** anstelle der 2 Rillen beim Standard-Verbinder
4. Hoher Infill (40%) für strukturelle Festigkeit an allen drei Armen!

> ⚠️ **ACHTUNG**: Den 2-Arm-Verbinder (TWR-CONN-01) der Helix- und Savonius-Variante **nicht** für den Lenz2 verwenden! Der 3-Arm-Verbinder (TWR-CONN-03) hat ein anderes Rillen-Raster.

---

## Schritt 3: Vielzahn-Plug drucken + bestücken

### Druckeinstellungen

| Parameter | Wert |
|-----------|------|
| Material | PETG |
| Füllung | 60% |
| Wände | 4 |

### Einschmelzmuttern einsetzen

1. Lötkolben auf **250°C** vorheizen
2. Einschmelzmutter mit der Lötkolben-Spitze aufnehmen
3. Langsam und gerade in die 4 Taschen des Kragens eindrücken
4. Bündig mit der Oberfläche abschließen lassen

> ⚠️ **ACHTUNG**: Die Muttern werden heiß! Nicht mit Fingern berühren. Lötkolben-Spitze nach dem Einsetzen sofort entfernen, nicht nachdrücken.

---

## Schritt 4: Zusammenbau einer Etage

1. **Ersten Flügel einstecken**: Flügel in eine der drei Rillen des Verbinders stecken — die Becheröffnung (210°-Bogen) zeigt radial nach außen
2. **Zweiten Flügel einstecken**: Um **120°** versetzt in die zweite Rille stecken, Öffnung ebenfalls radial nach außen
3. **Dritten Flügel einstecken**: Um weitere **120°** versetzt (also 240° zum ersten) in die dritte Rille stecken
4. **Plug einsetzen**: Vielzahn-Plug (12-Zahn, R9.0/R7.8) in das zentrale Loch des Verbinders drücken
5. **Achse durchschieben**: Vierkant-Achse (10×10mm) durch Plug und Verbinder führen
6. **Madenschrauben anziehen**: 4× M3×8 Madenschrauben im Kragen gleichmäßig festziehen

> 💡 **TIPP**: Alle drei Flügel sind identisch — keine Spiegelvarianten wie beim Savonius. Kontrolliere in der Draufsicht, dass die drei Öffnungen gleichmäßig im Kreis verteilt sind und alle in dieselbe Umlaufrichtung zeigen (Schaufelöffnung vorne, Rücken hinten).

---

## Schritt 5: Etagen stapeln

1. Nächste Etage von oben aufsetzen
2. Flügel der oberen Etage in die **oberen** Rillen des unteren Verbinders stecken
3. Verbinder der oberen Etage von oben aufsetzen
4. Plug einsetzen und verschrauben
5. Wiederholen bis gewünschte Höhe erreicht

> 💡 **TIPP**: Die 210°-Öffnung ist breiter als ein Halbkreis — sie erzeugt an der Eintrittskante einen Vortex, der Auftrieb über reinen Strömungswiderstand hinaus liefert. Dieser Effekt wirkt über die gesamte Blatthöhe und steigert den Wirkungsgrad gegenüber klassischem Savonius spürbar.

---

## Technische Referenz

| Merkmal | Wert |
|---------|------|
| Flügelprofil | Asymmetrischer Bogen, 210° Öffnungswinkel |
| Flügelhöhe | 240mm |
| Außenradius | 66mm |
| Innenradius | ≈38.5mm (66mm × 0.62 − 2.4mm) |
| Wandstärke | 2.4mm |
| Flügel pro Etage | 3 (identisch, 120° versetzt) |
| Verdrehung Etage zu Etage | Optional (0° oder 60° für bessere Windabdeckung) |
| Vielzahn | 12 Zähne, R9.0/R7.8 |
| Quellskript | `src/leaf/lenz2_leaf.py` |

---

## ✅ Fertig!

Dein Lenz2-Turm sollte jetzt frei auf der Achse rotieren. Teste den Lauf von Hand — er sollte smooth und ohne Unwucht drehen. Schon bei leichtem Wind (ab ca. 2 m/s) sollte der Rotor selbstständig anlaufen, ohne Anstoßen.

---

**Weiter mit**: [⚡ Generator-Bauanleitung](02_generator.md)
