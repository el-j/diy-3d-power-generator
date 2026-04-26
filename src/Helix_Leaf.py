import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Coreless_Tower")

# ==========================================
# ⚙️ PARAMETER (Exakt berechnet für Bambu Lab P1S - 256x256mm)
# ==========================================
hohe = 240.0              # Z-Höhe nutzt den P1S maximal aus
blatt_radius = 66.0       # Skaliert: Ergibt exakt 250mm Gesamtdurchmesser!
dicke = 2.4               # Wanddicke (6 Wandlinien)
versatz = 12.0            # Skaliert für perfekten Cross-Flow

# VIERKANT-ACHSE (Bleibt bei Originalgröße!)
achse_kantenlaenge = 10.0 

# DIE CORELESS-HELIX 
twist_winkel = 90.0       
loft_steps = 60           

# BAUKASTEN-PARAMETER
kappen_dicke = 6.0        
rillen_tiefe = 3.0        
toleranz = 0.5            
# ==========================================

cx = blatt_radius - versatz
gesamt_radius = cx + blatt_radius
kappen_radius = gesamt_radius + 5.0 # Radius 125mm = Durchmesser 250mm (Perfekt für P1S!)

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def create_blade_wire(offset_dicke, extra_radius=0):
    p_out_start = App.Vector(-versatz - extra_radius, 0, 0)
    p_out_mid = App.Vector(cx, blatt_radius + extra_radius, 0)
    p_out_end = App.Vector(cx + blatt_radius + extra_radius, 0, 0)
    arc_out = Part.Arc(p_out_start, p_out_mid, p_out_end)

    p_in_start = App.Vector(-versatz + offset_dicke + extra_radius, 0, 0)
    p_in_mid = App.Vector(cx, blatt_radius - offset_dicke - extra_radius, 0)
    p_in_end = App.Vector(cx + blatt_radius - offset_dicke - extra_radius, 0, 0)
    arc_in = Part.Arc(p_in_start, p_in_mid, p_in_end)

    edge_out = arc_out.toShape()
    edge_in = arc_in.toShape()
    edge_tip1 = Part.makeLine(p_out_end, p_in_end)
    edge_tip2 = Part.makeLine(p_in_start, p_out_start)

    return Part.Wire([edge_out, edge_tip1, edge_in, edge_tip2])

base_wire = create_blade_wire(dicke)
cutter_wire = create_blade_wire(dicke + toleranz, toleranz / 2.0)

# 1. DAS DRUCKBARE HELIX-BLATT
wires = []
for j in range(loft_steps + 1):
    z = (hohe / loft_steps) * j
    angle = (twist_winkel / loft_steps) * j
    w = base_wire.copy()
    w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    w.translate(App.Vector(0, 0, z))
    wires.append(w)

druck_blatt = Part.makeLoft(wires, True)
druck_blatt = druck_blatt.removeSplitter()

cutter_0 = cutter_wire.copy()
cutter_180 = cutter_wire.copy()
cutter_180.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)

# 2. DER UNIVERSAL-VERBINDER (Kappe)
kappe = Part.makeCylinder(kappen_radius, kappen_dicke)

rille_unten_1 = Part.Face(cutter_0).extrude(App.Vector(0,0,rillen_tiefe))
rille_unten_2 = Part.Face(cutter_180).extrude(App.Vector(0,0,rillen_tiefe))
kappe = kappe.cut(rille_unten_1).cut(rille_unten_2)

rille_oben_1 = Part.Face(cutter_0).extrude(App.Vector(0,0,rillen_tiefe))
rille_oben_1.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
rille_oben_2 = Part.Face(cutter_180).extrude(App.Vector(0,0,rillen_tiefe))
rille_oben_2.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
kappe = kappe.cut(rille_oben_1).cut(rille_oben_2)

achse_loch = make_square_prism(achse_kantenlaenge + toleranz, kappen_dicke)
kappe = kappe.cut(achse_loch)
kappe = kappe.removeSplitter()

druck_blatt.translate(App.Vector(0, 0, 0)) 
kappe.translate(App.Vector(gesamt_radius * 2.5, 0, 0)) 

Part.show(druck_blatt)
Part.show(kappe)

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Coreless Helix-System auf P1S Größe herunterskaliert!")