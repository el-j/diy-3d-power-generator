# 🔧 Bauanleitung: Werkzeuge

> Hier findest du die Anleitungen für die Wickel-Werkzeuge. Wähle dein Level!

---

## 🎯 Übersicht — Welches Werkzeug brauchst du?

| Level | Werkzeug | Beschreibung | Teile |
|:-----:|----------|-------------|:-----:|
| ⭐ | [Easy-Tool](#-easy-tool) | Akkuschrauber-Aufsatz | 2 |
| ⭐⭐ | [First Spooler](#-first-spooler) | Handkurbel mit Zahnrad | 9 |
| ⭐⭐⭐ | [Komplex-Spooler](#-komplex-spooler) | Traversier-Wickelmaschine | 15+ |
| 🧲 | [Magnet-Puffer](#-magnet-puffer) | Drahtspanner | 3 |

> 💡 **Empfehlung**: Der **Easy-Tool** reicht für die ersten Spulen. Für Serien-Produktion (viele Spulen) nimm den **Komplex-Spooler** + **Magnet-Puffer**.

---

## ⭐ Easy-Tool

Der simpelste Weg: Ein Aufsatz für den Akkuschrauber, der direkt in den Bit-Halter gesteckt wird.

### Teile
- 1× Winder Basis Bit (passt in Standard-Bit-Aufnahme)
- 1× Winder Deckel Kern (klemmt den Spulenkern)

### Drucken
| Parameter | Wert |
|-----------|------|
| Material | PLA oder PETG |
| Infill | 40% |
| Stützstruktur | Nein |

### Benutzung
1. Basis-Bit in den Akkuschrauber stecken
2. Kupferdraht einführen
3. Deckel aufsetzen
4. Langsam wickeln (niedrigste Stufe!)

> ⚠️ **ACHTUNG**: Nicht zu schnell drehen! Der Draht kann reißen.

---

## ⭐⭐⭐ Komplex-Spooler

Die professionelle Traversier-Wickelmaschine mit 4 Achsen und 1:24 Zahnrad-Untersetzung.

### Zahnrad-Kette
```
Kurbel (40Z) → Spule (10Z)          = 4:1
               × Zwischen (40Z→10Z) = 4:1 
               × Trommel (60Z)       = 1.5:1 (Traversierung)
               
Gesamt: 1 Umdrehung Kurbel = 4 Umdrehungen Spule
```

### Aufbau
1. **Basis Skeleton** drucken (Kompakte Bodenplatte mit Capsule-Aussparungen)
2. **8× Steck-Türme** drucken (4 Achsen × Vorne + Hinten)
3. **6× Zahnräder** drucken (40Z, 10Z, 60Z Varianten)
4. Achsen aus 8mm Hex-Stangen schneiden
5. Türme in Basis einstecken und verschrauben
6. Zahnräder auf die Achsen stecken
7. Trommel-Zahnrad für die Traversierung einrichten

---

## 🧲 Magnet-Puffer

Der magnetische Drahtspanner sorgt für konstante Spannung beim Wickeln.

### Prinzip
Ein Magnet-Schlitten gleitet auf einer T-Nut-Schiene. Neodym-Magnete im Schlitten werden von Magneten im Endblock angezogen → konstante Bremskraft!

### Teile
- 1× Basis mit Filz-Bremse + T-Nut Schiene
- 1× Endblock (schraubbar, 3 Magnetlöcher)
- 1× Magnet-Schlitten ("Pilz"-Form)
- 6× Neodym-Magnete Ø5×3mm
- 2× Filz-Pads
- 1× M3×20 Schraube + Mutter (Tensioner)

### Montage
1. Endblock auf Basis verschrauben
2. 3 Magnete in Endblock → 3 Magnete in Schlitten (ABSPREISSEND!)
3. Filz-Pads in den Tensioner-Schlitz
4. M3 Tensioner-Schraube eindrehen (reguliert Bremskraft)
5. Draht durch Basis → Filz → Führungspin → Wickelmaschine

> 💡 **TIPP**: Durch die 3 Stopper-Positionen in der Basis kannst du den Arbeitsweg des Schlittens einstellen.
