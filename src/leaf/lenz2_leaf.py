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
        "cup_arc_deg": v("cup_arc_deg", 210.0),
        "inner_scale": v("inner_scale", 0.62),
        "connector_h": v("kappen_dicke", tower["kappen_dicke"])
    }


def make_lenz2_blade(radius, thickness, arc_deg, inner_scale, height):
    a0 = -arc_deg / 2.0
    a1 = arc_deg / 2.0

    p_out_0 = App.Vector(radius * math.cos(math.radians(a0)), radius * math.sin(math.radians(a0)), 0)
    p_out_m = App.Vector(radius, 0, 0)
    p_out_1 = App.Vector(radius * math.cos(math.radians(a1)), radius * math.sin(math.radians(a1)), 0)

    r_in = max(0.1, radius * inner_scale - thickness)
    p_in_0 = App.Vector(r_in * math.cos(math.radians(a0)), r_in * math.sin(math.radians(a0)), 0)
    p_in_m = App.Vector(r_in, 0, 0)
    p_in_1 = App.Vector(r_in * math.cos(math.radians(a1)), r_in * math.sin(math.radians(a1)), 0)

    outer = Part.Arc(p_out_0, p_out_m, p_out_1).toShape()
    inner = Part.Arc(p_in_1, p_in_m, p_in_0).toShape()

    wire = Part.Wire([
        outer,
        Part.makeLine(p_out_1, p_in_1),
        inner,
        Part.makeLine(p_in_0, p_out_0)
    ])
    return Part.Face(wire).extrude(App.Vector(0, 0, height))


def main():
    params = get_variant_params("lenz2")
    global_params = load_parameters(section="global")
    doc = App.newDocument("Lenz2_Tower")

    rotor = None
    for i in range(3):
        blade = make_lenz2_blade(
            params["radius"],
            params["thickness"],
            params["cup_arc_deg"],
            params["inner_scale"],
            params["height"]
        )
        blade.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), i * 120.0)
        rotor = blade if rotor is None else rotor.fuse(blade)

    show_obj(doc, rotor.removeSplitter(), "Lenz2_Rotor_Stage")

    ring = Part.makeCylinder(params["radius"] + 6.0, params["connector_h"])
    ring = ring.cut(Part.makeCylinder(params["radius"] - 8.0, params["connector_h"]))
    spline = make_vielzahn_prism(
        global_params["vielzahn_r_out"] + 0.2,
        global_params["vielzahn_r_in"] + 0.2,
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    ring = ring.cut(spline)
    ring.translate(App.Vector((params["radius"] + 8.0) * 2.4, 0, 0))
    show_obj(doc, ring, "Lenz2_Connector_Ring")

    plug = make_vielzahn_prism(
        global_params["vielzahn_r_out"],
        global_params["vielzahn_r_in"],
        global_params["vielzahn_zaehne"],
        params["connector_h"]
    )
    shaft = make_square_prism(global_params["achse_kantenlaenge"] + global_params["toleranz"], params["connector_h"] + 2.0)
    shaft.translate(App.Vector(0, 0, -1.0))
    plug = plug.cut(shaft)
    plug.translate(App.Vector((params["radius"] + 8.0) * 2.4, 34.0, 0))
    show_obj(doc, plug, "Lenz2_Spline_Plug")

    finalize_doc(doc)
    print("Lenz2 variant generated: rotor stage + connector ring + plug")


if __name__ == "__main__":
    main()
