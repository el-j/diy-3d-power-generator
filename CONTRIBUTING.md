# Contributing to WindPower-3D

Danke, dass du zum Projekt beitragen möchtest! 🌬️

## Wie du beitragen kannst

### 🐛 Bug melden
1. Prüfe ob der Bug schon gemeldet wurde (Issues)
2. Erstelle ein neues Issue mit:
   - Betroffenes Bauteil (BOM-ID)
   - FreeCAD-Version
   - Fehlerbeschreibung + Screenshots

### 🔧 Bauteil verbessern
1. Fork das Repository
2. Erstelle einen Branch: `feat/improve-<component-id>`
3. Ändere die `component.json` UND das FreeCAD-Script
4. Aktualisiere die BOM (`docs/bom/master_bom.md`)
5. Aktualisiere die Bauanleitung falls nötig
6. Pull Request erstellen

### 📐 Neues Bauteil hinzufügen
Folge dem Design-Pipeline Workflow:

1. **component.json** erstellen (Parameter, Toleranzen, Kaufteile)
2. **3-Ansichten-Zeichnungen** erstellen (front.svg, side.svg, top.svg)
3. **FreeCAD-Script** schreiben (shared/freecad_utils.py nutzen!)
4. **BOM** aktualisieren
5. **Bauanleitung** ergänzen

### 🤖 Agent verbessern
Agenten-Dateien liegen in `.agents/identities/`. Du kannst:
- Neue Learnings ergänzen
- Regeln verfeinern
- Neue Agenten vorschlagen

## Code-Konventionen

### FreeCAD Scripts
- Parameter aus `shared/parameters.json` laden
- `shared/freecad_utils.py` für gemeinsame Funktionen
- Docstrings: Purpose, Usage, Rationale, Feature
- `removeSplitter()` nach Boolean-Ketten

### Commit-Format
```
[type](<bom-id>): <Beschreibung>

Beispiele:
feat(GEN-ROT-01): Add 20-pole magnet variant
fix(TWR-PLUG-01): Correct spline tolerance
docs(BOM): Update magnet quantities for 20-pole
```

Types: `feat`, `fix`, `refactor`, `docs`, `bom`, `guide`

## Lizenz

Mit deinem Beitrag stimmst du zu, dass er unter der gleichen Lizenz wie das Projekt veröffentlicht wird.
