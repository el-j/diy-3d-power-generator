# 🗼 Bauanleitung: Darrieus H-Rotor

> Der Darrieus H-Rotor erzeugt seinen Antrieb ausschließlich über aerodynamischen Auftrieb — wie ein Flugzeugflügel, das sich dreht. Er startet nicht selbst, erreicht aber mit TSR 3–4 die höchsten Wirkungsgrade aller fünf Rotorprinzipien in diesem Projekt.

---

## Benötigte Teile

- [ ] 3× Tragflügel-Blatt (TWR-DAR-01)
- [ ] 1× Naben-Ring (TWR-DAR-HUB)
- [ ] 1× Deckscheibe oben (TWR-DAR-DISC-TOP)
- [ ] 1× Bodenplatte mit Vielzahn-Loch (TWR-DAR-DISC-BOT)
- [ ] 1× Vielzahn-Plug (TWR-PLUG-01)
- [ ] 6× M3 Einschmelzmutter (F-M3-HI)
- [ ] 6× M3×8 Madenschraube (F-M3x8-MDS)

### Zusätzlich für den kompletten Turm
- [ ] 1× Vierkant-Achse 10×10mm, Länge je nach Etagenanzahl (A-SQ10)

---

## Schritt 1: Tragflügel drucken

### Profil-Geometrie
| Parameter | Wert |
|-----------|------|
| Profiltyp | NACA-ähnlich, symmetrisch |
| Gesamttiefe (Chord) | 20 mm |
| Dicke | 4 mm |
| Nase | Halbzylinder Ø4mm |
| Heck | Halbzylinder Ø2.2mm bei Chord−1.8mm |
| Körper | 15.4×4mm Box, 1.2mm versetzt |
| Blattlänge | 240 mm |

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PLA-CF |
| Schichthöhe | **0.1mm** (!!) |
| Füllung Streben | 100% |
| Füllung Blattkörper | 40% |
| Wände | 4 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Stehend (Länge = Z-Achse) |

### Durchführung
1. Lade `exports/generator/darrieus_h/TWR-DAR-01.stl` in deinen Slicer
2. Blatt stehend auf dem Druckbett platzieren — Längsachse zeigt nach oben
3. **Kein Support nötig!** Das Profil ist bei stehender Ausrichtung selbsttragend
4. Schichthöhe auf **0.1mm** einstellen — kein Kompromiss!
5. Drucke 3 Stück

> ⚠️ **ACHTUNG**: Die 0.1mm Schichthöhe ist zwingend. Gröbere Schichten zerstören die aerodynamische Genauigkeit des Profils und reduzieren den Wirkungsgrad spürbar.

> ⚠️ **ACHTUNG**: Die horizontalen Streben müssen mit **100% Infill** gedruckt werden — sie tragen die vollen Biegekräfte aus der Zentrifugalkraft bei Betriebsdrehzahl.

> 💡 **TIPP**: Alle drei Blätter passen gleichzeitig auf ein 256×256mm Druckbett. Prüfe die Ausrichtung im Slicer sorgfältig vor dem Start.

---

## Schritt 2: Naben-Ring drucken

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PLA-CF |
| Schichthöhe | 0.2mm |
| Füllung | 100% |
| Wände | 4 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Flach (Ring-Ebene = XY) |

### Durchführung
1. Lade `exports/generator/darrieus_h/TWR-DAR-HUB.stl`
2. Flach auf dem Druckbett platzieren
3. 100% Infill für maximale Knotenfestigkeit an den Streben-Ansätzen
4. Naben-Radius beträgt 12mm — Mittelloch auf korrekte Achse prüfen

---

## Schritt 3: Deckscheiben drucken

### Druckeinstellungen (für beide Scheiben identisch)
| Parameter | Wert |
|-----------|------|
| Material | PLA-CF |
| Schichthöhe | 0.2mm |
| Füllung | 100% |
| Wände | 4 |
| Stützstruktur | ❌ Nein |
| Ausrichtung | Flach (Scheibenebene = XY) |

### Durchführung
1. Lade `exports/generator/darrieus_h/TWR-DAR-DISC-TOP.stl` und `TWR-DAR-DISC-BOT.stl`
2. Beide Scheiben flach drucken
3. Die **Bodenplatte** (TWR-DAR-DISC-BOT) hat das Vielzahn-Loch (12 Zähne, R9.0/R7.8) — Ausrichtung vor dem Druck prüfen!

---

## Schritt 4: Vielzahn-Plug drucken + bestücken

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PLA-CF |
| Füllung | 60% |
| Wände | 4 |

### Einschmelzmuttern einsetzen
1. Lötkolben auf **250°C** vorheizen
2. Einschmelzmutter mit der Lötkolben-Spitze aufnehmen
3. Langsam und gerade in die Taschen des Plugs eindrücken
4. Bündig mit der Oberfläche abschließen lassen

> ⚠️ **ACHTUNG**: Die Muttern werden heiß! Nicht mit Fingern berühren. Lötkolben-Spitze nach dem Einsetzen sofort entfernen, nicht nachdrücken.

---

## Schritt 5: Zusammenbau

1. **Bodenplatte positionieren**: TWR-DAR-DISC-BOT flach auf die Arbeitsfläche legen, Vielzahn-Loch nach oben
2. **Blätter einsetzen**: Alle drei Blätter (TWR-DAR-01) im 120°-Abstand an den Streben-Endpunkten des Naben-Rings einhängen — Nabenradius R=12mm
3. **Naben-Ring zentrieren**: TWR-DAR-HUB über die drei Blatt-Ansätze schieben und ausrichten
4. **Streben-Positionen prüfen**: Untere Streben bei 15% der Blattlänge (36mm), obere bei 85% (204mm) — beides vom Blattfuß gemessen
5. **Deckscheibe aufsetzen**: TWR-DAR-DISC-TOP auf die Oberkante der Blätter aufsetzen und bündig ausrichten
6. **Plug einsetzen**: TWR-PLUG-01 in das Vielzahn-Loch der Bodenplatte drücken
7. **Achse durchschieben**: Vierkant-Achse durch Plug und Bodenplatte führen
8. **Madenschrauben anziehen**: 6× M3×8 Madenschrauben festziehen

> 💡 **TIPP**: Die 12-Zahn Vielzahn-Kupplung erlaubt 30°-Rastungen. Nutze das, um den Darrieus-Rotor optimal zur Helix-Etage darunter zu versetzt zu montieren.

---

## Schritt 6: Anlaufverhalten verstehen

> 💡 **TIPP**: Der Darrieus H-Rotor startet **nicht selbst**. Er benötigt einen kurzen Anschubs per Hand oder kurzen Motor-Impuls bei schwachem Wind. Sobald er über TSR = 1 beschleunigt hat, übernimmt der aerodynamische Auftrieb vollständig — ab da läuft er sehr effizient.

| Betriebspunkt | Wert |
|---------------|------|
| Selbststart | ❌ Nein |
| Optimale TSR | 3–4 |
| Anlaufhilfe | Kurzer Handanstoß oder Motor-Impuls |
| Wirkungsgrad-Peak | Höchster aller 5 Rotorprinzipien |

---

## Quellskript

```
src/leaf/darrieus_h_leaf.py
```

---

## ✅ Fertig!

Der Darrieus H-Rotor sollte sich jetzt leichtgängig von Hand drehen lassen. Gib ihm einen Schwung — er sollte mehrere Umdrehungen aus dem Impuls freilaufen. Wenn er sofort abbremst, Lagerreibung und Achspassung prüfen.

**Weiter mit**: [🌀 Gorlov Helical Rotor](tower-gorlov.md)
