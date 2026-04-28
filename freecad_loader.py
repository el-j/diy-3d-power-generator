"""
WindPower-3D — FreeCAD Loader

Paste this ONCE into FreeCAD's Python console to set up the project.
After that, use run("scriptname") to load any script.

Usage in FreeCAD Python Console:
    exec(open("/Users/rex-fab-alt/Documents/code/playground/windpower-3d/freecad_loader.py").read())
    
    # Then run any script:
    run("Helix_Leaf+Connector")
    run("Helix_Generator_eckige-magnete-10er_rotor")
    run("Helix_Magnet_Basis_Station")
    run("tools/wickler_basis+wheels")
    run("tools/achsen+spule")
"""
import sys
import os

# ==========================================
# 📁 PROJECT ROOT SETUP
# ==========================================
# Automatically detect project root from this file's location
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else "/Users/rex-fab-alt/Documents/code/playground/windpower-3d"

# Add project root to Python path so "from shared.freecad_utils import *" works
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Also add the shared directory directly
SHARED_DIR = os.path.join(PROJECT_ROOT, "shared")
if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

print(f"✅ WindPower-3D project loaded from: {PROJECT_ROOT}")
print(f"   Scripts:    {os.path.join(PROJECT_ROOT, 'src')}")
print(f"   Shared:     {SHARED_DIR}")
print(f"   Parameters: {os.path.join(SHARED_DIR, 'parameters.json')}")
print()

# ==========================================
# 🚀 SCRIPT RUNNER
# ==========================================
def run(script_name):
    """
    Run a FreeCAD script by name.
    
    Usage:
        run("Helix_Leaf+Connector")           # runs src/Helix_Leaf+Connector.py
        run("tools/wickler_basis+wheels")       # runs src/tools/wickler_basis+wheels.py
        run("Helix_Generator_eckige-magnete-10er_rotor")
    """
    # Add .py if not present
    if not script_name.endswith(".py"):
        script_name += ".py"
    
    # Try src/ directory first
    script_path = os.path.join(PROJECT_ROOT, "src", script_name)
    
    if not os.path.exists(script_path):
        # Try direct path
        script_path = os.path.join(PROJECT_ROOT, script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script nicht gefunden: {script_name}")
        print(f"   Gesucht in: {os.path.join(PROJECT_ROOT, 'src')}")
        return
    
    print(f"🔧 Lade: {script_path}")
    exec(open(script_path).read(), globals())
    print(f"✅ Fertig: {script_name}")


def list_scripts():
    """List all available FreeCAD scripts."""
    src_dir = os.path.join(PROJECT_ROOT, "src")
    print("📁 Verfügbare Scripts:")
    print()
    for root, dirs, files in os.walk(src_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, f), src_dir)
                name = rel.replace(".py", "")
                print(f'   run("{name}")')
    print()


# Show available scripts on load
list_scripts()
