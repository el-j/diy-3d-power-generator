import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station_XXL")

# ==========================================
# ⚙️ PARAMETER FÜR DIE XXL BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

lager_innen_d = 29.0      
lager_aussen_d = 50.0     
lager_dicke = 15.0        
lager_toleranz = 0.2      
adapter_pressfit = 0.15   

# ==========================================
# 🔥 GEHÄUSE-HÖHE OPTIMIERT FÜR PLA-CF
# 76.0 mm Gesamthöhe (Gibt oben und unten +2.5mm Warping-Toleranz)
# ==========================================
gehaeuse_h = 76.0         
fuss_radius = 110.0       
deckel_h = 18.0           

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
# BAUTEIL 1: DER XXL MASCHINEN-FUSS 
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# Achsen-Freilauf (Damit Clamps und Achse nicht reiben)
clearance_hole = Part.makeCylinder(22.0, gehaeuse_h + 2).translate(App.Vector(0,0,-1))
gehaeuse = gehaeuse.cut(clearance_hole)

# OBERE KAMMER (+2.5mm Toleranz -> Startet bei Z=52.0mm, Höhe=24.0mm)
r_o_cyl = Part.makeCylinder(102.0, 24.0).translate(App.Vector(0, 0, 52.0))
r_o_box = Part.makeBox(204.0, 140.0, 24.0).translate(App.Vector(-102.0, -140.0, 52.0))
gehaeuse = gehaeuse.cut(r_o_cyl).cut(r_o_box)

# STATOR SCHLITZ (9.0mm Dicke, Startet exakt bei Z=43.0mm)
s_cyl = Part.makeCylinder(102.0, 9.0).translate(App.Vector(0,0,43.0))
s_box = Part.makeBox(204.0, 140.0, 9.0).translate(App.Vector(-102.0, -140.0, 43.0))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

# UNTERE KAMMER (+2.5mm Toleranz -> Startet bei Z=16.0mm, Höhe=27.0mm)
r_u_cyl = Part.makeCylinder(102.0, 27.0).translate(App.Vector(0,0,16.0))
r_u_box = Part.makeBox(204.0, 140.0, 27.0).translate(App.Vector(-102.0, -140.0, 16.0))
gehaeuse = gehaeuse.cut(r_u_cyl).cut(r_u_box)

# MASSIVER BODEN (Z=0 bis 16)
b_cyl = Part.makeCylinder(100.0, 16.0).translate(App.Vector(0,0,0))
b_box = Part.makeBox(200.0, 140.0, 16.0).translate(App.Vector(-100.0, -140.0, 0))
gehaeuse = gehaeuse.cut(b_cyl).cut(b_box)

# Seitliche Verstärkungspads (Angepasst auf 76mm Höhe)
for angle in [0, 90, 180]:
    pad = Part.makeBox(15.0, 40.0, gehaeuse_h - 16.0).translate(App.Vector(102.0, -20.0, 16.0))
    pad.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    gehaeuse = gehaeuse.fuse(pad)
    
    for dy in [-12, 12]:
        for dz in [25.0, 60.0]: # Schraubenlöcher mitgewachsen
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

# M3 Gewindeeinsätze für den Deckel 
for i in range(6):
    angle = math.radians(i * 60)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, gehaeuse_h - einschmelzmutter_t))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, gehaeuse_h - 10.0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# M3 Gewindeeinsätze für Stacking (Unten)
for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, 0))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, 0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# M3 Gewindeeinsätze für die Wasserdichte Bodenwanne
for i in range(4):
    angle_deg = i * 90 + 45
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t + 2.0)
    insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    insert.translate(App.Vector(fuss_radius - einschmelzmutter_t, 0, 20.0))
    insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    gehaeuse = gehaeuse.cut(insert)

# M3 Verschraubung für die Elektronik-Wartungsklappe
for z_pos in [20.0, 65.0]: # Schraubenlöcher mitgewachsen
    for x_pos in [-96.0, 96.0]:
        notch = Part.makeBox(16.0, 30.0, 16.0).translate(App.Vector(x_pos - 8.0, -70.0, z_pos - 8.0))
        gehaeuse = gehaeuse.cut(notch)
        
        insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
        insert.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        insert.translate(App.Vector(x_pos, -40.0, z_pos))
        
        loch = Part.makeCylinder(3.4 / 2.0, 20.0)
        loch.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        loch.translate(App.Vector(x_pos, -40.0, z_pos))
        
        gehaeuse = gehaeuse.cut(insert).cut(loch)

gehaeuse = gehaeuse.removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse_XXL")


# ==========================================
# BAUTEIL 2: DER FLACHE STACKING-DECKEL 
# ==========================================
deckel_base = Part.makeCylinder(fuss_radius + 3.0, deckel_h)

# Innere Führung an den 102mm Kammer-Radius angepasst
fuehrung_u = Part.makeCylinder(101.5, 6.0).cut(Part.makeCylinder(95.0, 6.0)).translate(App.Vector(0, 0, -6.0))
lippe_u = Part.makeCylinder(fuss_radius + 3.0, 4.0).cut(Part.makeCylinder(fuss_radius + 0.6, 4.0)).translate(App.Vector(0, 0, -4.0))

deckel = deckel_base.fuse(fuehrung_u).fuse(lippe_u)

lager_tasche = Part.makeCylinder((lager_aussen_d + lager_toleranz) / 2.0, lager_dicke).translate(App.Vector(0, 0, deckel_h - lager_dicke))
deckel = deckel.cut(lager_tasche)

schulter = Part.makeCylinder(38.0 / 2.0, deckel_h + 10.0).translate(App.Vector(0, 0, -6.0))
deckel = deckel.cut(schulter)

for i in range(6):
    angle = math.radians(i * 60 + 15) 
    x = 70.0 * math.cos(angle)
    y = 70.0 * math.sin(angle)
    loch_unten = Part.makeCylinder(20.0, 22.0).translate(App.Vector(x, y, -6.0))
    deckel = deckel.cut(loch_unten)

for i in range(6):
    angle_d = math.radians(i * 60)
    xd = 105.0 * math.cos(angle_d)
    yd = 105.0 * math.sin(angle_d)
    loch_d = Part.makeCylinder(3.4 / 2.0, deckel_h + 10.0).translate(App.Vector(xd, yd, -6.0))
    kopf_d = Part.makeCylinder(6.4 / 2.0, 10.0).translate(App.Vector(xd, yd, 8.0)) 
    deckel = deckel.cut(loch_d).cut(kopf_d)
    
    angle_u = math.radians(i * 60 + 30)
    xu = 105.0 * math.cos(angle_u)
    yu = 105.0 * math.sin(angle_u)
    loch_u = Part.makeCylinder(3.4 / 2.0, deckel_h + 10.0).translate(App.Vector(xu, yu, -6.0))
    kopf_u = Part.makeCylinder(6.4 / 2.0, 8.0).translate(App.Vector(xu, yu, 0.0)) 
    deckel = deckel.cut(loch_u).cut(kopf_u)

deckel = deckel.removeSplitter()
deckel.translate(App.Vector(0, 0, gehaeuse_h + 30.0)) 
show_obj(deckel, "Stacking_Lager_Deckel_FLACH")


# ==========================================
# BAUTEIL 3: DER WAND-FLANSCH (Flacher für Base)
# ==========================================
bracket_w = 40.0
bracket_h = 70.0 
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
    for dz in [15, 55]: 
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
# BAUTEIL 4: MODULARER BODEN-SCHLITTEN 
# ==========================================
bs_rad = 99.0 
bs_thick = 16.0

bs_back = Part.makeCylinder(bs_rad, bs_thick)
bs_front = Part.makeBox(bs_rad*2, 140.0, bs_thick).translate(App.Vector(-bs_rad, -140.0, 0))
boden_schlitten = bs_back.fuse(bs_front)
bs_griff = Part.makeBox(50.0, 20.0, bs_thick).translate(App.Vector(-25.0, -160.0, 0))
boden_schlitten = boden_schlitten.fuse(bs_griff)

boden_lager_sitz = Part.makeCylinder((lager_aussen_d + lager_toleranz) / 2.0, 15.0).translate(App.Vector(0,0, 1.0))
boden_schlitten = boden_schlitten.cut(boden_lager_sitz)

boden_lippe = Part.makeCylinder(38.0 / 2.0, bs_thick)
boden_schlitten = boden_schlitten.cut(boden_lippe)

for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 64.0 * math.cos(angle)
    y = 64.0 * math.sin(angle)
    loch = Part.makeCylinder(22.0, 14.0).translate(App.Vector(x, y, 0))
    boden_schlitten = boden_schlitten.cut(loch)

boden_schlitten = boden_schlitten.removeSplitter()
boden_schlitten.translate(App.Vector(0, -fuss_radius * 2.3, 0)) 
show_obj(boden_schlitten, "Boden_Schlitten_XXL")


# ==========================================
# BAUTEIL 5: FLACHE START-SCHEIBE 
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
scheibe.translate(App.Vector(0, fuss_radius * 2.8, 0)) 
show_obj(scheibe, "Start_Scheibe_FLACH")


# ==========================================
# BAUTEIL 6: BODEN-WANNE WASSERDICHT 
# ==========================================
wanne_h_out = 28.0 
wanne_base = Part.makeCylinder(fuss_radius + 3.0, wanne_h_out)
wanne_base.translate(App.Vector(0,0,-4.0))

wanne_in = Part.makeCylinder(fuss_radius + 0.6, 24.0)
wanne = wanne_base.cut(wanne_in)

achse_freiraum = Part.makeCylinder(12.0, 3.0).translate(App.Vector(0,0,-3.0))
wanne = wanne.cut(achse_freiraum)

for i in range(4):
    angle_deg = i * 90 + 45
    loch = Part.makeCylinder(3.4 / 2.0, 10.0)
    loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    loch.translate(App.Vector(fuss_radius - 2.0, 0, 20.0))
    loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    
    senk = Part.makeCone(3.4/2.0, 6.4/2.0, 2.0)
    senk.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    senk.translate(App.Vector(fuss_radius + 1.0, 0, 20.0))
    senk.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    
    wanne = wanne.cut(loch).cut(senk)

wanne = wanne.removeSplitter()
wanne.translate(App.Vector(0, 0, -50.0)) 
show_obj(wanne, "Boden_Wanne_Wasserdicht")


# ==========================================
# BAUTEIL 7: ELEKTRONIK WARTUNGS-KLAPPE 
# ==========================================
# Klappe wächst mit (60.0mm Höhe)
hatch_h = gehaeuse_h - 16.0
c_out = Part.makeCylinder(110.0, hatch_h).translate(App.Vector(0, 0, 16.0))
c_in = Part.makeCylinder(106.0, hatch_h).translate(App.Vector(0, 0, 16.0))
shield = c_out.cut(c_in)

b1 = Part.makeBox(230.0, 230.0, 150.0).translate(App.Vector(-115.0, 0, 0))
b2 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(91.5, -115.0, 0))
b3 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(-201.5, -115.0, 0))
shield = shield.cut(b1).cut(b2).cut(b3)

for z_pos in [20.0, 65.0]:
    for x_pos in [-96.0, 96.0]:
        tab = Part.makeBox(16.0, 18.0, 16.0).translate(App.Vector(x_pos - 8.0, -58.0, z_pos - 8.0))
        
        loch = Part.makeCylinder(3.4 / 2.0, 20.0)
        loch.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        loch.translate(App.Vector(x_pos, -60.0, z_pos))
        
        kopf = Part.makeCylinder(6.4 / 2.0, 15.0)
        kopf.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        kopf.translate(App.Vector(x_pos, -65.0, z_pos))
        
        tab = tab.cut(loch).cut(kopf)
        shield = shield.fuse(tab)

bp_out = Part.makeBox(80.0, 70.0, hatch_h).translate(App.Vector(-40.0, -170.0, 16.0))
bp_in = Part.makeBox(72.0, 65.0, hatch_h - 4.0).translate(App.Vector(-36.0, -165.0, 18.0))
backpack = bp_out.cut(bp_in)

durchbruch = Part.makeBox(72.0, 30.0, hatch_h - 4.0).translate(App.Vector(-36.0, -120.0, 18.0))
shield = shield.cut(durchbruch)
klappe = shield.fuse(backpack)

for dx in [-25.0, 25.0]:
    for dz in [25.0, 60.0]:
        standoff = Part.makeCylinder(4.0, 5.0)
        standoff.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        standoff.translate(App.Vector(dx, -165.0, dz))
        
        loch = Part.makeCylinder(1.4, 6.0)
        loch.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        loch.translate(App.Vector(dx, -166.0, dz))
        klappe = klappe.fuse(standoff).cut(loch)

kabel_loch = Part.makeCylinder(4.0, 10.0).translate(App.Vector(0, -135.0, 10.0))
klappe = klappe.cut(kabel_loch)

klappe = klappe.removeSplitter()
klappe.translate(App.Vector(0, -80.0, 0)) 
show_obj(klappe, "Elektronik_Wartungs_Klappe")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")