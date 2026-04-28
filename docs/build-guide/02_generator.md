# ⚡ Bauanleitung: Axialfluss-Generator

> Sandwich-Bauweise mit 2 Magnet-Rotoren und einem Spulen-Stator. Verfügbar als 10-Pol und 20-Pol Variante.

---

## Benötigte Teile (10-Pol Variante)

### Druckteile
- [ ] 1× Rotor Oben (GEN-ROT-01)
- [ ] 1× Rotor Unten (GEN-ROT-02)
- [ ] 1× Backplate Oben (GEN-BP-01)
- [ ] 1× Backplate Unten (GEN-BP-02)
- [ ] 1× Stator-Schlitten (GEN-STAT-01)
- [ ] 1× Stator-Deckel (GEN-STAT-02)

### Kaufteile
- [ ] 10× M3 Einschmelzmutter (F-M3-HI)
- [ ] 10× M3×16 Senkkopfschraube (F-M3x16-SK)
- [ ] 20× Neodym-Magnet 20×5×3mm N52 (MAG-20x5x3)
- [ ] ~50m Kupferlackdraht Ø0.5mm
- [ ] 4× M3×12 Zylinderkopfschraube (F-M3x12)

---

## Schritt 1: Rotoren bestücken

### 1a. Einschmelzmuttern einsetzen
1. Je 5× Einschmelzmuttern in **Rotor Oben** (Taschen auf der Oberseite)
2. Je 5× Einschmelzmuttern in **Rotor Unten** (Taschen auf der Unterseite)

### 1b. Magnete einsetzen

> ⚠️ **KRITISCH: Polarität beachten!**
> - Dreiecks-Markierungen zeigen zum Zentrum → dort kommt der **N-Pol** hin
> - Gegenüberliegende Rotoren müssen **sich anziehen** (N↔S)
> - Teste mit einem einzelnen Magneten durch den Stator hindurch!

1. Magnete einzeln in die Taschen einsetzen (Gleitpassung, kein Kleber nötig)
2. **Alternierend** N/S einsetzen (jeder 2. Magnet hat Dreieck!)
3. Am Schluss: Rotor Oben und Unten gegenüberhalten → sie sollten sich **anziehen**

> 💡 **TIPP**: Markiere die Magnete vor dem Einsetzen mit einem Edding auf der N-Seite.

---

## Schritt 2: Backplates montieren

1. Backplate Oben auf Rotor Oben setzen (Stempel greifen in die Magnettaschen)
2. 5× M3×16 Senkkopfschrauben durch die Backplate → Rotor → Einschmelzmuttern
3. Wiederholen für Backplate Unten + Rotor Unten

> 💡 **TIPP**: Die Stempel in der Backplate halten die Magnete sicher in Position.

---

## Schritt 3: Spulen wickeln (12 Stück)

### Wickeldaten
| Parameter | Wert |
|-----------|------|
| Draht | Kupferlackdraht Ø0.5mm |
| Windungen | ~80 pro Spule |
| Kern-Ø | 7mm (Spulen-Kern) |
| Außen-Ø | max. 14mm |
| Dicke | max. 3.5mm |

1. Verwende den Spulen-Wickler (TOOL-WIND-01) oder einen Bohrer als Kern
2. 80 Windungen sauber nebeneinander wickeln
3. Enden ca. 10cm lang lassen
4. Spule mit Sekundenkleber fixieren

> 💡 **TIPP**: Die Spulen-Wickler Vorlage aus dem Werkzeuge-Set nutzen!

---

## Schritt 4: Stator bestücken und verdrahten

1. 12 Spulen in die konischen Löcher des Stator-Schlittens einsetzen
2. **3-Phasen Stern-Schaltung** verdrahten:
   - Phase A: Spulen 1, 4, 7, 10
   - Phase B: Spulen 2, 5, 8, 11
   - Phase C: Spulen 3, 6, 9, 12
3. Kabel durch den Kabelkanal-Ring und den Griff-Kanal führen
4. Stator-Deckel aufsetzen und mit 4× M3×12 verschrauben

---

## Schritt 5: Funktionstest

1. Beide Rotoren auf die Achse schieben (Stator dazwischen)
2. Von Hand drehen → Multimeter an die 3 Phasen-Ausgänge
3. Bei flotter Handdrehung sollten **>1V AC** messbar sein

> ⚠️ **Falls <0.5V**: Polarität der Magnete oder Spulen-Verschaltung prüfen!

---

## ✅ Fertig!

**Weiter mit**: [🏗️ Basis-Station](03_base_station.md)
