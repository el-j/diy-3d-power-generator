# 🗼 Bauanleitung: Helix-Turm

> Der Turm besteht aus modularen Etagen. Jede Etage hat 2 Helix-Flügel, einen Mittelverbinder und einen Vielzahn-Plug. Stapele so viele Etagen wie du möchtest!

---

## Benötigte Teile (pro Etage)

- [ ] 2× Helix-Flügel (TWR-LEAF-01)
- [ ] 1× Mittelverbinder Skelett (TWR-CONN-01)
- [ ] 1× Vielzahn-Plug (TWR-PLUG-01)
- [ ] 4× M3 Einschmelzmutter (F-M3-HI)
- [ ] 4× M3×8 Madenschraube (F-M3x8-MDS)

### Zusätzlich für den kompletten Turm
- [ ] 1× Vierkant-Achse 10×10mm, Länge je nach Etagenanzahl (A-SQ10)

---

## Schritt 1: Flügel drucken

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PETG |
| Schichthöhe | 0.2mm |
| Füllung | 15% |
| Wände | 3 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Stehend (Höhe = Z-Achse) |

### Durchführung
1. Lade `exports/middel-verbinder/Coreless_Helix_Fluegel.stl` in deinen Slicer
2. Platziere den Flügel stehend auf dem Druckbett
3. **Kein Support nötig!** Die Helix-Form ist selbsttragend
4. Drucke 2 Stück pro Etage

> 💡 **TIPP**: Beide Flügel können gleichzeitig auf dem Druckbett gedruckt werden (sie sind identisch, die 180°-Drehung erfolgt bei der Montage).

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
3. Hoher Infill (40%) für strukturelle Festigkeit!

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

1. **Flügel einstecken**: Beide Flügel um 180° versetzt in die unteren Rillen des Verbinders stecken
2. **Plug einsetzen**: Vielzahn-Plug in das zentrale Loch des Verbinders drücken
3. **Achse durchschieben**: Vierkant-Achse durch Plug und Verbinder führen
4. **Madenschrauben anziehen**: 4× M3×8 Madenschrauben im Kragen festziehen

> 💡 **TIPP**: Die 12-Zahn Vielzahn-Kupplung erlaubt 30°-Rastungen. Nutze das für die Helix-Verdrehung zwischen den Etagen!

---

## Schritt 5: Etagen stapeln

1. Nächste Etage von oben aufsetzen
2. Flügel der oberen Etage in die **oberen** Rillen des unteren Verbinders stecken
3. Verbinder der oberen Etage von oben aufsetzen
4. Plug einsetzen und verschrauben
5. Wiederholen bis gewünschte Höhe erreicht

> 💡 **TIPP**: Empfohlen sind 3–5 Etagen für eine gute Windausbeute bei handlicher Größe.

---

## ✅ Fertig!

Dein Turm sollte jetzt frei auf der Achse rotieren. Teste den Lauf von Hand — er sollte smooth und ohne Unwucht drehen.

**Weiter mit**: [⚡ Generator-Bauanleitung](02_generator.md)
