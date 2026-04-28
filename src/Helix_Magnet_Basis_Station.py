import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station")

# ==========================================
# ⚙️ PARAMETER FÜR DIE BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Maße für das Kegelrollenlager (32005)
lager_innen_d = 25.0      
lager_aussen_d = 47.0     
lager_dicke = 15.0        

# Schlitten & Generator
schlitten_breite = 95.0 
fuss_radius = 60.0 
gehaeuse_h = 110.0 

# Turm Daten & Hex-System
blatt_radius = 66.0       
dicke = 2.4               
versatz = 12.0            
kappen_dicke = 8.0        
hex_radius = 10.0         
hex_h = kappen_dicke

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0  
# ==========================================

def make_hex_prism(radius, height):
    points = []
    for j in range(7):
        angle = math.radians(60 * j + 30) 
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    face = Part.Face(Part.Wire(polygon))
    return face.extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DER MASCHINEN-FUSS (Mit Flansch-Pads!)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# 1. Der Lagersitz ganz oben
lager_sitz = Part.makeCylinder((lager_aussen_d + 0.2) / 2.0, lager_dicke)
lager_sitz.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke))
gehaeuse = gehaeuse.cut(lager_sitz)

# 2. Die dicke Schulter, die das Lager stützt
schulter_durchlass = Part.makeCylinder(14.0, 10.0)
schulter_durchlass.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke - 10.0))
gehaeuse = gehaeuse.cut(schulter_durchlass)

# 3. DIE EINSCHUB-ETAGEN
k_cyl = Part.makeCylinder(40.0, 30.0)
k_box = Part.makeBox(80.0, 80.0, 30.0).translate(App.Vector(-40.0, -80.0, 0))
gehaeuse = gehaeuse.cut(k_cyl).cut(k_box)

s_cyl = Part.makeCylinder(47.5, 5.2).translate(App.Vector(0,0,30.0))
s_box = Part.makeBox(95.0, 80.0, 5.2).translate(App.Vector(-47.5, -80.0, 30.0))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

g_cyl = Part.makeCylinder(46.0, 49.8).translate(App.Vector(0, 0, 35.2))
g_box = Part.makeBox(92.0, 80.0, 49.8).translate(App.Vector(-46.0, -80.0, 35.2))
gehaeuse = gehaeuse.cut(g_cyl).cut(g_box)

# 4. NEU: Die 3 Flansch-Pads (bei 0°, 90° und 180°)
for angle in [0, 90, 180]:
    # Der flache Block auf der Außenseite
    pad = Part.makeBox(15.0, 40.0, 50.0).translate(App.Vector(53.0, -20.0, 20.0))
    pad.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    gehaeuse = gehaeuse.fuse(pad)
    
    # 4 Bohrlöcher pro Pad
    for dy in [-12, 12]:
        for dz in [30, 60]:
            # Durchgangsloch (Tiefe auf 18mm limitiert, damit innen 2.5mm Wand stehen bleibt!)
            loch = Part.makeCylinder(3.4 / 2.0, 18.0)
            loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            loch.translate(App.Vector(50.0, dy, dz))
            loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            gehaeuse = gehaeuse.cut(loch)
            
            # Tasche für die Einschmelzmutter (Plan auf der Außenfläche bei X=68)
            insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
            insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            insert.translate(App.Vector(68.0 - einschmelzmutter_t, dy, dz))
            insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            gehaeuse = gehaeuse.cut(insert)

gehaeuse = gehaeuse.removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse")


# ==========================================
# BAUTEIL 2: DER WAND-FLANSCH (NEU!)
# ==========================================
bracket_w = 40.0
bracket_h = 50.0
bracket_d = 40.0
wall_thick = 6.0

# Vertikale Platte (wird an die Basis geschraubt)
b_vert = Part.makeBox(wall_thick, bracket_w, bracket_h)
b_vert.translate(App.Vector(0, -bracket_w/2.0, 0))

# Horizontale Platte (wird an die Wand geschraubt)
b_horiz = Part.makeBox(bracket_d, bracket_w, wall_thick)
b_horiz.translate(App.Vector(0, -bracket_w/2.0, 0))
bracket = b_vert.fuse(b_horiz)

# Stütz-Dreiecke für extreme Stabilität
p1 = App.Vector(wall_thick, -bracket_w/2.0, wall_thick)
p2 = App.Vector(bracket_d, -bracket_w/2.0, wall_thick)
p3 = App.Vector(wall_thick, -bracket_w/2.0, bracket_h)
tri1 = Part.Face(Part.Wire(Part.makePolygon([p1, p2, p3, p1]))).extrude(App.Vector(0, 4.0, 0))

p1_2 = App.Vector(wall_thick, bracket_w/2.0 - 4.0, wall_thick)
p2_2 = App.Vector(bracket_d, bracket_w/2.0 - 4.0, wall_thick)
p3_2 = App.Vector(wall_thick, bracket_w/2.0 - 4.0, bracket_h)
tri2 = Part.Face(Part.Wire(Part.makePolygon([p1_2, p2_2, p3_2, p1_2]))).extrude(App.Vector(0, 4.0, 0))

bracket = bracket.fuse(tri1).fuse(tri2)

# Löcher für die Befestigung an der Basisstation (M3 Senkkopf)
for dy in [-12, 12]:
    for dz in [10, 40]: 
        loch = Part.makeCylinder(3.4 / 2.0, wall_thick + 2)
        loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        loch.translate(App.Vector(-1.0, dy, dz))
        
        senk = Part.makeCone(6.0/2.0, 3.4/2.0, 2.0)
        senk.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        senk.translate(App.Vector(0, dy, dz))
        
        bracket = bracket.cut(loch).cut(senk)

# Löcher für die Wandmontage (5.5mm für dicke Spax-Schrauben)
for dy in [-10, 10]:
    loch = Part.makeCylinder(5.5 / 2.0, wall_thick + 2)
    loch.translate(App.Vector(bracket_d - 12.0, dy, -1))
    
    senk = Part.makeCone(10.0/2.0, 5.5/2.0, 3.0)
    senk.translate(App.Vector(bracket_d - 12.0, dy, wall_thick - 3.0))
    bracket = bracket.cut(loch).cut(senk)

bracket = bracket.removeSplitter()
bracket.translate(App.Vector(-100, 0, 0)) 
show_obj(bracket, "Wand_Flansch")


# ==========================================
# BAUTEIL 3: DER SCHLITTEN
# ==========================================
schlitten_radius = 47.0 
schlitten_back = Part.makeCylinder(schlitten_radius, 5.0)
schlitten_front = Part.makeBox(schlitten_radius * 2, 70.0, 5.0)
schlitten_front.translate(App.Vector(-schlitten_radius, -70.0, 0))

schlitten = schlitten_back.fuse(schlitten_front)

griff = Part.makeBox(30.0, 10.0, 5.0).translate(App.Vector(-15.0, -80.0, 0))
schlitten = schlitten.fuse(griff)
schlitten = schlitten.cut(Part.makeCylinder(20.0, 5.0))

for i in range(4):
    angle = math.radians(i * 90 + 45)
    x = 41.5 * math.cos(angle)
    y = 41.5 * math.sin(angle)
    loch = Part.makeCylinder(1.7, 5.0).translate(App.Vector(x, y, 0))
    schlitten = schlitten.cut(loch)

schlitten = schlitten.removeSplitter()
schlitten.translate(App.Vector(0, -fuss_radius * 2.0, 0)) 
show_obj(schlitten, "Schiebe_Schlitten")


# ==========================================
# BAUTEIL 4: FLACHE START-SCHEIBE 
# ==========================================
kappen_radius_scheibe = blatt_radius - versatz + blatt_radius + 5.0 
scheibe = Part.makeCylinder(kappen_radius_scheibe, kappen_dicke)

hex_cut = make_hex_prism(hex_radius + 0.2, kappen_dicke)
scheibe = scheibe.cut(hex_cut)

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
scheibe.translate(App.Vector(0, fuss_radius * 2.8, 0)) 
show_obj(scheibe, "Start_Scheibe_FLACH")


# ==========================================
# BAUTEIL 5: MODULARER VERBINDER-ADAPTER (Hex-Plug)
# ==========================================
plug = make_hex_prism(hex_radius, hex_h)

lager_schaft = Part.makeCylinder((lager_innen_d - 0.2) / 2.0, lager_dicke + 2.0)
lager_schaft.translate(App.Vector(0,0, -lager_dicke - 2.0))
plug = plug.fuse(lager_schaft)

kragen = Part.makeCylinder(kragen_d / 2.0, kragen_h)
kragen.translate(App.Vector(0,0, hex_h))
plug = plug.fuse(kragen)

achse_cut = make_square_prism(achse_kantenlaenge + toleranz, hex_h + lager_dicke + kragen_h + 5.0)
achse_cut.translate(App.Vector(0,0, -lager_dicke - 3.0))
plug = plug.cut(achse_cut)

einschmelzmutter_t_kragen = 4.0 
for i in range(4):
    angle = i * 90
    m3_loch = Part.makeCylinder(3.4 / 2.0, 30.0)
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_loch.translate(App.Vector(-15, 0, hex_h + (kragen_h / 2.0)))
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t_kragen)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t_kragen, 0, hex_h + (kragen_h / 2.0)))
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    plug = plug.cut(m3_loch).cut(m3_insert)

plug = plug.removeSplitter()
plug.translate(App.Vector(fuss_radius * 2.5, 0, 0)) 
show_obj(plug, "Adapter_Hex_Verbinder")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")