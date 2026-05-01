import FreeCAD as App
import Part
import math

doc = App.newDocument("Helix_Base_Station_XXL")

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
# 🔥 GEHÄUSE-HÖHE: EXAKT 76.0 mm
# Ergibt exakt 5.0 mm "Warping"-Freiraum 
# über und unter den Rotoren!
# ==========================================
gehaeuse_h = 76.0         
fuss_radius = 110.0       
deckel_h = 18.0           

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0  
# ==========================================

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DAS XXL GEHÄUSE-ROHR 
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# 🔥 OBERE KAMMER (Radius 93mm -> Perfekter Freiraum für 90mm Rotor)
# Geht von Z=46.5 bis Z=76.0 (Höhe 29.5mm)
r_o_cyl = Part.makeCylinder(93.0, 29.5).translate(App.Vector(0, 0, 46.5))
r_o_box = Part.makeBox(186.0, 140.0, 29.5).translate(App.Vector(-93.0, -140.0, 46.5))
gehaeuse = gehaeuse.cut(r_o_cyl).cut(r_o_box)

# 🔥 STATOR SCHLITZ (Zentriert den Stack: Z=37.5 bis Z=46.5, Höhe=9.0mm)
# Schneidet 199mm breit, damit der 198mm Stator reinpasst!
s_cyl = Part.makeCylinder(99.5, 9.0).translate(App.Vector(0,0,37.5))
s_box = Part.makeBox(199.0, 140.0, 9.0).translate(App.Vector(-99.5, -140.0, 37.5))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

# 🔥 UNTERE KAMMER (Radius 93mm)
# Geht von Z=16.0 bis Z=37.5 (Höhe 21.5mm)
r_u_cyl = Part.makeCylinder(93.0, 21.5).translate(App.Vector(0,0,16.0))
r_u_box = Part.makeBox(186.0, 140.0, 21.5).translate(App.Vector(-93.0, -140.0, 16.0))
gehaeuse = gehaeuse.cut(r_u_cyl).cut(r_u_box)

# MASSIVER BODEN (Z=0 bis 16)
b_cyl = Part.makeCylinder(100.0, 16.0).translate(App.Vector(0,0,0))
b_box = Part.makeBox(200.0, 140.0, 16.0).translate(App.Vector(-100.0, -140.0, 0))
gehaeuse = gehaeuse.cut(b_cyl).cut(b_box)

# Seitliche Verstärkungspads (Für den Wandflansch)
for angle in [0, 90, 180]:
    pad = Part.makeBox(15.0, 40.0, gehaeuse_h).translate(App.Vector(102.0, -20.0, 0))
    pad.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    gehaeuse = gehaeuse.fuse(pad)
    
    for dy in [-12, 12]:
        for dz in [20.0, 55.0]: 
            loch = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(95.0, dy, dz)).rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(117.0 - einschmelzmutter_t, dy, dz)).rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            gehaeuse = gehaeuse.cut(loch).cut(insert)

# M3 Gewindeeinsätze für TOP DECKEL 
for i in range(6):
    angle = math.radians(i * 60)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, gehaeuse_h - einschmelzmutter_t))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, gehaeuse_h - 10.0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# M3 Gewindeeinsätze für BOTTOM DECKEL
for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, 0))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, 0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# 🔥 WARTUNGSKLAPPEN-AUFNAHME (Kollisionsfrei!)
# Die Schrauben sitzen bei Z=20.0 und Z=60.0 (weit weg vom 37.5er Stator!)
# Die X-Position liegt bei ±104.0 (weit außerhalb des 198mm Stators!)
for z_pos in [20.0, 60.0]: 
    for x_pos in [-104.0, 104.0]:
        # Tasche für den Tab der Klappe
        notch = Part.makeBox(10.0, 20.0, 18.0).translate(App.Vector(x_pos - 5.0, -50.0, z_pos - 9.0))
        gehaeuse = gehaeuse.cut(notch)
        
        insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(x_pos, -30.0, z_pos))
        loch = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(x_pos, -40.0, z_pos))
        gehaeuse = gehaeuse.cut(insert).cut(loch)

gehaeuse = gehaeuse.removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse_XXL")


# ==========================================
# BAUTEIL 2: DER FLACHE STACKING-DECKEL 
# ==========================================
deckel_base = Part.makeCylinder(fuss_radius + 3.0, deckel_h)

# Innere Führung passt exakt in die 93mm Kammer
fuehrung_u = Part.makeCylinder(92.5, 6.0).cut(Part.makeCylinder(85.0, 6.0)).translate(App.Vector(0, 0, -6.0))
lippe_u = Part.makeCylinder(fuss_radius + 3.0, 4.0).cut(Part.makeCylinder(fuss_radius + 0.6, 4.0)).translate(App.Vector(0, 0, -4.0))
deckel = deckel_base.fuse(fuehrung_u).fuse(lippe_u)

# Lager Tasche (15mm Tiefe für das fette 32005 Lager!)
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
# BAUTEIL 3: DER WAND-FLANSCH 
# ==========================================
bracket_w = 40.0
bracket_h = 76.0 
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
    for dz in [20.0, 55.0]: 
        loch = Part.makeCylinder(3.4 / 2.0, wall_thick + 2).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-1.0, dy, dz))
        senk = Part.makeCone(6.0/2.0, 3.4/2.0, 2.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(0, dy, dz))
        bracket = bracket.cut(loch).cut(senk)

for dy in [-10, 10]:
    loch = Part.makeCylinder(5.5 / 2.0, wall_thick + 2).translate(App.Vector(bracket_d - 12.0, dy, -1))
    senk = Part.makeCone(10.0/2.0, 5.5/2.0, 3.0).translate(App.Vector(bracket_d - 12.0, dy, wall_thick - 3.0))
    bracket = bracket.cut(loch).cut(senk)

bracket = bracket.removeSplitter()
bracket.translate(App.Vector(-150, 0, 0)) 
show_obj(bracket, "Wand_Flansch")


# ==========================================
# BAUTEIL 4: ELEKTRONIK WARTUNGS-KLAPPE 
# ==========================================
# Klappe wächst exakt mit dem Gehäuse mit (Z=0 bis Z=76)
hatch_h = gehaeuse_h
c_out = Part.makeCylinder(110.0, hatch_h)
c_in = Part.makeCylinder(106.0, hatch_h)
shield = c_out.cut(c_in)

# 🔥 KLAPPE VERBREITERT! Deckt jetzt alles bis X=±104.5 ab
b1 = Part.makeBox(230.0, 230.0, 150.0).translate(App.Vector(-115.0, 0, -10.0))
b2 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(104.5, -115.0, -10.0))
b3 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(-214.5, -115.0, -10.0))
shield = shield.cut(b1).cut(b2).cut(b3)

# Die neuen, nach außen gerückten Schraubpunkte (X=±104)
for z_pos in [20.0, 60.0]:
    for x_pos in [-104.0, 104.0]:
        tab = Part.makeBox(9.0, 15.0, 17.0).translate(App.Vector(x_pos - 4.5, -45.0, z_pos - 8.5))
        
        loch = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(x_pos, -50.0, z_pos))
        kopf = Part.makeCylinder(6.4 / 2.0, 10.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(x_pos, -55.0, z_pos))
        
        tab = tab.cut(loch).cut(kopf)
        shield = shield.fuse(tab)

# 🔥 OPTIMIERT FÜR UPSIDE-DOWN DRUCK:
# Boden komplett offen, Dach 3mm dick (Z=73 bis 76)
bp_out = Part.makeBox(80.0, 70.0, hatch_h).translate(App.Vector(-40.0, -170.0, 0))
bp_in = Part.makeBox(74.0, 66.0, hatch_h - 2.0).translate(App.Vector(-37.0, -166.0, -1.0))
backpack = bp_out.cut(bp_in)

# 🔥 Durchbruch öffnet die Wand nun ebenfalls komplett nach unten!
durchbruch = Part.makeBox(74.0, 30.0, hatch_h - 2.0).translate(App.Vector(-37.0, -120.0, -1.0))
shield = shield.cut(durchbruch)
klappe = shield.fuse(backpack)

# 🔥 NEU: Befestigungs-Blöcke für die Bodenplatte (In den 4 Ecken)
tab_positions = [(-34.0, -164.0), (34.0, -164.0), (-34.0, -112.0), (34.0, -112.0)]
for tx, ty in tab_positions:
    tab = Part.makeBox(12.0, 12.0, 8.0).translate(App.Vector(tx - 6.0, ty - 6.0, 0))
    # Einschmelzmutter von unten (Z=0)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(tx, ty, 0))
    loch = Part.makeCylinder(3.4 / 2.0, 15.0).translate(App.Vector(tx, ty, -1.0))
    tab = tab.cut(insert).cut(loch)
    klappe = klappe.fuse(tab)

for dx in [-25.0, 25.0]:
    for dz in [20.0, 55.0]:
        standoff = Part.makeCylinder(4.0, 5.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(dx, -165.0, dz))
        loch = Part.makeCylinder(1.4, 6.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(dx, -166.0, dz))
        klappe = klappe.fuse(standoff).cut(loch)

kabel_loch = Part.makeCylinder(4.0, 10.0).translate(App.Vector(0, -135.0, 10.0))
klappe = klappe.cut(kabel_loch)

klappe = klappe.removeSplitter()
klappe.translate(App.Vector(0, -80.0, 0)) 
show_obj(klappe, "Elektronik_Wartungs_Klappe")

# ==========================================
# BAUTEIL 5: WARTUNGSKLAPPEN-BODEN (Neu!)
# ==========================================
boden = Part.makeBox(80.0, 70.0, 3.0).translate(App.Vector(-40.0, -170.0, 0))
# Exakt an die Rundung des Hauptgehäuses anpassen
c_in_cut = Part.makeCylinder(106.0, 10.0).translate(App.Vector(0,0,-5.0))
boden = boden.cut(c_in_cut)

for tx, ty in tab_positions:
    loch = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(tx, ty, -1.0))
    # Versenkt für sauberen Abschluss der Schraubenköpfe von unten
    senk = Part.makeCone(6.4 / 2.0, 3.4 / 2.0, 2.0).translate(App.Vector(tx, ty, 0))
    boden = boden.cut(loch).cut(senk)

boden = boden.removeSplitter()
boden.translate(App.Vector(0, -160.0, 0)) 
show_obj(boden, "Wartungsklappen_Boden")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")