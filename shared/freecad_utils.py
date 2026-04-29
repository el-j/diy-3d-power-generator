"""
Shared FreeCAD utility functions for the WindPower-3D project.

Purpose: Eliminates code duplication across component scripts by providing
         common geometric primitives, array patterns, and display helpers.

Usage (3 Wege, je nach Workflow):

  1. LOADER (empfohlen): Einmal in FreeCAD pasten, dann run():
     exec(open("/path/to/windpower-3d/freecad_loader.py").read())
     run("Helix_Leaf+Connector")

  2. EXEC direkt: Am Anfang jedes Scripts diesen Bootstrap-Block:
     import sys, os
     _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
     if _root not in sys.path: sys.path.insert(0, _root)
     from shared.freecad_utils import *

  3. PASTE: freecad_utils.py Inhalt direkt in die Console pasten,
     dann Script pasten. (Alter Workflow, funktioniert weiterhin.)

Rationale: All 5 existing scripts duplicated these functions. Centralizing
           ensures consistency and simplifies maintenance.
Feature: INFRA-001 (Design Bureau Foundation)
"""

import FreeCAD as App
import Part
import math
import json
import os


# ==========================================
# 🔌 PROJECT BOOTSTRAP
# ==========================================

def setup_project(script_file=None):
    """
    Set up sys.path so shared imports work from any script location.

    Purpose: Call this at the top of any FreeCAD script to enable shared imports.
    Usage:
        # At the top of your FreeCAD script:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from shared.freecad_utils import *
        PROJECT_ROOT = setup_project(__file__)

    Returns: The project root path (for building relative paths to exports, etc.)
    """
    import sys

    if script_file:
        # Detect project root by walking up from the script location
        candidate = os.path.dirname(os.path.abspath(script_file))
        for _ in range(5):  # max 5 levels up
            if os.path.exists(os.path.join(candidate, "shared", "parameters.json")):
                if candidate not in sys.path:
                    sys.path.insert(0, candidate)
                return candidate
            candidate = os.path.dirname(candidate)

    # Fallback: this file lives in shared/, so project root is one level up
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(this_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return project_root


# ==========================================
# 📐 GEOMETRIC PRIMITIVES
# ==========================================

def make_square_prism(size, height):
    """
    Create a centered square prism (box centered on XY origin).

    Purpose: Square shaft hole for the 10×10mm Vierkant-Achse.
    Usage: make_square_prism(10.5, 20.0)  →  centered 10.5mm square, 20mm tall
    """
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box


def make_hex_prism(radius, height, rotation_offset=30.0):
    """
    Create a centered hexagonal prism.

    Purpose: Hex coupling for tower-to-base adapter.
    Usage: make_hex_prism(10.0, 8.0)
    Rationale: 30° default rotation places flat side toward blade slots.
    """
    points = []
    for j in range(7):
        angle = math.radians(60 * j + rotation_offset)
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    face = Part.Face(Part.Wire(polygon))
    return face.extrude(App.Vector(0, 0, height))


def make_vielzahn_prism(r_out, r_in, teeth, height, rotation_offset=15.0):
    """
    Create a centered spline (Vielzahn) prism with alternating inner/outer radii.

    Purpose: Rotational coupling between tower segments (12-tooth spline).
    Usage: make_vielzahn_prism(9.0, 7.8, 12, 8.0)
    Rationale: 15° offset aligns thick teeth with 45° corners of square shaft hole.
    """
    points = []
    for j in range(teeth * 2):
        angle = math.radians(j * (360.0 / (teeth * 2)) + rotation_offset)
        r = r_out if j % 2 == 0 else r_in
        points.append(App.Vector(r * math.cos(angle), r * math.sin(angle), 0))
    points.append(points[0])  # Close polygon
    return Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0, 0, height))


def make_capsule(length, width, height):
    """
    Create a centered capsule (stadium) shape — rectangle with semicircular ends.

    Purpose: Oval coil pockets in XXL generator stator.
    Usage: make_capsule(40.0, 26.0, 6.0)  →  40mm long, 26mm wide capsule
    Feature: INFRA-002 (XL Generator Support)
    """
    r = width / 2.0
    d = length - width
    cx = d / 2.0
    cyl1 = Part.makeCylinder(r, height).translate(App.Vector(cx, 0, 0))
    cyl2 = Part.makeCylinder(r, height).translate(App.Vector(-cx, 0, 0))
    box = Part.makeBox(d, width, height).translate(App.Vector(-cx, -r, 0))
    return cyl1.fuse(cyl2).fuse(box)


def make_centered_box(length, width, height, cx=0, cy=0, cz=None):
    """
    Create a box centered on a given point.

    Purpose: Cleaner positioning for pillars, brackets, pockets.
    Usage: make_centered_box(20, 12, 50, cx=0, cy=0, cz=25)
    Feature: INFRA-002 (Tool Scripts Support)
    """
    if cz is None:
        cz = height / 2.0
    box = Part.makeBox(length, width, height)
    box.translate(App.Vector(cx - length / 2.0, cy - width / 2.0, cz - height / 2.0))
    return box


# ==========================================
# 🔄 ARRAY PATTERNS
# ==========================================

def create_circular_array(radius, item_radius, depth, count):
    """
    Create a fused circular array of cylinders.

    Purpose: Coil holes in stator, bolt holes in rotors.
    Usage: create_circular_array(27.0, 7.0, 5.0, 12)  →  12 cylinders on R27 circle
    """
    items = []
    for i in range(count):
        angle = math.radians(i * (360.0 / count))
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        items.append(Part.makeCylinder(item_radius, depth).translate(App.Vector(x, y, 0)))
    res = items[0]
    for m in items[1:]:
        res = res.fuse(m)
    return res


def create_rectangular_array(radius, length, width, depth, count):
    """
    Create a fused circular array of rectangular boxes (rotated to face center).

    Purpose: Magnet pockets in generator rotors.
    Usage: create_rectangular_array(27.0, 20.0, 5.0, 6.0, 10)
    """
    items = []
    for i in range(count):
        angle_deg = i * (360.0 / count)
        angle_rad = math.radians(angle_deg)

        box = Part.makeBox(length, width, depth)
        box.translate(App.Vector(-length / 2.0, -width / 2.0, 0))
        box.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle_deg)
        box.translate(App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0))
        items.append(box)
    res = items[0]
    for m in items[1:]:
        res = res.fuse(m)
    return res


def create_capsule_array(radius, length, width, depth, count):
    """
    Create a fused circular array of capsule shapes (rotated to face center).

    Purpose: Oval coil pockets in XXL generator stator.
    Usage: create_capsule_array(74.0, 40.0, 26.0, 6.0, 12)
    Feature: INFRA-002 (XL Generator Support)
    """
    items = []
    for i in range(count):
        angle_deg = i * (360.0 / count)
        angle_rad = math.radians(angle_deg)
        cap = make_capsule(length, width, depth)
        cap.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle_deg)
        cap.translate(App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0))
        items.append(cap)
    res = items[0]
    for m in items[1:]:
        res = res.fuse(m)
    return res


# ==========================================
# 🖥️ DISPLAY & EXPORT HELPERS
# ==========================================

def show_obj(doc, shape, name):
    """
    Add a shape to the FreeCAD document as a Part::Feature.

    Purpose: Render geometry in the FreeCAD GUI.
    Usage: show_obj(doc, my_shape, "Rotor_Oben")
    """
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def finalize_doc(doc):
    """
    Recompute document and set axonometric view if GUI is available.

    Purpose: Standard end-of-script cleanup.
    Usage: finalize_doc(doc)
    """
    doc.recompute()
    if App.GuiUp:
        App.Gui.activeDocument().activeView().viewAxometric()
        App.Gui.SendMsgToActiveView("ViewFit")


def export_stl(doc, obj_name, export_dir):
    """
    Export a named object from the document as STL.

    Purpose: Generate printable mesh files.
    Usage: export_stl(doc, "Rotor_Oben", "/path/to/exports/generator")
    """
    obj = doc.getObject(obj_name)
    if obj is None:
        print(f"WARNING: Object '{obj_name}' not found in document.")
        return
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, f"{obj_name}.stl")
    obj.Shape.exportStl(filepath)
    print(f"Exported: {filepath}")


# ==========================================
# 📋 PARAMETER LOADING
# ==========================================

def load_parameters(param_file=None, section=None):
    """
    Load parameters from the central parameters.json registry.

    Purpose: Single source of truth for all dimensions.
    Usage: params = load_parameters(section="generator")
    Rationale: Prevents parameter drift between scripts.
    """
    if param_file is None:
        # Find parameters.json relative to this file
        this_dir = os.path.dirname(os.path.abspath(__file__))
        param_file = os.path.join(this_dir, "parameters.json")

    with open(param_file, "r") as f:
        data = json.load(f)

    if section:
        section_data = data.get(section, {})
        # Extract just the values for easy use
        result = {}
        for key, val in section_data.items():
            if isinstance(val, dict) and "value" in val:
                result[key] = val["value"]
            else:
                result[key] = val
        # Also merge global params
        for key, val in data.get("global", {}).items():
            if isinstance(val, dict) and "value" in val:
                result[key] = val["value"]
            else:
                result[key] = val
        return result
    return data
