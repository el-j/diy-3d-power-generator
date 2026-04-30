# docs/ARCHITECTURE.md
# 🏗️ Architecture — WindPower-3D Design Bureau

## System Overview

This project uses an **AI-agent-orchestrated design pipeline** to manage the full lifecycle of 3D-printed components: from parametric design through technical drawings, FreeCAD code, BOM management, and build instructions.

### Design Patterns Used

| Pattern | Source | Application |
|---------|--------|-------------|
| Identity-driven agents | [agency-agents](https://github.com/msitarzewski/agency-agents) | Each agent has personality, mission, deliverables, learnings |
| Task pipeline | [claude-agent-blueprint](https://github.com/mongoistkeingemuese/claude-agent-blueprint) | Phased workflow with quality gates |
| Skill routing | claude-agent-blueprint | Domain specialists triggered by task type |
| State machine | claude-agent-blueprint | `state.json` tracks queue, active, history |
| Self-evolution | Both repos | Agents accumulate learnings over time |

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   🎛️ ORCHESTRATOR                          │
│  Reads: state.json    Writes: state.json                    │
│  Controls: Phase progression, retries, quality gates        │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────▼──────────┐
    │  P1: CAD Engineer   │ → component.json (params, tolerances)
    ├─────────▼──────────┤
    │  P2: Drawing Agent  │ → front.svg, side.svg, top.svg
    ├─────────▼──────────┤
    │  P3: FreeCAD Coder  │ → component.py, exports/*.stl
    ├─────────▼──────────┤
    │  P4: BOM Manager    │ → assembly_bom.md, master_bom.json
    ├─────────▼──────────┤
    │  P5: Build Guide    │ → build-guide/*.md
    ├─────────▼──────────┤
    │  P6: QA Inspector   │ → qa_report (PASS/NEEDS_WORK)
    └────────────────────┘
              │
         PASS ↓ FAIL → Route back to failing phase
```

## Data Flow

```
shared/parameters.json ──────────────┐
shared/materials.json ───────────────┤
shared/fasteners.json ───────────────┤
                                     ▼
                            ┌─────────────────┐
                            │  Component JSON  │
                            │  (per component) │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐   ┌────────────┐   ┌──────────┐
              │ Drawings  │   │ FreeCAD.py │   │   BOM    │
              │  (SVG)    │   │  + STL     │   │ (MD+JSON)│
              └──────────┘   └────────────┘   └──────────┘
```

## Directory Conventions

| Path | Purpose |
|------|---------|
| `.agents/identities/` | Agent identity files (personality + rules) |
| `.agents/workflows/` | Pipeline definitions (JSON) |
| `.agents/state.json` | Runtime state (queue, progress) |
| `assemblies/<name>/` | Assembly with components subdirectories |
| `shared/` | Global parameters, utilities, catalogs |
| `docs/bom/` | Bill of Materials (master + per-assembly) |
| `docs/build-guide/` | Step-by-step assembly instructions (DE) |
| `exports/` | STL/3MF build outputs |
| `src/` | FreeCAD Python scripts (bigBasis = active, smalBasis = legacy) |
| `src/bigBasis/` | XXL Generator + XXL Base Station (v2.x, ACTIVE) |
| `src/smalBasis/` | Small 10/20-pole generator + base station (LEGACY) |
| `src/tools/` | Winding machines and manufacturing tools |
| `src/tools/komplexSPooler/example.aufbau.py` | Virtual assembly (visual reference, not a printed part) |
| `exports/generator/` | Latest XXL generator STLs |
| `exports/xl_basis/` | Latest XXL base station STLs |

## Active Assembly Versions (2026-04-30)

| Assembly | Version | Source |
|----------|---------|--------|
| xl-generator | **2.1.0** | `src/bigBasis/big_base_generator.py` |
| xl-base-station | 2.0.0 | `src/bigBasis/big_base_station.py` |
| tools | **2.1.0** | `src/tools/komplexSPooler/` |
| tower | 1.x | `src/Helix_Leaf+Connector.py` |
