import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station_XXL")

# ==========================================
# ⚙️ PARAMETER FÜR DIE XXL BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

lager_innen_d = 25.0      
lager_aussen_d = 47.0     
lager_dicke = 15.0        

# MASSIVE GRÖSSEN!
fuss_radius = 110.0       # 220mm Gesamtdurchmesser
gehaeuse_h = 145.0        # Gestreckt auf 145mm für den modularen Boden-Schlitten!

# Turm & Adapter Daten
blatt_radius = 66.0       
dicke = 2.4               
versatz = 12.0            
hex_radius = 10.5         
kappen_dicke = 8.0        

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
# BAUTEIL 1: DER XXL MASCHINEN-FUSS (Wasser-Dichtes Skelett!)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# 1. Z=130 bis 145: Der obere Lagersitz
lager_sitz = Part.makeCylinder((lager_aussen_d + 0.4) / 2.0, lager_dicke)
lager_sitz.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke))
gehaeuse = gehaeuse.cut(lager_sitz)

# 2. Z=120 bis 130: Die dicke Schulter, auf der das äußere Lager aufliegt
schulter_durchlass = Part.makeCylinder(38.0 / 2.0, 10.0)
schulter_durchlass.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke - 10.0))
gehaeuse = gehaeuse.cut(schulter_durchlass)

# 3. NEU: Leichtbau-Taschen von UNTEN! (Z=120 bis 143)
# Spart massiv Material, lässt aber ein 2mm starkes geschlossenes Dach (Regenschirm) stehen!
for i in range(6):
    angle = math.radians(i * 60 + 30) 
    x = 75.0 * math.cos(angle)
    y = 75.0 * math.sin(angle)
    # Lochradius 22mm, Höhe 23mm (bis Z=143). Bleibt 2mm Dach bis Z=145!
    loch = Part.makeCylinder(22.0, 23.0).translate(App.Vector(x, y, 120.0))
    gehaeuse = gehaeuse.cut(loch)

# 4. Z=54.4 bis 120: Oberer Rotor & Freiraum (65.6mm Höhe)
r_o_cyl = Part.makeCylinder(92.0, 65.6).translate(App.Vector(0, 0, 54.4))
r_o_box = Part.makeBox(184.0, 140.0, 65.6).translate(App.Vector(-92.0, -140.0, 54.4))
gehaeuse = gehaeuse.cut(r_o_cyl).cut(r_o_box)

# 5. Z=46 bis 54.4: Stator-Schlitten Slot (8.4mm dick)
s_cyl = Part.makeCylinder(100.0, 8.4).translate(App.Vector(0,0,46.0))
s_box = Part.makeBox(200.0, 140.0, 8.4).translate(App.Vector(-100.0, -140.0, 46.0))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

# 6. Z=16 bis 46: Unterer Rotor Freiraum (30.0mm Höhe)
r_u_cyl = Part.makeCylinder(92.0, 30.0).translate(App.Vector(0,0,16.0))
r_u_box = Part.makeBox(184.0, 140.0, 30.0).translate(App.Vector(-92.0, -140.0, 16.0))
gehaeuse = gehaeuse.cut(r_u_cyl).cut(r_u_box)

# 7. Z=0 bis 16: Slot für den modularen Boden-Schlitten
b_cyl = Part.makeCylinder(100.0, 16.0).translate(App.Vector(0,0,0))
b_box = Part.makeBox(200.0, 140.0, 16.0).translate(App.Vector(-100.0, -140.0, 0))
gehaeuse = gehaeuse.cut(b_cyl).cut(b_box)

# 8. Die 3 Flansch-Pads 
for angle in [0, 90, 180]:
    pad = Part.makeBox(15.0, 40.0, 90.0).translate(App.Vector(102.0, -20.0, 25.0))
    pad.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    gehaeuse = gehaeuse.fuse(pad)
    
    for dy in [-12, 12]:
        for dz in [40, 100]: 
            loch = Part.makeCylinder(3.4 / 2.0, 20.0)
            loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            loch.translate(App.Vector(95.0, dy, dz))
            loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            gehaeuse = gehaeuse.cut(loch)
            
            insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
            insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            insert.translate(App.Vector(117.0 - einschmelzmutter_t, dy, dz))
            insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            gehaeuse = gehaeuse.cut(insert)

gehaeuse = gehaeuse.removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse_XXL")


# ==========================================
# BAUTEIL 2: DER WAND-FLANSCH 
# ==========================================
bracket_w = 40.0
bracket_h = 110.0 
bracket_d = 50.0
wall_thick = 6.0

b_vert = Part.makeBox(wall_thick, bracket_w, bracket_h).translate(App.Vector(0, -bracket_w/2.0, 0))
b_horiz = Part.makeBox(bracket_d, bracket_w, wall_thick).translate(App.Vector(0, -bracket_w/2.0, 0))
bracket = b_vert.fuse(b_horiz)

p1 = App.Vector(wall_thick, -bracket_w/2.0, wall_thick)
p2 = App.Vector(bracket_d, -bracket_w/2.0, wall_thick)
p3 = App.Vector(wall_thick, -bracket_w/2.0, bracket_h)
tri1 = Part.Face(Part.Wire(Part.makePolygon([p1, p2, p3, p1]))).extrude(App.Vector(0, 4.0, 0))

p1_2 = App.Vector(wall_thick, bracket_w/2.0 - 4.0, wall_thick)
p2_2 = App.Vector(bracket_d, bracket_w/2.0 - 4.0, wall_thick)
p3_2 = App.Vector(wall_thick, bracket_w/2.0 - 4.0, bracket_h)
tri2 = Part.Face(Part.Wire(Part.makePolygon([p1_2, p2_2, p3_2, p1_2]))).extrude(App.Vector(0, 4.0, 0))

bracket = bracket.fuse(tri1).fuse(tri2)

for dy in [-12, 12]:
    for dz in [15, 75]: 
        loch = Part.makeCylinder(3.4 / 2.0, wall_thick + 2)
        loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        loch.translate(App.Vector(-1.0, dy, dz))
        senk = Part.makeCone(6.0/2.0, 3.4/2.0, 2.0)
        senk.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        senk.translate(App.Vector(0, dy, dz))
        bracket = bracket.cut(loch).cut(senk)

for dy in [-10, 10]:
    loch = Part.makeCylinder(5.5 / 2.0, wall_thick + 2).translate(App.Vector(bracket_d - 12.0, dy, -1))
    senk = Part.makeCone(10.0/2.0, 5.5/2.0, 3.0).translate(App.Vector(bracket_d - 12.0, dy, wall_thick - 3.0))
    bracket = bracket.cut(loch).cut(senk)

bracket = bracket.removeSplitter()
bracket.translate(App.Vector(-150, 0, 0)) 
show_obj(bracket, "Wand_Flansch")


# ==========================================
# BAUTEIL 3: NEUER MODULARER BODEN-SCHLITTEN (Skelettiert)
# ==========================================
bs_rad = 99.0 
bs_thick = 16.0

bs_back = Part.makeCylinder(bs_rad, bs_thick)
bs_front = Part.makeBox(bs_rad*2, 140.0, bs_thick).translate(App.Vector(-bs_rad, -140.0, 0))
boden_schlitten = bs_back.fuse(bs_front)
bs_griff = Part.makeBox(50.0, 20.0, bs_thick).translate(App.Vector(-25.0, -160.0, 0))
boden_schlitten = boden_schlitten.fuse(bs_griff)

# Lagersitz
boden_lager_sitz = Part.makeCylinder(47.4 / 2.0, 15.0).translate(App.Vector(0,0, 1.0))
boden_schlitten = boden_schlitten.cut(boden_lager_sitz)

# Lippe
boden_lippe = Part.makeCylinder(38.0 / 2.0, bs_thick)
boden_schlitten = boden_schlitten.cut(boden_lippe)

# Leichtbau für den fetten Bodenschlitten (6 x 22mm Löcher)
for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 64.0 * math.cos(angle)
    y = 64.0 * math.sin(angle)
    loch = Part.makeCylinder(22.0, bs_thick).translate(App.Vector(x, y, 0))
    boden_schlitten = boden_schlitten.cut(loch)

boden_schlitten = boden_schlitten.removeSplitter()
boden_schlitten.translate(App.Vector(0, -fuss_radius * 2.3, 0)) 
show_obj(boden_schlitten, "Boden_Schlitten_XXL")


# ==========================================
# BAUTEIL 4: DER UNIVERSAL-LAGER-ADAPTER 
# ==========================================
adapter = Part.makeCylinder(24.8 / 2.0, 15.0) 
kragen_fase = Part.makeCone(24.8 / 2.0, 34.0 / 2.0, 4.6).translate(App.Vector(0,0, 15.0))
kragen_gerade = Part.makeCylinder(34.0 / 2.0, 12.0).translate(App.Vector(0,0, 19.6))
adapter = adapter.fuse(kragen_fase).fuse(kragen_gerade)

hex_plug = make_hex_prism(hex_radius, 8.0).translate(App.Vector(0,0, 31.6))
adapter = adapter.fuse(hex_plug)

achse_cut = make_square_prism(achse_kantenlaenge + 0.5, 42.0).translate(App.Vector(0,0, -1.0))
adapter = adapter.cut(achse_cut)

z_loch = 19.6 + 6.0 
for i in range(4):
    angle = i * 90
    m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_loch.translate(App.Vector(0, 0, z_loch))
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_insert.translate(App.Vector((34.0 / 2.0) - einschmelzmutter_t, 0, z_loch))
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    adapter = adapter.cut(m3_loch).cut(m3_insert)

adapter = adapter.removeSplitter()
adapter.translate(App.Vector(fuss_radius * 2.2, 0, 0)) 
show_obj(adapter, "Universal_Lager_Adapter")


# ==========================================
# BAUTEIL 5: FLACHE START-SCHEIBE (High-Tech Skelettiert!)
# ==========================================
# BAUTEIL 5: FLACHE START-SCHEIBE (High-Tech Skelettiert & Wasserdicht!)
# ==========================================
kappen_radius_scheibe = blatt_radius - versatz + blatt_radius + 5.0 
scheibe = Part.makeCylinder(kappen_radius_scheibe, kappen_dicke)

hex_cut = make_hex_prism(hex_radius + 0.2, kappen_dicke)
scheibe = scheibe.cut(hex_cut)

# NEU: Leichtbau-Taschen von UNTEN! (Wasserdichter Regenschirm)
# Die Kappe ist 8mm dick. Wir fräsen von unten 6mm tief, 
# sodass oben ein 2mm dickes, geschlossenes Dach stehen bleibt.
for i in range(6):
    angle = math.radians(i * 60)
    x = 75.0 * math.cos(angle)
    y = 75.0 * math.sin(angle)
    # Lochradius 36mm, Tiefe 6mm
    loch = Part.makeCylinder(36.0, 6.0).translate(App.Vector(x, y, 0))
    scheibe = scheibe.cut(loch)

# Die Blade-Cuts an der Unterseite (Z=3 bis 8)
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

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")