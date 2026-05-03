import FreeCAD as App
import Part
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from shared.freecad_utils import load_parameters, make_square_prism, make_vielzahn_prism, show_obj, finalize_doc


def get_variant_params(variant_key):
    data = load_parameters()
    tower = {k: v["value"] for k, v in data["tower"].items() if isinstance(v, dict) and "value" in v}
    variant = data.get("tower_variants", {}).get(variant_key, {})

    def v(name, default):
        item = variant.get(name)
        if isinstance(item, dict) and "value" in item:
            return item["value"]
        return default

    return {
        "height": v("hohe", tower["hohe"]),
        "radius": v("blatt_radius", tower["blatt_radius"]),
        "airfoil_chord": v("airfoil_chord", 16.0),
        "airfoil_thickness": v("airfoil_thickness", 3.4),
        "twist_winkel": v("twist_winkel", 120.0),
        "steps": v("loft_steps", 48),
        "connector_h": v("kappen_dicke", tower["kappen_dicke"])
    }


def make_airfoil_wire(chord, thickness):
    x0 = -chord / 2.0
    x1 = chord / 2.0
    top_mid = App.Vector(0, thickness / 2.0, 0)
    bot_mid = App.Vector(0, -thickness / 2.0, 0)

    top = Part.Arc(App.Vector(x0, 0, 0), top_mid, App.Vector(x1, 0, 0)).toShape()
    bottom = Part.Arc(App.Vector(x1, 0, 0), bot_mid, App.Vector(x0, 0, 0)).toShape()
    return Part.Wire([top, bottom])


def make_gorlov_blade(radius, chord, thickness, height, twist_deg, steps, base_angle_deg):
    base = make_airfoil_wire(chord, thickness)
    wires = []
    for i in range(steps + 1):
        z = height * (float(i) / float(steps))
        ang = base_angle_deg + twist_deg * (float(i) / float(steps))
        wire = base.copy()
        wire.translate(App.Vector(radius, 0, 0))
        wire.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), ang)
        wire.translate(App.Vector(0, 0, z))
        wires.append(wire)
    return Part.makeLoft(wires, True).removeSplitter()


def main():
    params = get_variant_params("gorlov")
    global_params = load_parameters(section="global")
    doc = App.newDocument("Gorlov_Tower")

    rotor = None
    for i in range(3):
        blade = make_gorlov_blade(
            params["radius"],
            params["airfoil_chord"],
            params["airfoil_thickness"],
            params["height"],
            params["twist_winkel"],
            params["steps"],
            i * 120.0
        )
        rotor = blade if rotor is None else rotor.fuse(blade)

    hub = Part.makeCylinder(12.0, params["height"])
    rotor = rotor.fuse(hub).removeSplitter()
    show_obj(doc, rotor, "Gorlov_Helical_Rotor_Stage")

    connector = Part.makeCylinder(params["radius"] + 6.0, params["connector_h"])
    connector = connector.cut(Part.makeCylinder(13.0, params["connector_h"]))
    connector = connector.cut(make_vielzahn_prism(
        global_params["vielzahn_r_out"] + 0.2,
        global_params["vielzahn_r_in"] + 0.2,
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    ))
    connector.translate(App.Vector((params["radius"] + 8.0) * 2.3, 0, 0))
    show_obj(doc, connector, "Gorlov_Connector_Ring")

    plug = make_vielzahn_prism(
        global_params["vielzahn_r_out"],
        global_params["vielzahn_r_in"],
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    shaft = make_square_prism(global_params["achse_kantenlaenge"] + global_params["toleranz"], params["connector_h"] + 2.0)
    shaft.translate(App.Vector(0, 0, -1.0))
    plug = plug.cut(shaft)
    plug.translate(App.Vector((params["radius"] + 8.0) * 2.3, 36.0, 0))
    show_obj(doc, plug, "Gorlov_Spline_Plug")

    finalize_doc(doc)
    print("Gorlov variant generated: helical rotor stage + connector + plug")


if __name__ == "__main__":
    main()
