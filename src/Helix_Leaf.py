import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Coreless_Tower")

# ==========================================
# ⚙️ PARAMETER (Bambu Lab P1S - 256x256mm)
# ==========================================
hohe = 240.0              # Z-Höhe für P1S max
blatt_radius = 66.0       # Ergibt 250mm Gesamtdurchmesser
dicke = 2.4               # Wanddicke der Flügel
versatz = 12.0            

# VIERKANT-ACHSE
achse_kantenlaenge = 10.0 

# HELIX
twist_winkel = 90.0       
loft_steps = 60           

# UNIFIED HEX-SYSTEM & VERBINDER
kappen_dicke = 8.0        # 8mm dick (3mm Rille Oben + 2mm Wand + 3mm Rille Unten)
rillen_tiefe = 3.0        
toleranz = 0.5            

hex_radius = 10.5         # Das gedrehte, flügelfreie 10.5mm Hexagon
hex_h = kappen_dicke

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 4.0  # 4mm Tiefe für den schmalen Kragen
kragen_d = 17.5           # Schmal genug, um die Flügel nicht zu blockieren
kragen_h = 15.0
# ==========================================

cx = blatt_radius - versatz
gesamt_radius = cx + blatt_radius

def make_hex_prism(radius, height):
    points = []
    for j in range(7):
        # +30 Grad Drehung, flache Seite zu den Flügeln!
        angle = math.radians(60 * j + 30) 
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

def create_blade_wire(offset_dicke, extra_radius=0):
    p_out_start = App.Vector(-versatz - extra_radius, 0, 0)
    p_out_mid = App.Vector(cx, blatt_radius + extra_radius, 0)
    p_out_end = App.Vector(cx + blatt_radius + extra_radius, 0, 0)
    arc_out = Part.Arc(p_out_start, p_out_mid, p_out_end)

    p_in_start = App.Vector(-versatz + offset_dicke + extra_radius, 0, 0)
    p_in_mid = App.Vector(cx, blatt_radius - offset_dicke - extra_radius, 0)
    p_in_end = App.Vector(cx + blatt_radius - offset_dicke - extra_radius, 0, 0)
    arc_in = Part.Arc(p_in_start, p_in_mid, p_in_end)

    return Part.Wire([arc_out.toShape(), Part.makeLine(p_out_end, p_in_end), arc_in.toShape(), Part.makeLine(p_in_start, p_out_start)])

base_wire = create_blade_wire(dicke)
cutter_wire = create_blade_wire(dicke + toleranz, toleranz / 2.0)

# ==========================================
# 1. DAS DRUCKBARE HELIX-BLATT
# ==========================================
wires = []
for j in range(loft_steps + 1):
    z = (hohe / loft_steps) * j
    angle = (twist_winkel / loft_steps) * j
    w = base_wire.copy()
    w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    w.translate(App.Vector(0, 0, z))
    wires.append(w)

druck_blatt = Part.makeLoft(wires, True).removeSplitter()
show_obj(druck_blatt, "Coreless_Helix_Fluegel")


# # ==========================================
# # 2. SKELETT-VERBINDER (Mittelstück, Flachdruck)
# # ==========================================
# # A) Die 3mm dicke Außenhülle um den Flügel erzeugen (Skelett-Rahmen)
# shell_wire = create_blade_wire(dicke + 6.0, 3.0) 
# shell_1 = Part.Face(shell_wire).extrude(App.Vector(0,0,kappen_dicke))

# shell_wire_180 = shell_wire.copy()
# shell_wire_180.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
# shell_2 = Part.Face(shell_wire_180).extrude(App.Vector(0,0,kappen_dicke))

# # B) Zentraler Hub (Hält den Sechskant sicher)
# hub = Part.makeCylinder(22.0, kappen_dicke)
# verbinder = hub.fuse(shell_1).fuse(shell_2)

# # C) Hex-Loch (+0.2 Toleranz zum Stecken)
# verbinder = verbinder.cut(make_hex_prism(hex_radius + 0.2, kappen_dicke))

# # D) Rillen einschneiden (Unten UND Oben)
# cutter_0 = cutter_wire.copy()
# cutter_180 = cutter_wire.copy()
# cutter_180.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)

# # Rillen von UNTEN (Z=0 bis 3mm) - Druckt sich problemlos frei schwebend (Bridging)!
# rille_unten_1 = Part.Face(cutter_0).extrude(App.Vector(0,0,rillen_tiefe))
# rille_unten_2 = Part.Face(cutter_180).extrude(App.Vector(0,0,rillen_tiefe))
# verbinder = verbinder.cut(rille_unten_1).cut(rille_unten_2)

# # Rillen von OBEN (Z=5mm bis 8mm)
# rille_oben_1 = Part.Face(cutter_0).extrude(App.Vector(0,0,rillen_tiefe)).translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
# rille_oben_2 = Part.Face(cutter_180).extrude(App.Vector(0,0,rillen_tiefe)).translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
# verbinder = verbinder.cut(rille_oben_1).cut(rille_oben_2)

# verbinder = verbinder.removeSplitter()
# verbinder.translate(App.Vector(gesamt_radius * 2.2, 0, 0)) 
# show_obj(verbinder, "Mittel_Verbinder_Skelett_FLACH")


# # ==========================================
# # 3. ZWISCHEN-HEX-PLUG (Der Adapter)
# # ==========================================
# plug = make_hex_prism(hex_radius, hex_h)

# # Kragen für die 4x Anti-Unwucht Madenschrauben
# kragen = Part.makeCylinder(kragen_d / 2.0, kragen_h).translate(App.Vector(0,0, hex_h))
# plug = plug.fuse(kragen)

# # 10x10 Achsloch
# achse_cut = make_square_prism(achse_kantenlaenge + toleranz, hex_h + kragen_h + 10.0)
# achse_cut.translate(App.Vector(0,0, -5.0))
# plug = plug.cut(achse_cut)

# # 4x M3 Gewindeeinsatz und Löcher im Kragen
# for i in range(4):
#     angle = i * 90
#     m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
#     m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
#     m3_loch.translate(App.Vector(-10, 0, hex_h + (kragen_h / 2.0)))
#     m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
#     m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
#     m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
#     m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, hex_h + (kragen_h / 2.0)))
#     m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
#     plug = plug.cut(m3_loch).cut(m3_insert)

# plug = plug.removeSplitter()
# plug.translate(App.Vector(gesamt_radius * 2.2, 60.0, 0)) 
# show_obj(plug, "Zwischen_Hex_Plug")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Skelett-Verbinder & Hex-Plug System erfolgreich hinzugefügt!")