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
        "airfoil_chord": v("airfoil_chord", 20.0),
        "airfoil_thickness": v("airfoil_thickness", 4.0),
        "strut_d": v("strut_d", 4.0),
        "hub_r": v("hub_r", 12.0),
        "connector_h": v("kappen_dicke", tower["kappen_dicke"])
    }


def make_airfoil(chord, thickness, height):
    front = Part.makeCylinder(thickness / 2.0, height)
    rear = Part.makeCylinder((thickness * 0.55) / 2.0, height)
    rear.translate(App.Vector(chord - thickness * 0.45, 0, 0))
    body = Part.makeBox(chord - thickness * 0.6, thickness, height)
    body.translate(App.Vector(thickness * 0.3, -thickness / 2.0, 0))
    return front.fuse(rear).fuse(body).removeSplitter()


def main():
    params = get_variant_params("darrieus_h")
    global_params = load_parameters(section="global")
    doc = App.newDocument("Darrieus_H_Tower")

    rotor = None
    for i in range(3):
        angle = math.radians(i * 120.0)
        blade = make_airfoil(params["airfoil_chord"], params["airfoil_thickness"], params["height"])
        blade.translate(App.Vector(params["radius"], -params["airfoil_thickness"] / 2.0, 0))
        blade.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), i * 120.0)

        # Two struts per blade (top + bottom) for H-rotor structure
        strut_len = params["radius"]
        for z in (params["height"] * 0.15, params["height"] * 0.85):
            strut = Part.makeCylinder(params["strut_d"] / 2.0, strut_len)
            strut.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
            strut.translate(App.Vector(0, 0, z))
            strut.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), i * 120.0)
            blade = blade.fuse(strut)

        rotor = blade if rotor is None else rotor.fuse(blade)

    hub = Part.makeCylinder(params["hub_r"], params["height"])
    rotor = rotor.fuse(hub).removeSplitter()
    show_obj(doc, rotor, "Darrieus_H_Rotor_Stage")

    top_disc = Part.makeCylinder(params["radius"] + 8.0, params["connector_h"])
    top_disc = top_disc.cut(Part.makeCylinder(params["hub_r"] + 1.0, params["connector_h"]))
    top_disc.translate(App.Vector(0, 0, params["height"] + 5.0))
    show_obj(doc, top_disc, "Darrieus_H_Top_Disc")

    bottom_disc = top_disc.copy()
    bottom_disc.translate(App.Vector(0, 0, -(params["height"] + 5.0)))
    spline = make_vielzahn_prism(
        global_params["vielzahn_r_out"] + 0.2,
        global_params["vielzahn_r_in"] + 0.2,
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    bottom_disc = bottom_disc.cut(spline)
    show_obj(doc, bottom_disc, "Darrieus_H_Bottom_Disc")

    plug = make_vielzahn_prism(
        global_params["vielzahn_r_out"],
        global_params["vielzahn_r_in"],
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    shaft = make_square_prism(global_params["achse_kantenlaenge"] + global_params["toleranz"], params["connector_h"] + 2.0)
    shaft.translate(App.Vector(0, 0, -1.0))
    plug = plug.cut(shaft)
    plug.translate(App.Vector((params["radius"] + 10.0) * 2.2, 0, 0))
    show_obj(doc, plug, "Darrieus_H_Spline_Plug")

    finalize_doc(doc)
    print("Darrieus H variant generated: rotor stage + top/bottom discs + plug")


if __name__ == "__main__":
    main()
