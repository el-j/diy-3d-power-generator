# 🗼 Bauanleitung: Savonius-Turm (Straight)

> Der Savonius-Rotor ist der einfachste Windrotor — zwei halbzylindrische Flügel erzeugen durch Schaufelsog hohe Anlaufdrehmomente bei niedrigen Windgeschwindigkeiten. Kein Anlaufstrom, kein Anlaufproblem.

---

## Benötigte Teile (pro Etage)

- [ ] 1× Savonius-Flügel A (TWR-STR-01)
- [ ] 1× Savonius-Flügel B (TWR-STR-02)
- [ ] 1× Mittelverbinder Skelett (TWR-CONN-01)
- [ ] 1× Vielzahn-Plug (TWR-PLUG-01)
- [ ] 4× M3 Einschmelzmutter (F-M3-HI)
- [ ] 4× M3×8 Madenschraube (F-M3x8-MDS)

### Zusätzlich für den kompletten Turm

- [ ] 1× Vierkant-Achse 10×10mm, Länge je nach Etagenanzahl (A-SQ10)

---

## Schritt 1: Savonius-Flügel drucken

### Druckeinstellungen

| Parameter | Wert |
|-----------|------|
| Material | PETG |
| Schichthöhe | 0.2mm |
| Füllung | 20% |
| Wände | 3 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Flach (Halbzylinder-Öffnung zeigt nach oben) |

### Durchführung

1. Lade `exports/middel-verbinder/Savonius_Straight_Fluegel_A.stl` in deinen Slicer
2. Flügel A flach auf dem Druckbett platzieren — die gebogene Außenseite liegt unten, die offene Seite zeigt nach oben
3. Wiederhole für `Savonius_Straight_Fluegel_B.stl` (Spiegelvariante)
4. Kein Support nötig — der gerade halbzylindrische Querschnitt ist vollständig selbsttragend
5. Drucke je 1× Flügel A und 1× Flügel B pro Etage

> 💡 **TIPP**: Flügel A und B sind Spiegelbilder voneinander. Beide können gleichzeitig auf dem Druckbett gedruckt werden. Die Wandstärke beträgt 2.4mm — halte Schichtlinienmuster (Perimeter) parallel zur Kurve für maximale Biegesteifigkeit.

---

## Schritt 2: Mittelverbinder drucken

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

1. Lade `exports/middel-verbinder/Mittel_Verbinder_Skelett_FLACH.stl`
2. Flach drucken — die 8mm Kappenhöhe ist die Z-Achse
3. Hoher Infill (40%) für strukturelle Festigkeit an den Flügelrillen!

> 💡 **TIPP**: Derselbe Verbinder wird für alle Turmvarianten (Helix, Savonius, Lenz2) verwendet. Du kannst vorhandene Bestände wiederverwenden.

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

1. **Flügel A einstecken**: Flügel A in eine der beiden Rillen des Verbinders stecken (Öffnung zeigt nach innen zur Achse)
2. **Flügel B einstecken**: Flügel B um **180°** versetzt in die gegenüberliegende Rille stecken — die Öffnungen zeigen aufeinander zu und bilden das klassische S-Profil
3. **Plug einsetzen**: Vielzahn-Plug (12-Zahn, R9.0/R7.8) in das zentrale Loch des Verbinders drücken
4. **Achse durchschieben**: Vierkant-Achse (10×10mm) durch Plug und Verbinder führen
5. **Madenschrauben anziehen**: 4× M3×8 Madenschrauben im Kragen gleichmäßig festziehen

> 💡 **TIPP**: Kontrolliere vor dem Festschrauben, dass die Schaufelöffnungen exakt 180° versetzt sind und das S-Profil in der Draufsicht symmetrisch wirkt. Unsymmetrie verursacht Unwucht und Vibration.

---

## Schritt 5: Etagen stapeln

1. Nächste Etage von oben aufsetzen
2. Flügel der oberen Etage in die **oberen** Rillen des unteren Verbinders stecken
3. Verbinder der oberen Etage von oben aufsetzen
4. Plug einsetzen und verschrauben
5. Wiederholen bis gewünschte Höhe erreicht

> 💡 **TIPP**: **Kein Twist zwischen den Etagen!** Beim Savonius-Straight bleiben alle Etagen gleich ausgerichtet (im Gegensatz zur Helix-Variante). Das erzeugt den klassischen Savonius-Schaufelzug, bei dem immer eine Schaufel optimal dem Wind zugewandt ist.

---

## Technische Referenz

| Merkmal | Wert |
|---------|------|
| Flügelprofil | Halbzylinder, 180° Bogen |
| Flügelhöhe | 240mm |
| Flügelradius | 66mm |
| Wandstärke | 2.4mm |
| Flügel pro Etage | 2 (A + B, 180° versetzt) |
| Verdrehung Etage zu Etage | 0° (keine — alle gleich) |
| Vielzahn | 12 Zähne, R9.0/R7.8 |
| Quellskript | `src/leaf/savonius_straight_leaf.py` |

---

## ✅ Fertig!

Dein Savonius-Turm sollte jetzt frei auf der Achse rotieren. Teste den Lauf von Hand — er sollte smooth und ohne Unwucht drehen. Bei leichtem Windhauch sollte er sofort anlaufen, ohne Anstoßen.

---

**Weiter mit**: [⚡ Generator-Bauanleitung](02_generator.md)
