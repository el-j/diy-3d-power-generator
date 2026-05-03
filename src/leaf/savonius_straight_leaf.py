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
        "thickness": v("dicke", tower["dicke"]),
        "offset": v("versatz", tower["versatz"]),
        "connector_h": v("kappen_dicke", tower["kappen_dicke"]),
        "connector_r": v("connector_radius", tower["blatt_radius"] + 6.0)
    }


def make_savonius_blade(radius, thickness, offset, height):
    cx = radius - offset
    p0 = App.Vector(-offset, 0, 0)
    pm = App.Vector(cx, radius, 0)
    p1 = App.Vector(cx + radius, 0, 0)

    pi0 = App.Vector(-offset + thickness, 0, 0)
    pim = App.Vector(cx, radius - thickness, 0)
    pi1 = App.Vector(cx + radius - thickness, 0, 0)

    outer_arc = Part.Arc(p0, pm, p1).toShape()
    inner_arc = Part.Arc(pi1, pim, pi0).toShape()
    wire = Part.Wire([
        outer_arc,
        Part.makeLine(p1, pi1),
        inner_arc,
        Part.makeLine(pi0, p0)
    ])
    return Part.Face(wire).extrude(App.Vector(0, 0, height))


def main():
    params = get_variant_params("savonius_straight")
    global_params = load_parameters(section="global")

    doc = App.newDocument("Savonius_Straight_Tower")

    blade_a = make_savonius_blade(params["radius"], params["thickness"], params["offset"], params["height"])
    blade_b = blade_a.copy()
    blade_b.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)

    show_obj(doc, blade_a, "Savonius_Straight_Blade_A")
    show_obj(doc, blade_b, "Savonius_Straight_Blade_B")

    connector = Part.makeCylinder(params["connector_r"], params["connector_h"])
    spline_hole = make_vielzahn_prism(
        global_params["vielzahn_r_out"] + 0.2,
        global_params["vielzahn_r_in"] + 0.2,
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    connector = connector.cut(spline_hole)
    connector.translate(App.Vector(params["connector_r"] * 2.5, 0, 0))
    show_obj(doc, connector, "Savonius_Straight_Connector")

    plug_h = params["connector_h"]
    plug = make_vielzahn_prism(
        global_params["vielzahn_r_out"],
        global_params["vielzahn_r_in"],
        global_params["vielzahn_zaehne"],
        plug_h
    )
    shaft_hole = make_square_prism(global_params["achse_kantenlaenge"] + global_params["toleranz"], plug_h + 2.0)
    shaft_hole.translate(App.Vector(0, 0, -1.0))
    plug = plug.cut(shaft_hole)
    plug.translate(App.Vector(params["connector_r"] * 2.5, 35.0, 0))
    show_obj(doc, plug, "Savonius_Straight_Plug")

    finalize_doc(doc)
    print("Savonius straight variant generated: blades + connector + plug")


if __name__ == "__main__":
    main()
