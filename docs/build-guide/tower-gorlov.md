# 🌀 Bauanleitung: Gorlov Helical-Turm

> Der Gorlov-Rotor ist die eleganteste Lösung: die gleiche Auftriebsgeometrie wie der Darrieus, aber mit 120° Helixdrall über die Höhe — dadurch startet er selbst, läuft ohne Drehmomentschwankungen und erreicht ~32% Wirkungsgrad.

**Aerodynamisches Prinzip**: Lift-Drag-Hybrid | **TSR**: 2,0–3,0 | **Cp**: ~32% | **Selbstanlaufend**: ✅ Ja

---

## Benötigte Teile (pro Etage)

- [ ] 3× Gorlov Helical Blade (TWR-GOR-01)
- [ ] 1× Gorlov Connector Ring (TWR-GOR-RING)
- [ ] 1× Vielzahn-Plug (TWR-PLUG-01)
- [ ] 4× M3 Einschmelzmutter (F-M3-HI)
- [ ] 4× M3×8 Madenschraube (F-M3x8-MDS)

### Zusätzlich für den kompletten Turm
- [ ] 1× Vierkant-Achse 10×10mm, Länge je nach Etagenanzahl (A-SQ10)

**Quellcode**: `src/leaf/gorlov_leaf.py`

---

## Schritt 1: Gorlov-Flügel drucken

### Flügelprofil
Das Gorlov-Blatt ist ein **bikonvexes, symmetrisches Tragflächenprofil** mit 120° Helixdrall über 240mm Höhe:
- Profil: Oberer Bogen (−8mm, 0) über (0, +1,7mm) bis (8mm, 0); unterer Bogen gespiegelt
- Sehne: 16mm | Dicke: 3,4mm | 48 Loft-Schritte

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | **CF-Nylon oder PLA-CF** |
| Schichthöhe | **0,15mm** (Pflicht für Profilgenauigkeit!) |
| Füllung | 40% |
| Wände | 4 |
| Stützstruktur | ❌ Nein — Helixform ist selbsttragend |
| Ausrichtung | Stehend (Höhe = Z-Achse) |

### Durchführung
1. Lade `exports/gorlov/Gorlov_Blade.stl` in deinen Slicer
2. Flügel stehend platzieren — die 120° Helix ist entlang der Z-Achse
3. **Kein Support nötig**: Die kontinuierliche Helixgeometrie trägt sich selbst
4. Drucke 3 Stück pro Etage
5. Am Blatt-Ring-Übergang Wände auf 5+ erhöhen (höchste Belastungszone)

> 💡 **TIPP**: 0,15mm Schichthöhe ist bei diesem Profil kein Luxus — die 3,4mm dicke Profilkante ist bei 0,3mm Schichten nicht mehr aerodynamisch korrekt. Das CF-Nylon kompensiert den Mehraufwand mit überlegener Festigkeit unter Schubbelastung.

> ⚠️ **ACHTUNG**: Die Blatt-Ring-Verbindung trägt den vollen Biegeanteil der Zentrifugalkraft bei Drehzahl. Prüfe nach dem Druck auf Delaminierung an dieser Stelle. Schwacher Verbund = Blattversagen bei Sturm.

---

## Schritt 2: Connector Ring drucken

Der Connector Ring schließt oben und unten die 3 Gorlov-Blätter zusammen und überträgt die Kraft auf den Vielzahn-Plug.

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PLA-CF |
| Schichthöhe | 0,2mm |
| Füllung | 60% |
| Wände | 5 |
| Ausrichtung | Flach (Ring-Ebene = XY) |

### Abmessungen Ring
- Außenradius: 72mm | Innenbohrung: 13mm (Naben-Freistich)
- Vielzahn-Splineaufnahme am Bodenring: 12 Zähne, R9,0/R7,8, +0,2mm Spiel

### Durchführung
1. Lade `exports/gorlov/Gorlov_ConnectorRing.stl`
2. Ring flach auf dem Bett platzieren
3. Drucke 2 Stück pro Etage (oben + unten)
4. Überprüfe die Blattaufnahme-Slots auf scharfe Kanten — bei Bedarf mit 400er Schleifpapier entgraten

---

## Schritt 3: Vielzahn-Plug drucken + bestücken

Identisch mit allen anderen Rotortypen — das Vielzahn-Interface ist einheitlich.

### Druckeinstellungen
| Parameter | Wert |
|-----------|------|
| Material | PETG oder PLA-CF |
| Füllung | 60% |
| Wände | 4 |

### Einschmelzmuttern einsetzen
1. Lötkolben auf **250°C** vorheizen
2. 4× M3 Einschmelzmutter aufnehmen
3. Langsam und gerade in die Kragen-Taschen eindrücken
4. Bündig mit der Oberfläche abschließen lassen

> ⚠️ **ACHTUNG**: Nicht nachdrücken sobald die Mutter sitzt — das verdrängt Schmelzgrat in das Gewinde.

---

## Schritt 4: Zusammenbau einer Etage

1. **Bodenring einlegen**: Unteren Connector Ring auf die Arbeitsflä­che legen, Vielzahn-Seite nach unten
2. **Flügel einsetzen**: Alle 3 Gorlov-Flügel gleichzeitig in die Ring-Slots führen — exakt 120° versetzt
3. **Topring aufsetzen**: Oberen Connector Ring auf die Blattenden drücken und in die Slots rasten
4. **Plug einsetzen**: Vielzahn-Plug durch Bodenring und Achsloch des oberen Rings führen
5. **Achse durchschieben**: Vierkant-Achse durch Plug und alle Ringe schieben
6. **Madenschrauben anziehen**: 4× M3×8 im Kragen festziehen

> 💡 **TIPP**: Die Blätter können beim gleichzeitigen Einsetzen aller 3 leicht verklemmen. Starte von oben: oberen Ring leicht geneigt aufsetzen, ersten Flügel rasten, dann 120° weiterdrehen für den zweiten, nochmals 120° für den dritten. Dann Bodenring aufdrücken.

---

## Schritt 5: Etagen stapeln

1. Fertige Etage auf die Achse schieben
2. Nächste Etage aufsetzen — der Connector Ring der oberen Etage sitzt direkt auf dem der unteren
3. Plug der oberen Etage einsetzen und verschrauben
4. Wiederholen bis zur gewünschten Turmhöhe

> 💡 **TIPP**: Beim Gorlov-Rotor können die Etagen alle gleich ausgerichtet werden — der 120°-Drall jedes Blatts sorgt selbst dafür, dass sich zu jedem Zeitpunkt immer Blattabschnitte in günstiger Auftriebsposition befinden. Kein Versatz zwischen den Etagen nötig (anders als beim Darrieus H).

> 💡 **TIPP**: 3–4 Etagen sind ideal. Die Gorlov-Geometrie entfaltet ihren Vorteil (kein Drehmomentruckeln) besonders bei 3+ Etagen mit versetzter Blattphase.

---

## Vergleich mit anderen Rotortypen

| Eigenschaft | Gorlov (dieses Blatt) | Darrieus H | Helix Savonius |
|---|---|---|---|
| Wirkungsgrad Cp | **~32%** | ~28% | ~18% |
| Selbstanlaufend | ✅ Ja | ❌ Nein | ✅ Ja |
| Drehmomentrippel | **Keiner** | Hoch | Mittel |
| Druckschwierigkeit | Mittel-Hoch | Hoch | Einfach |
| Windbereich | Konstant/stark | Konstant | Böig/schwach |

---

## ✅ Fertig!

Dein Gorlov-Turm ist fertig. Teste die Rotation von Hand — er sollte extrem smooth laufen, ohne spürbare Drehmomentschwankungen. Wenn du ein leichtes "Anhalten und Weiterlaufen" bei einer Position spürst, ist ein Blatt falsch ausgerichtet oder der Ring klemmt.

**Weiter mit**: [⚡ Generator-Bauanleitung](02_generator.md)
