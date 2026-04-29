import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station_XXL")

# ==========================================
# ⚙️ PARAMETER FÜR DIE XXL BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# KRITISCHE ÄNDERUNG AUFGRUND REALER MESSUNG!
# Datenblatt: Lager 50mm außen. 29mm innen.
# Wir konstruieren für die Realität!
lager_innen_d = 29.0      
lager_aussen_d = 50.0     # REAL-MESSUNG ÜBERNIMMT!
lager_dicke = 15.0        
lager_toleranz = 0.2      # Ergibt 50.2mm CAD-Loch für das 50.0mm Lager.
adapter_pressfit = 0.15   # NEU: +0.15mm Übermaß für den "saftigen" Sitz im inneren Lagerring!

# MASSIVE GRÖSSEN!
fuss_radius = 110.0       
gehaeuse_h = 120.0        
deckel_h = 18.0           

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
# BAUTEIL 1: DER XXL MASCHINEN-FUSS (Basis)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

r_o_cyl = Part.makeCylinder(92.0, 65.6).translate(App.Vector(0, 0, 54.4))
r_o_box = Part.makeBox(184.0, 140.0, 65.6).translate(App.Vector(-92.0, -140.0, 54.4))
gehaeuse = gehaeuse.cut(r_o_cyl).cut(r_o_box)

s_cyl = Part.makeCylinder(100.0, 8.4).translate(App.Vector(0,0,46.0))
s_box = Part.makeBox(200.0, 140.0, 8.4).translate(App.Vector(-100.0, -140.0, 46.0))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

r_u_cyl = Part.makeCylinder(92.0, 30.0).translate(App.Vector(0,0,16.0))
r_u_box = Part.makeBox(184.0, 140.0, 30.0).translate(App.Vector(-92.0, -140.0, 16.0))
gehaeuse = gehaeuse.cut(r_u_cyl).cut(r_u_box)

b_cyl = Part.makeCylinder(100.0, 16.0).translate(App.Vector(0,0,0))
b_box = Part.makeBox(200.0, 140.0, 16.0).translate(App.Vector(-100.0, -140.0, 0))
gehaeuse = gehaeuse.cut(b_cyl).cut(b_box)

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

# 6. M3 Gewindeeinsätze für den Deckel (Oben bei Z=120, Radius=105)
for i in range(6):
    angle = math.radians(i * 60)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, gehaeuse_h - einschmelzmutter_t))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, gehaeuse_h - 10.0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# 7. M3 Gewindeeinsätze für Stacking (Unten bei Z=0, Radius=105, 30° versetzt)
for i in range(6):
    angle = math.radians(i * 60 + 30)
    x = 105.0 * math.cos(angle)
    y = 105.0 * math.sin(angle)
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, 0))
    freiraum = Part.makeCylinder(3.4 / 2.0, 10.0).translate(App.Vector(x, y, 0))
    gehaeuse = gehaeuse.cut(insert).cut(freiraum)

# 8. M3 Gewindeeinsätze für die Wasserdichte Bodenwanne (seitlich unten)
for i in range(4):
    angle_deg = i * 90 + 45
    insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t + 2.0)
    insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    insert.translate(App.Vector(fuss_radius - einschmelzmutter_t, 0, 20.0))
    insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    gehaeuse = gehaeuse.cut(insert)

# 9. M3 Verschraubung für die Elektronik-Wartungsklappe (Vorne an den Wangen)
for z_pos in [25.0, 105.0]:
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
# BAUTEIL 2: DER NEUE FLACHE STACKING-DECKEL (50mm Lagerschale!)
# ==========================================
deckel_base = Part.makeCylinder(fuss_radius + 3.0, deckel_h)

fuehrung_u = Part.makeCylinder(91.5, 6.0).cut(Part.makeCylinder(85.0, 6.0)).translate(App.Vector(0, 0, -6.0))
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
# BAUTEIL 3: DER WAND-FLANSCH 
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
# BAUTEIL 5: DER UNIVERSAL-LAGER-ADAPTER (Jetzt mit dynamischem Pressfit!)
# ==========================================
adapter_d = lager_innen_d + adapter_pressfit
kragen_aussen_d = max(34.0, lager_innen_d + 8.0) # Der Kragen skaliert dynamisch mit!

# Die konische Einführ-Fase (Die ersten 2mm sind abgeschrägt zum perfekten Einfädeln)
einfuehr_fase = Part.makeCone((adapter_d - 1.5) / 2.0, adapter_d / 2.0, 2.0)
haupt_schaft = Part.makeCylinder(adapter_d / 2.0, 13.0).translate(App.Vector(0,0, 2.0))
adapter = einfuehr_fase.fuse(haupt_schaft)

kragen_fase = Part.makeCone(adapter_d / 2.0, kragen_aussen_d / 2.0, 4.6).translate(App.Vector(0,0, 15.0))
kragen_gerade = Part.makeCylinder(kragen_aussen_d / 2.0, 12.0).translate(App.Vector(0,0, 19.6))
adapter = adapter.fuse(kragen_fase).fuse(kragen_gerade)

hex_plug = make_hex_prism(hex_radius, 8.0).translate(App.Vector(0,0, 31.6))
adapter = adapter.fuse(hex_plug)

achse_cut = make_square_prism(achse_kantenlaenge + 0.5, 42.0).translate(App.Vector(0,0, -1.0))
adapter = adapter.cut(achse_cut)

z_loch = 19.6 + 6.0 
for i in range(4):
    angle = i * 90
    m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    m3_loch.translate(App.Vector(0, 0, z_loch))
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    m3_insert.translate(App.Vector((kragen_aussen_d / 2.0) - einschmelzmutter_t, 0, z_loch))
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    adapter = adapter.cut(m3_loch).cut(m3_insert)

adapter = adapter.removeSplitter()
adapter.translate(App.Vector(fuss_radius * 2.2, 0, 0)) 
show_obj(adapter, "Universal_Lager_Adapter")


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
scheibe.translate(App.Vector(0, fuss_radius * 2.8, 0)) 
show_obj(scheibe, "Start_Scheibe_FLACH")


# ==========================================
# BAUTEIL 7: BODEN-WANNE WASSERDICHT (Völlig flach von unten!)
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
    
    # GEFIXT: Der Senkkopf war verkehrt herum! Er wird nun nach außen hin breiter (6.4mm).
    senk = Part.makeCone(3.4/2.0, 6.4/2.0, 2.0)
    senk.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    senk.translate(App.Vector(fuss_radius + 1.0, 0, 20.0))
    senk.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    
    wanne = wanne.cut(loch).cut(senk)

wanne = wanne.removeSplitter()
wanne.translate(App.Vector(0, 0, -50.0)) 
show_obj(wanne, "Boden_Wanne_Wasserdicht")


# ==========================================
# BAUTEIL 8: ELEKTRONIK WARTUNGS-KLAPPE 
# ==========================================
c_out = Part.makeCylinder(110.0, 103.0).translate(App.Vector(0, 0, 16.5))
c_in = Part.makeCylinder(106.0, 103.0).translate(App.Vector(0, 0, 16.5))
shield = c_out.cut(c_in)

b1 = Part.makeBox(230.0, 230.0, 150.0).translate(App.Vector(-115.0, 0, 0))
b2 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(91.5, -115.0, 0))
b3 = Part.makeBox(110.0, 230.0, 150.0).translate(App.Vector(-201.5, -115.0, 0))
shield = shield.cut(b1).cut(b2).cut(b3)

for z_pos in [25.0, 105.0]:
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

bp_out = Part.makeBox(80.0, 70.0, 103.0).translate(App.Vector(-40.0, -170.0, 16.5))
bp_in = Part.makeBox(72.0, 65.0, 99.0).translate(App.Vector(-36.0, -165.0, 18.5))
backpack = bp_out.cut(bp_in)

durchbruch = Part.makeBox(72.0, 30.0, 99.0).translate(App.Vector(-36.0, -120.0, 18.5))
shield = shield.cut(durchbruch)
klappe = shield.fuse(backpack)

for dx in [-25.0, 25.0]:
    for dz in [40.0, 95.0]:
        standoff = Part.makeCylinder(4.0, 5.0)
        standoff.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        standoff.translate(App.Vector(dx, -165.0, dz))
        
        loch = Part.makeCylinder(1.4, 6.0)
        loch.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
        loch.translate(App.Vector(dx, -166.0, dz))
        klappe = klappe.fuse(standoff).cut(loch)

# Das Kabel verlässt das System jetzt sauber durch die Seite der Anlage!
kabel_loch = Part.makeCylinder(4.0, 10.0).translate(App.Vector(0, -135.0, 10.0))
klappe = klappe.cut(kabel_loch)

klappe = klappe.removeSplitter()
klappe.translate(App.Vector(0, -80.0, 0)) 
show_obj(klappe, "Elektronik_Wartungs_Klappe")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")