import FreeCAD as App
import Part
import math

doc = App.newDocument("Helix_Coreless_Tower")

# ==========================================
# ⚙️ PARAMETER (Bambu Lab P1S - 256x256mm)
# ==========================================
hohe = 240.0              # Z-Höhe für P1S max
blatt_radius = 66.0       # Ergibt 250mm Gesamtdurchmesser
dicke = 2.4               # Wanddicke der Flügel
versatz = 12.0            

# VIERKANT-ACHSE
achse_kantenlaenge = 10.0 
# HEXAGON-LOCH in der Startscheibe (für die 6x M3 Madenschrauben, die die Scheibe auf der Achse fixieren)
hex_radius = 10.5        

# HELIX
twist_winkel = 90.0       
loft_steps = 60           

# UNIFIED VIELZAHN-SYSTEM & VERBINDER
kappen_dicke = 8.0        # 8mm dick (3mm Rille Oben + 2mm Wand + 3mm Rille Unten)
rillen_tiefe = 3.0        
toleranz = 0.5            

vielzahn_zaehne = 12       # REDUZIERT auf 12 Zähne = 30° Rast-Schritte (Passt perfekt für 60°/90° Twist)
vielzahn_r_out = 9.0       # KLEINER: Bleibt unter 9.1mm, berührt die Flügel nicht mehr!
vielzahn_r_in = 7.8        # Innenradius Vielzahn
vielzahn_h = kappen_dicke

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 4.0  # 4mm Tiefe für den schmalen Kragen
kragen_d = 17.5           # Schmal genug, um die Flügel nicht zu blockieren
kragen_h = 15.0
# ==========================================

cx = blatt_radius - versatz
gesamt_radius = cx + blatt_radius

def make_vielzahn_prism(r_out, r_in, teeth, height):
    points = []
    for j in range(teeth * 2):
        # +15 Grad Drehung: Legt die dicken Zähne exakt auf die 45°-Ecken des internen Vierkant-Lochs!
        angle = math.radians(j * (360.0 / (teeth * 2)) + 15)
        r = r_out if j % 2 == 0 else r_in
        points.append(App.Vector(r * math.cos(angle), r * math.sin(angle), 0))
    points.append(points[0]) # Polygon schließen
    return Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0, 0, height))

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
cutter_wire = create_blade_wire(dicke + toleranz, toleranz)  # full toleranz (0.5mm) outward clearance for reliable insertion
shell_wire = create_blade_wire(dicke + 6.0, 3.0)

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


# ==========================================
# 2. SKELETT-VERBINDER (Mittelstück, Flachdruck)
# ==========================================
# A) Die Außenhülle um den Flügel erzeugen (Skelett-Rahmen mit runden Endkappen!)
shell_1_base = Part.Face(shell_wire).extrude(App.Vector(0,0,kappen_dicke))

# Die perfekte runde Endkappe für die Hülle hinzufügen
cap_x = cx + blatt_radius - (dicke / 2.0)
shell_cap_radius = (dicke / 2.0) + 3.0
shell_cap = Part.makeCylinder(shell_cap_radius, kappen_dicke)
shell_cap.translate(App.Vector(cap_x, 0, 0))
shell_1 = shell_1_base.fuse(shell_cap)

shell_2 = shell_1.copy()
shell_2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)

# B) Zentraler Hub
hub = Part.makeCylinder(22.0, kappen_dicke)
verbinder = hub.fuse(shell_1).fuse(shell_2)

# C) Vielzahn-Loch
verbinder = verbinder.cut(make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, kappen_dicke))

# D) Rillen einschneiden (Unten UND Oben) mit runden Cuttern am Ende!
cutter_0_base = Part.Face(cutter_wire).extrude(App.Vector(0,0,rillen_tiefe))
cutter_cap_radius = (dicke + toleranz) / 2.0
cutter_cap_unten = Part.makeCylinder(cutter_cap_radius, rillen_tiefe)
cutter_cap_unten.translate(App.Vector(cap_x, 0, 0))

# Den geraden Cutter mit der runden Endkappe verschmelzen
rille_unten_1 = cutter_0_base.fuse(cutter_cap_unten)
rille_unten_2 = rille_unten_1.copy()
rille_unten_2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
verbinder = verbinder.cut(rille_unten_1).cut(rille_unten_2)

# Kopie für die obere Seite anfertigen
rille_oben_1 = rille_unten_1.copy()
rille_oben_1.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
rille_oben_2 = rille_unten_2.copy()
rille_oben_2.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))
verbinder = verbinder.cut(rille_oben_1).cut(rille_oben_2)

verbinder = verbinder.removeSplitter()
verbinder.translate(App.Vector(gesamt_radius * 2.2, 0, 0)) 
show_obj(verbinder, "Mittel_Verbinder_Skelett_FLACH")


# ==========================================
# 3. ZWISCHEN-VIELZAHN-PLUG (Der Adapter)
# ==========================================
plug = make_vielzahn_prism(vielzahn_r_out, vielzahn_r_in, vielzahn_zaehne, vielzahn_h)

# Kragen für die 4x Anti-Unwucht Madenschrauben
kragen = Part.makeCylinder(kragen_d / 2.0, kragen_h).translate(App.Vector(0,0, vielzahn_h))
plug = plug.fuse(kragen)

# 10x10 Achsloch
achse_cut = make_square_prism(achse_kantenlaenge + toleranz, vielzahn_h + kragen_h + 10.0)
achse_cut.translate(App.Vector(0,0, -5.0))
plug = plug.cut(achse_cut)

# 4x M3 Gewindeeinsatz und Löcher im Kragen
for i in range(4):
    angle = i * 90
    m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_loch.translate(App.Vector(-10, 0, vielzahn_h + (kragen_h / 2.0)))
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    # Insert flush with collar outer surface — intentional, heat-set inserts are pressed in from outside
    m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, vielzahn_h + (kragen_h / 2.0)))
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    plug = plug.cut(m3_loch).cut(m3_insert)

plug = plug.removeSplitter()
plug.translate(App.Vector(gesamt_radius * 2.2, 60.0, 0)) 
show_obj(plug, "Zwischen_Vielzahn_Plug")




def make_hex_prism(radius, height):
    points = []
    for j in range(7):
        angle = math.radians(60 * j + 30) 
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    face = Part.Face(Part.Wire(polygon))
    return face.extrude(App.Vector(0, 0, height))


# ==========================================
# BAUTEIL 6: FLACHE START-SCHEIBE 
# ==========================================
kappen_radius_scheibe = blatt_radius - versatz + blatt_radius + 5.0 
scheibe = Part.makeCylinder(kappen_radius_scheibe, kappen_dicke)

hex_cut = make_hex_prism(hex_radius + 0.2, kappen_dicke)
scheibe = scheibe.cut(hex_cut)

for i in range(6):
    angle = math.radians(i * 60)
    x = 75.0 * math.cos(angle)
    y = 75.0 * math.sin(angle)
    loch = Part.makeCylinder(36.0, 6.0).translate(App.Vector(x, y, 0))
    scheibe = scheibe.cut(loch)

cx_scheibe = blatt_radius - versatz
po_s = App.Vector(-versatz, 0, 0)
po_m = App.Vector(cx_scheibe, blatt_radius, 0)
po_e = App.Vector(cx_scheibe + blatt_radius, 0, 0)
pi_s = App.Vector(-versatz + dicke + toleranz, 0, 0)
pi_m = App.Vector(cx_scheibe, blatt_radius - dicke - toleranz, 0)
pi_e = App.Vector(cx_scheibe + blatt_radius - dicke - toleranz, 0, 0)

blade_wire = Part.Wire([
    Part.Arc(po_s, po_m, po_e).toShape(), 
    Part.makeLine(po_e, pi_e), 
    Part.Arc(pi_e, pi_m, pi_s).toShape(), 
    Part.makeLine(pi_s, po_s)
])

blade_cut = Part.Face(blade_wire).extrude(App.Vector(0,0,5.0))
blade_cut.translate(App.Vector(0,0, kappen_dicke - 5.0))

scheibe = scheibe.cut(blade_cut)
blade_cut2 = blade_cut.copy()
blade_cut2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
scheibe = scheibe.cut(blade_cut2)

scheibe = scheibe.removeSplitter()
scheibe.translate(App.Vector(0, 0, 0)) 
show_obj(scheibe, "Start_Scheibe_FLACH")


doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Skelett-Verbinder mit runden, geschlossenen Enden erfolgreich generiert!")