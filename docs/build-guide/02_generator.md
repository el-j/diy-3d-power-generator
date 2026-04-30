# ⚡ Bauanleitung: XXL Axialfluss-Generator (v2.1)

> Sandwich-Bauweise mit 2 Magnet-Rotoren (Ø180mm) und 12 ovalen Capsule-Spulen im Stator (20-Pol).
> Quelle: `src/bigBasis/big_base_generator.py`
>
> Die kleine 10/20-Pol Variante (smalBasis) ist **LEGACY** — baue nur noch den XXL Generator.

---

## Benötigte Druckteile

| ID | Bauteil | Menge | Infill |
|----|---------|:-----:|:------:|
| XLG-ROT-01 | XXL Rotor Oben (Ø180mm) | 1 | 30% |
| XLG-ROT-02 | XXL Rotor Unten (Ø180mm) | 1 | 30% |
| XLG-BP-01 | XXL Backplate Oben | 1 | 25% |
| XLG-BP-02 | XXL Backplate Unten | 1 | 25% |
| XLG-STAT-01 | XXL Stator-Schlitten (Ø198mm) | 1 | 25% |
| XLG-STAT-02 | XXL Stator-Deckel | 1 | 20% |
| XLG-PLUG-01 | Magnet-Spacer Klötzchen | 20 | 100% |
| XLG-SPACER-01 | Abstands-Hülse Rotoren (Ø20×10mm) | 2 | 100% |
| XLG-SPACER-02 | Abstands-Hülse Lager (Ø28×7mm) | 1 | 100% |

## Benötigte Kaufteile

- [ ] 10× M3 Einschmelzmutter (Ø4.2×5mm, Messing)
- [ ] 5× M5×20 Senkkopfschraube (Rotor-Backplate)
- [ ] 4× M3×12 Zylinderkopfschraube (Stator-Deckel)
- [ ] 20× Neodym-Magnet **20×5×3mm N52** (pro Rotor — gesamt: 40 Stk.)
- [ ] ~100m Kupferlackdraht Ø0.5mm

---

## Schritt 1: Einschmelzmuttern einsetzen

1. Je 5× Einschmelzmuttern in **Rotor Oben** (Taschen auf Oberseite, R=50mm, 72° Abstand)
2. Je 5× Einschmelzmuttern in **Rotor Unten** (Taschen auf Unterseite)

> 💡 Lötkolben auf ~250°C, Mutter langsam eindrücken bis bündig.

---

## Schritt 2: Magnete einsetzen

> ⚠️ **KRITISCH: Polarität beachten!**
> - Alternierende N/S Bestückung — jeder 2. Magnet umgedreht
> - Die beiden Rotoren müssen sich **anziehen** (N-Seite zu S-Seite durch den Stator)
> - Test: Rotor Oben und Unten gegenüberhalten → sie ziehen sich an

1. **Magneten markieren**: Alle N-Pole mit Edding markieren, bevor du anfängst
2. Je 20 Magnete abwechselnd N/S in die Taschen (Länge radial ausgerichtet, 20×5×3mm)
3. **Magnet-Spacer** (XLG-PLUG-01) über jeden Magneten setzen — hält Magnete höhenbündig

> 💡 20 Spacer (Einzelteile) — einer pro Magnet. Kein Kleber nötig, Presspassung.

---

## Schritt 3: Backplates montieren

1. **Backplate Oben** (XLG-BP-01) auf Rotor Oben setzen
2. 5× M5×20 Senkkopfschrauben durch die Backplate → Rotor → Einschmelzmuttern anziehen
3. Wiederholen für **Backplate Unten** (XLG-BP-02) + Rotor Unten

> ⚠️ **v2.1**: Die Backplates haben **keine** eingebauten Magnet-Plugs mehr — XLG-PLUG-01 übernimmt diese Funktion als Einzelteil.

---

## Schritt 4: Spulen wickeln (12 Stück)

### Wickeldaten (Capsule-Spulen)

| Parameter | Wert |
|-----------|------|
| Spulenform | Oval / Capsule |
| Außenmaß | 40×26mm |
| Innenmaß (Kern) | 22×8mm |
| Taschen-Tiefe | 6mm |
| Draht | Kupferlackdraht Ø0.5mm |
| Windungen | ~120–150 pro Spule |

> 💡 Verwende den **Komplex-Spooler** (Traversier-Wickelmaschine) für gleichmäßige Lagen.
> Alternativ: **Easy-Tool** mit Akkuschrauber. Siehe [🛠️ Werkzeuge](05_tools.md).

1. 12× Capsule-Spulen wickeln (Kern entspricht dem Innenmaß der Taschen)
2. Enden ca. 15cm lang lassen für die Verdrahtung
3. Spule mit dünnem Klebeband oder Sekundenkleber fixieren

---

## Schritt 5: Stator bestücken und verdrahten

1. 12 Spulen in die ovalen Taschen des **Stator-Schlittens** (XLG-STAT-01) einsetzen
   - Taschen auf R=74mm, gleichmäßig 30° Abstand
2. **3-Phasen Stern-Schaltung** verdrahten:
   - Phase A: Spulen 1, 4, 7, 10
   - Phase B: Spulen 2, 5, 8, 11
   - Phase C: Spulen 3, 6, 9, 12
3. Kabel durch den **Ring-Kanal** (R82–88mm, 3.5mm tief) und **Griff-Kanal** nach außen führen
4. **Stator-Deckel** (XLG-STAT-02) aufsetzen — Mittelloch Ø32mm (R=16mm) passt über die Achse
5. 4× M3×12 durch die Deckel-Löcher (R=94mm, 45° versetzt) verschrauben

> ⚠️ **v2.1**: Stator-Deckel hat korrektes Mittelloch R=16mm (Ø32mm). Ältere Drucke mit R=9mm passen nicht!

---

## Schritt 6: Abstands-Hülsen auf Achse montieren

| Bauteil | Position | Funktion |
|---------|----------|----------|
| XLG-SPACER-01 (Ø20×10mm) | 2× zwischen Rotor und Stator | Luftspalt sichern |
| XLG-SPACER-02 (Ø28×7mm) | 1× unten, auf Basisstation | Auflage auf 29mm Zentrierung |

1. **Spacer-02** ganz unten auf die Basisstation-Lagerzentrierung (Ø29mm innen) setzen
2. **Spacer-01** (2×) je zwischen Rotor und Stator auf die Vierkant-Achse schieben

---

## Schritt 7: Endmontage & Funktionstest

Reihenfolge auf der Achse (von unten nach oben):
```
Basisstation → Spacer-02 → Rotor Unten → Spacer-01 → Stator → Spacer-01 → Rotor Oben
```

1. Von Hand drehen → muss leichtgängig sein, kein Schleifen
2. **Multimeter** an die 3 Phasen-Ausgänge
3. Bei flotter Handdrehung sollten **>2V AC** messbar sein

> ⚠️ **Falls <1V**: Magnetpolarität prüfen (Rotor Oben und Unten müssen sich **anziehen**) oder Spulen-Verschaltung kontrollieren.

---

## ✅ Fertig!

**Weiter mit**: [🏗️ XXL Basis-Station](03_base_station.md)
