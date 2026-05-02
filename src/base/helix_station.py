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
# 🔥 GEHÄUSE-HÖHE: EXTREM FLACHE 68.0 mm
# ==========================================
gehaeuse_h = 68.0         
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
# BAUTEIL 1: DAS XXL GEHÄUSE (ECHTES U-SHAPE)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# Innenkammer (Radius 96mm -> Perfekte 2mm Luft für den 94mm Rotor!)
inner_chamber = Part.makeCylinder(96.0, gehaeuse_h + 2.0).translate(App.Vector(0,0,-1.0))
gehaeuse = gehaeuse.cut(inner_chamber)

# 🔥 DAS OFFENE U-SHAPE (Z=0 bis Z=68) 
# Front wird auf exakt 213mm Breite geöffnet (X=±106.5)
front_opening = Part.makeBox(213.0, 150.0, gehaeuse_h + 2.0).translate(App.Vector(-106.5, -150.0, -1.0))
gehaeuse = gehaeuse.cut(front_opening)

# STATOR SCHLITZ IM GEHÄUSE (Z=25.8 bis Z=35.3 — 9.5mm = stator_dicke 9mm + 0.5mm Gleitspiel)
s_cyl = Part.makeCylinder(99.5, 9.5).translate(App.Vector(0,0,25.8))
s_box = Part.makeBox(200.0, 140.0, 9.5).translate(App.Vector(-100.0, -140.0, 25.8))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

# 🔥 WAND-FLANSCH PADS (Alle drei Pads schließen nun bündig auf 121.5mm ab!)
pad_r = Part.makeBox(15.0, 50.0, gehaeuse_h).translate(App.Vector(106.5, -25.0, 0)) 
pad_l = Part.makeBox(15.0, 50.0, gehaeuse_h).translate(App.Vector(-121.5, -25.0, 0)) 
# HINTERER KLOTZ: Gekürzt auf 21.5mm Tiefe -> Startet bei 100.0 und endet bündig bei 121.5!
pad_b = Part.makeBox(50.0, 21.5, gehaeuse_h).translate(App.Vector(-25.0, 100.0, 0)) 
gehaeuse = gehaeuse.fuse(pad_r).fuse(pad_l).fuse(pad_b)

# 4x M3 Bohrungen pro Pad (Sauber von der geraden Außenfläche nach innen!)
for dy in [-12, 12]:
    for dz in [15.0, 53.0]: 
        # Rechts (Pad R - Außenkante bei X=121.5)
        loch_r = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(125.0, dy, dz))
        insert_r = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(121.5, dy, dz))
        gehaeuse = gehaeuse.cut(loch_r).cut(insert_r)
        
        # Links (Pad L - Außenkante bei X=-121.5)
        loch_l = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-125.0, dy, dz))
        insert_l = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-121.5, dy, dz))
        gehaeuse = gehaeuse.cut(loch_l).cut(insert_l)

for dx in [-12, 12]:
    for dz in [15.0, 53.0]:
        # Hinten (Pad B - Außenkante bei Y=121.5)
        loch_b = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90).translate(App.Vector(dx, 121.5, dz))
        insert_b = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90).translate(App.Vector(dx, 121.5, dz))
        gehaeuse = gehaeuse.cut(loch_b).cut(insert_b)

# 🔥 DECKEL-VERSCHRAUBUNG FÜR DAS GEHÄUSE (15° Shift + Radius 104mm)
for i in range(12):
    angle_d = math.radians(i * 30 + 15) 
    x = 104.0 * math.cos(angle_d)
    y = 104.0 * math.sin(angle_d)
    
    # Loch gehört zum Gehäuse, wenn es Y > 0 ist
    if y >= 0: 
        if i % 2 == 0: 
            insert_t = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, gehaeuse_h - einschmelzmutter_t))
            freiraum_t = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, gehaeuse_h - 10.0))
            gehaeuse = gehaeuse.cut(insert_t).cut(freiraum_t)
        else: 
            insert_b = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, 0))
            freiraum_b = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, 0))
            gehaeuse = gehaeuse.cut(insert_b).cut(freiraum_b)

# 🔥 HORIZONTALE VERSCHRAUBUNG FÜR DIE KLAPPE (Nur noch EINE mittige Schraube!)
# Sitzt nun mittig bei Z=34.0 und bei Y=-20.0 (weit weg von den Flansch-Löchern!)
for z_pos in [34.0]:
    # Rechts
    loch_r = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(121.5, -20.0, z_pos))
    senk_r = Part.makeCylinder(6.4 / 2.0, 5.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(121.5, -20.0, z_pos))
    gehaeuse = gehaeuse.cut(loch_r).cut(senk_r)
    # Links
    loch_l = Part.makeCylinder(3.4 / 2.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-121.5, -20.0, z_pos))
    senk_l = Part.makeCylinder(6.4 / 2.0, 5.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-121.5, -20.0, z_pos))
    gehaeuse = gehaeuse.cut(loch_l).cut(senk_l)

gehaeuse = gehaeuse.removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse_XXL")


# ==========================================
# BAUTEIL 2: DIE MASSIVE WARTUNGSKLAPPE (OHNE SCHLITZE)
# ==========================================
hatch_vol = Part.makeBox(213.0, 150.0, gehaeuse_h).translate(App.Vector(-106.5, -150.0, 0))
missing_cyl = Part.makeCylinder(110.0, gehaeuse_h).common(hatch_vol)

bp_out = Part.makeBox(213.0, 130.0, gehaeuse_h).translate(App.Vector(-106.5, -150.0, 0))
klappe = missing_cyl.fuse(bp_out)

# CAVITY: Lässt 6mm dicke Wände an den Seiten und ein 6mm Dach stehen!
cavity = Part.makeBox(201.0, 145.0, gehaeuse_h - 6.0).translate(App.Vector(-100.5, -145.0, -1.0))
klappe = klappe.cut(cavity)

# STATOR SCHLITZ IM ARM (9.5mm = stator_dicke 9mm + 0.5mm Gleitspiel)
stator_slot = Part.makeBox(199.0, 120.0, 9.5).translate(App.Vector(-99.5, -120.0, 25.8))
klappe = klappe.cut(stator_slot)

# Rotor Freilauf schneiden
klappe = klappe.cut(Part.makeCylinder(96.0, gehaeuse_h + 2.0).translate(App.Vector(0,0,-1.0)))

# Horizontale Einschmelzmuttern für die Verriegelung (EINE mittige Schraube!)
for z_pos in [34.0]:
    insert_r = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(106.5, -20.0, z_pos))
    insert_l = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-106.5, -20.0, z_pos))
    klappe = klappe.cut(insert_r).cut(insert_l)

# TOP DECKEL INSERTS (Landen zu 100% sicher im 6mm dicken Dach der Klappe!)
for i in range(12):
    angle_d = math.radians(i * 30 + 15)
    x = 104.0 * math.cos(angle_d)
    y = 104.0 * math.sin(angle_d)
    
    if y < 0: 
        if i % 2 == 0: 
            insert_t = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, gehaeuse_h - einschmelzmutter_t))
            freiraum_t = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, gehaeuse_h - 10.0))
            klappe = klappe.cut(insert_t).cut(freiraum_t)

# PCB Standoffs an der Innenseite der Rückwand
for dx in [-25.0, 25.0]:
    for dz in [20.0, 50.0]:
        standoff = Part.makeCylinder(4.0, 5.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(dx, -145.0, dz))
        loch = Part.makeCylinder(1.4, 6.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(dx, -146.0, dz))
        klappe = klappe.fuse(standoff).cut(loch)

kabel_loch = Part.makeCylinder(5.0, 20.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90).translate(App.Vector(0, -135.0, 10.0))
klappe = klappe.cut(kabel_loch)

# TABS FÜR BODENPLATTE
tab_positions = [(-94.0, -135.0), (94.0, -135.0), (-94.0, -50.0), (94.0, -50.0)]
for tx, ty in tab_positions:
    tab = Part.makeBox(12.0, 12.0, 8.0).translate(App.Vector(tx - 6.0, ty - 6.0, 0))
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(tx, ty, 0))
    loch = Part.makeCylinder(3.4 / 2.0, 12.0).translate(App.Vector(tx, ty, -1.0))
    tab = tab.cut(insert).cut(loch)
    klappe = klappe.fuse(tab)

klappe = klappe.removeSplitter()
klappe.translate(App.Vector(0, -60.0, 0)) 
show_obj(klappe, "Elektronik_Wartungs_Klappe")


# ==========================================
# BAUTEIL 3: WARTUNGSKLAPPEN-BODEN 
# ==========================================
boden_vol = Part.makeBox(213.0, 150.0, 6.0).translate(App.Vector(-106.5, -150.0, 0))
boden_cyl = Part.makeCylinder(110.0, 6.0).common(boden_vol)
boden_bp = Part.makeBox(213.0, 130.0, 6.0).translate(App.Vector(-106.5, -150.0, 0))
boden = boden_cyl.fuse(boden_bp)

rotor_cut = Part.makeCylinder(96.0, 10.0).translate(App.Vector(0,0,-1.0))
boden = boden.cut(rotor_cut)

# BOTTOM DECKEL INSERTS
for i in range(12):
    angle_d = math.radians(i * 30 + 15)
    x = 104.0 * math.cos(angle_d)
    y = 104.0 * math.sin(angle_d)
    
    if y < 0: 
        if i % 2 != 0: 
            insert_b = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, 6.0 - einschmelzmutter_t))
            freiraum_b = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, -1.0))
            boden = boden.cut(insert_b).cut(freiraum_b)

# Verschraubungslöcher für die 4 Tabs
for tx, ty in tab_positions:
    loch = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(tx, ty, -1.0))
    senk = Part.makeCone(6.4 / 2.0, 3.4 / 2.0, 2.0).translate(App.Vector(tx, ty, 0))
    boden = boden.cut(loch).cut(senk)

boden = boden.removeSplitter()
boden.translate(App.Vector(0, -60.0, -30.0)) 
show_obj(boden, "Wartungsklappen_Boden")


# ==========================================
# BAUTEIL 4: DER FLACHE STACKING-DECKEL 
# ==========================================
deckel_base = Part.makeCylinder(fuss_radius, deckel_h)

fuehrung_u = Part.makeCylinder(95.5, 6.0).cut(Part.makeCylinder(85.0, 6.0)).translate(App.Vector(0, 0, -6.0))
lippe_u = Part.makeCylinder(fuss_radius, 4.0).cut(Part.makeCylinder(96.0, 4.0)).translate(App.Vector(0, 0, -4.0))

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

# DECKEL LÖCHER (Radius 104.0, 15° Shift)
for i in range(12):
    angle_d = math.radians(i * 30 + 15)
    xd = 104.0 * math.cos(angle_d)
    yd = 104.0 * math.sin(angle_d)
    
    if i % 2 == 0: 
        loch_d = Part.makeCylinder(3.4 / 2.0, deckel_h + 10.0).translate(App.Vector(xd, yd, -6.0))
        kopf_d = Part.makeCylinder(6.4 / 2.0, 10.0).translate(App.Vector(xd, yd, 8.0)) 
        deckel = deckel.cut(loch_d).cut(kopf_d)
    else:          
        loch_u = Part.makeCylinder(3.4 / 2.0, deckel_h + 10.0).translate(App.Vector(xd, yd, -6.0))
        kopf_u = Part.makeCylinder(6.4 / 2.0, 8.0).translate(App.Vector(xd, yd, 0.0)) 
        deckel = deckel.cut(loch_u).cut(kopf_u)

deckel = deckel.removeSplitter()
deckel.translate(App.Vector(0, 0, gehaeuse_h + 30.0)) 
show_obj(deckel, "Stacking_Lager_Deckel_FLACH")


# ==========================================
# BAUTEIL 5: DER WAND-FLANSCH 
# ==========================================
bracket_w = 40.0
bracket_h = gehaeuse_h 
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
    for dz in [15.0, 53.0]: 
        loch = Part.makeCylinder(3.4 / 2.0, wall_thick + 2).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(-1.0, dy, dz))
        senk = Part.makeCone(6.0/2.0, 3.4/2.0, 2.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90).translate(App.Vector(0, dy, dz))
        bracket = bracket.cut(loch).cut(senk)

for dy in [-10, 10]:
    loch = Part.makeCylinder(5.5 / 2.0, wall_thick + 2).translate(App.Vector(bracket_d - 12.0, dy, -1))
    senk = Part.makeCone(10.0/2.0, 5.5/2.0, 3.0).translate(App.Vector(bracket_d - 12.0, dy, wall_thick - 3.0))
    bracket = bracket.cut(loch).cut(senk)

bracket = bracket.removeSplitter()
bracket.translate(App.Vector(-160, 0, 0)) 
show_obj(bracket, "Wand_Flansch")


# ==========================================
# BAUTEIL 6: ERSATZ LAGERSCHALE (3D-Druck Dummy)
# ==========================================
# Da dir die äußere Metallschale (Cup) fehlt, drucken wir sie einfach!
# Außen exakt 50mm für deine Deckel-Aufnahme, innen konisch für die Kegelrollen.
def make_ersatz_lagerschale():
    schale_h = 12.0 # Typische Höhe der Schale bei diesen Lagern
    schale = Part.makeCylinder(lager_aussen_d / 2.0, schale_h)
    
    # Konischer Innenschnitt für die schrägen Kegelrollen
    # Unten enger (R=19.5), oben weiter (R=23.0) -> Passt sich den Rollen an
    r_unten = (lager_aussen_d / 2.0) - 5.5 
    r_oben = (lager_aussen_d / 2.0) - 2.0  
    innen_kegel = Part.makeCone(r_unten, r_oben, schale_h)
    
    schale = schale.cut(innen_kegel)

    return schale.removeSplitter()

ersatz_schale = make_ersatz_lagerschale()
ersatz_schale.translate(App.Vector(150, -100, 0))
show_obj(ersatz_schale, "Ersatz_Lagerschale_32005")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")