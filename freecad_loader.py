"""
WindPower-3D — FreeCAD Loader

Paste this ONCE into FreeCAD's Python console to set up the project.
After that, use run("scriptname") to load any script.

Usage in FreeCAD Python Console:
    exec(open("/Users/rex-fab-alt/Documents/code/playground/windpower-3d/freecad_loader.py").read())
    
    # XL Basis (Hauptsystem):
    run("bigBasis/big_base_station")
    run("bigBasis/big_base_generator")
    
    # Turm:
    run("Helix_Leaf+Connector")
    
    # Werkzeuge:
    run("tools/komplexSPooler/Traversier-Basis & Skeleton")
    run("tools/ magnetPuffer/magnetBuffer")
    run("tools/easy_tool_big_spools-accuschrauber")
    run("tools/firstSpooler/wickler_basis+wheels")
    
    # Legacy (kleine Basis):
    run("smalBasis/Helix_Magnet_Basis_Station")
    run("smalBasis/Helix_Generator_eckige-magnete-10er_rotor")
    run("smalBasis/Helix_Generator_eckige-magnete-20er_rotor")
"""
import sys
import os

# ==========================================
# 📁 PROJECT ROOT SETUP
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else "/Users/rex-fab-alt/Documents/code/playground/windpower-3d"

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

SHARED_DIR = os.path.join(PROJECT_ROOT, "shared")
if SHARED_DIR not in sys.path:
    sys.path.insert(0, SHARED_DIR)

print(f"✅ WindPower-3D project loaded from: {PROJECT_ROOT}")
print()

# ==========================================
# 🚀 SCRIPT RUNNER
# ==========================================
def run(script_name):
    """
    Run a FreeCAD script by name.
    
    Usage:
        run("bigBasis/big_base_station")
        run("Helix_Leaf+Connector")
        run("tools/komplexSPooler/Traversier-Basis & Skeleton")
    """
    if not script_name.endswith(".py"):
        script_name += ".py"
    
    script_path = os.path.join(PROJECT_ROOT, "src", script_name)
    
    if not os.path.exists(script_path):
        script_path = os.path.join(PROJECT_ROOT, script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ Script nicht gefunden: {script_name}")
        print(f"   Gesucht in: {os.path.join(PROJECT_ROOT, 'src')}")
        print(f"   Tipp: list_scripts() zeigt alle verfügbaren Scripts")
        return
    
    print(f"🔧 Lade: {os.path.basename(script_path)}")
    exec(open(script_path).read(), globals())
    print(f"✅ Fertig: {script_name}")


def list_scripts():
    """List all available FreeCAD scripts, grouped by category."""
    src_dir = os.path.join(PROJECT_ROOT, "src")
    
    categories = {
        "bigBasis": "🏗️  XXL Basis & Generator (HAUPTSYSTEM)",
        "smalBasis": "📦  Legacy Kleine Basis",
        "tools": "🔧  Werkzeuge",
        "": "🗼  Turm"
    }
    
    scripts_by_cat = {}
    for root, dirs, files in os.walk(src_dir):
        for f in sorted(files):
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, f), src_dir)
                name = rel.replace(".py", "")
                
                cat = ""
                for prefix in ["bigBasis", "smalBasis", "tools"]:
                    if name.startswith(prefix):
                        cat = prefix
                        break
                
                if cat not in scripts_by_cat:
                    scripts_by_cat[cat] = []
                scripts_by_cat[cat].append(name)
    
    print("📁 Verfügbare Scripts:")
    print()
    for cat_key in ["bigBasis", "", "tools", "smalBasis"]:
        if cat_key in scripts_by_cat:
            label = categories.get(cat_key, cat_key)
            print(f"  {label}")
            for name in scripts_by_cat[cat_key]:
                print(f'    run("{name}")')
            print()

list_scripts()
