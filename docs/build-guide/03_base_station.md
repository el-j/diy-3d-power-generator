# 🏗️ Bauanleitung: XXL Basis-Station v3.0 (68mm)

> Extrem flache 68mm Basis, Ø220mm. U-Form-Öffnung für Stator-Einschub, Führungslippe am Stacking-Deckel, abnehmbare Wartungsklappe mit PCB-Standoffs.
> Quelle: `src/base/helix_station.py`

---

## Benötigte Druckteile

| ID | STL-Datei (exports/xl_basis/) | Menge | Infill |
|----|-------------------------------|:-----:|:------:|
| XL-HOUS-01  | Basis_Gehaeuse_XXL              | 1 | 25% |
| XL-DECK-01  | Stacking_Lager_Deckel_FLACH     | 1 | 40% |
| XL-FLNSH-01 | Wand_Flansch                    | 3 | 50% |
| XL-KLAP-01  | Elektronik_Wartungs_Klappe      | 1 | 20% |
| XL-BODEN-01 | Wartungsklappen_Boden           | 1 | 30% |

## Benötigte Kaufteile

- [ ] 1× Kegelrollenlager **29×50×15mm** (REAL GEMESSEN — kein Datenblatt!)
- [ ] 24× M3 Einschmelzmutter Ø4.2×5mm
- [ ] 6× M3×16 Senkkopfschraube (Wand-Flansch → Gehäuse)
- [ ] 6× M6×30 Senkkopfschraube (Flansch → Wand)
- [ ] 4× M3×12 Zylinderkopfschraube (Klappen-Boden)

---

## Schritt 1: Einschmelzmuttern ins Gehäuse

Das Gehäuse hat drei Flansch-Pads (rechts, links, hinten) und Deckel-Bohrungen.

### Flansch-Pads (je 4× pro Pad = 12×)
- 4× an jedem der 3 Pads bei Z=15mm und Z=53mm
- Einschmelzen von der geraden Außenfläche (bei X=±121.5mm bzw. Y=121.5mm)

### Deckel-Verschraubung (R=104mm, 15° versetzt, 12 Bohrungen)
- **Gerade Positionen** (i=0,2,4…): Insert sitzt bei Z=63–68mm (oben), gehört zum Gehäuse → **6× einschmelzen**
- **Ungerade Positionen** (i=1,3,5…): Insert sitzt bei Z=0–5mm (unten), gehört zum Gehäuse → **6× einschmelzen**

> 💡 Insgesamt ~24 Einschmelzmuttern im Gehäuse. Lötkolben 250°C, langsam und gerade eindrücken.

---

## Schritt 2: Kegelrollenlager einpressen

1. **Stacking-Deckel** (XL-DECK-01) flach auf Tisch legen — Lagertasche zeigt nach oben
2. Lagertasche ist **50.2mm** (= Lager 50mm + 0.2mm Toleranz)
3. Lager mit gleichmäßigem Druck einpressen — ggf. mit einer Schraubzwinge oder Presse
4. Lager muss **bündig** mit der oberen Fläche sitzen

> ⚠️ Nie auf den Innenring hämmern — nur auf den Außenring drücken!

---

## Schritt 3: Stator-Schlitten einfahren

Das Gehäuse hat eine **U-Form-Öffnung** (213mm breit) und einen **Stator-Schlitz** bei Z=25.8–34.2mm.

1. Stator-Schlitten (XLG-STAT-01) von vorne durch die Öffnung einschieben
2. In den Schlitz einfädeln — der Stator läuft auf R=99mm, der Schlitz ist 99.5mm Radius
3. Stator schiebt sich bis zur Mitte und rastet in der richtigen Position

> 💡 Der Stator-Schlitz ist 8.4mm hoch (Stator 9mm − 0.6mm Spiel). Er sitzt bündig bei Ø198mm.

---

## Schritt 4: Stacking-Deckel aufsetzen

1. Stacking-Deckel von oben auf das Gehäuse aufsetzen
2. Die **Führungslippe** (R96–110mm, 4mm hoch) zentriert den Deckel automatisch am Gehäuse-Innenrand
3. Der **Führungsring** (R85–95.5mm, 6mm tief) greift in den Stator-Radius ein
4. 12× M3×16 Senkkopfschrauben durch die Deckel-Bohrungen (R=104mm) in die Einschmelzmuttern des Gehäuses

---

## Schritt 5: Wand-Flansche montieren

Die Flansche (XL-FLNSH-01) verbinden die Basis mit der Wand/Träger.

1. 3× Wand-Flansch auf die 3 Pads aufsetzen (rechts, links, hinten)
2. Je 4× M3×16 Senkkopf durch den senkrechten Flansch-Steg in die Pad-Einschmelzmuttern
3. Je 2× M6×30 durch die waagerechten Löcher in die Wand/Träger

> 💡 Die Dreiecks-Rippen am Flansch tragen Last — Montage ohne diese Seite führt zu Bruch!

---

## Schritt 6: Elektronik-Wartungsklappe

Die Klappe schließt die U-Form-Öffnung vorne und enthält die Elektronik.

1. **PCB-Standoffs**: 4× innen an der Rückwand (±25mm, Z=20mm + 50mm)
2. Gleichrichter, Laderegler und Anschlussklemmen auf den Standoffs befestigen
3. Kabel durch die **Kabeldurchführung** (Ø10mm, Z=10mm) führen
4. Klappe in die Öffnung einschieben und mit 1× M3×16 pro Seite (Z=34mm) verriegeln
5. **Klappen-Boden** (XL-BODEN-01) von unten aufsetzen und mit 4× M3×12 an den Tabs verschrauben

---

## Schritt 7: Generator einsetzen

1. Lager-Reduzierung Unten (XLG-REDUZ-01) in den Innenring des Kegelrollenlagers einpressen
   - Schaft Ø29.15mm (= Lager-Innen 29mm + 0.15mm Pressfit)
   - Fase ermöglicht leichtes Einfädeln
2. Vielzahn-Achse von oben einführen, alle Generator-Komponenten von oben aufstecken
3. Von unten: Clamp Lager Unten aufschrauben (fixiert Position)

---

## ✅ Fertig!

**Weiter mit**: [🔩 Endmontage](04_final_assembly.md)
