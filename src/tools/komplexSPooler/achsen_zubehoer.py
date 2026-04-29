import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Zubehoer_Komplett")

# ==========================================
# ⚙️ PARAMETER
# ==========================================
hex_achse_sw = 8.0        
hex_loch_sw = 8.4         
quad_spindel_sw = 6.0      
quad_spindel_loch_sw = 6.4 

spule_innen_d = 14.0      
spule_aussen_d = 36.0     
spule_dicke = 6.0         
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
    radius = (sw / 2.0) / math.cos(math.radians(30))
    points = []
    for j in range(6):
        angle = math.radians(60 * j) 
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append(App.Vector(x, y, 0))
    points.append(points[0])
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def get_m3_insert_cutout():
    ins = Part.makeCylinder(4.2/2.0, 5.0)
    pas = Part.makeCylinder(3.2/2.0, 15.0) 
    cut = ins.fuse(pas).removeSplitter()
    cut.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90) 
    return cut

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# 1. DIE 4 ACHSEN (Liegend für den perfekten Druck)
# ==========================================
achse_1 = make_hex_prism(hex_achse_sw, 110.0)
achse_1.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_1.translate(App.Vector(0, 0, 4.0)) 
show_obj(achse_1, "Achse_1_Kurbel_110mm")

achse_2_hex = make_hex_prism(hex_achse_sw, 80.0)
achse_2_quad = make_square_prism(quad_spindel_sw, 35.0).translate(App.Vector(0,0,80.0))
achse_2 = achse_2_hex.fuse(achse_2_quad)
achse_2.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_2.translate(App.Vector(15, 0, 4.0))
show_obj(achse_2, "Achse_2_Spule_115mm")

achse_3 = make_hex_prism(hex_achse_sw, 110.0)
achse_3.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_3.translate(App.Vector(30, 0, 4.0)) 
show_obj(achse_3, "Achse_3_Zwischen_110mm")

achse_4 = make_hex_prism(hex_achse_sw, 120.0)
achse_4.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_4.translate(App.Vector(45, 0, 4.0)) 
show_obj(achse_4, "Achse_4_Trommel_120mm")

# ==========================================
# 2. DIE LAGERHÜLSEN (8 Stück benötigt)
# ==========================================
def make_bearing_sleeve(x_pos, y_pos):
    zapfen = Part.makeCylinder(11.4/2.0, 14.0) 
    kragen = Part.makeCylinder(16.0/2.0, 8.0).translate(App.Vector(0,0,14.0))
    huelse = zapfen.fuse(kragen)
    
    hole = make_hex_prism(hex_loch_sw, 30.0).translate(App.Vector(0,0,-2.0))
    m3_cut = get_m3_insert_cutout().translate(App.Vector(0, 8.0, 18.0))
    
    fin = huelse.cut(hole).cut(m3_cut).removeSplitter()
    fin.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 180) 
    fin.translate(App.Vector(x_pos, y_pos, 22.0)) 
    return fin

for i in range(4):
    show_obj(make_bearing_sleeve(-20, i*20), f"Lagerhuelse_A{i+1}")
    show_obj(make_bearing_sleeve(-40, i*20), f"Lagerhuelse_B{i+1}")

# ==========================================
# 3. TAUMEL-SCHEIBEN (2 identische Hälften für flachen Druck)
# ==========================================
def make_wobble_half():
    # Flache Basis - massiv verdickt auf 16mm für extremen Halt der Schraube!
    drum = Part.makeCylinder(20.0, 16.0)
    
    # Schräger Schnitt (10 Grad für 6mm Hub) - Beginnt jetzt erst bei Z=8.0
    cut_box = Part.makeBox(60, 60, 30).translate(App.Vector(-30, -30, 0))
    cut_box.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 10.0) 
    cut_box.translate(App.Vector(0,0, 8.0))
    drum = drum.cut(cut_box)
    
    # Hex-Loch
    hex_hole = make_hex_prism(hex_loch_sw, 30).translate(App.Vector(0,0,-5))
    drum = drum.cut(hex_hole)
    
    # M3-Loch jetzt auf Z=6.0 zentriert (sitzt absolut mittig in der fetten 8mm Basis)
    m3_hole = Part.makeCylinder(3.6/2.0, 25)
    m3_hole.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    m3_hole.translate(App.Vector(0, 25, 6.0)) 
    
    m3_insert = Part.makeCylinder(4.6/2.0, 5.8)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    m3_insert.translate(App.Vector(0, 20.5, 6.0))
    
    drum = drum.cut(m3_hole.fuse(m3_insert))
    
    return drum.removeSplitter()

# Wir drucken einfach zwei exakt gleiche Hälften!
half1 = make_wobble_half()
half1.translate(App.Vector(80, -20, 0))
show_obj(half1, "Taumel_Scheibe_Haelfte_1")

half2 = make_wobble_half()
half2.translate(App.Vector(80, 30, 0))
show_obj(half2, "Taumel_Scheibe_Haelfte_2")

# ==========================================
# 4. KURBEL-ARM & GRIFF
# ==========================================
arm_dicke = 6.0 
arm_box = make_centered_box(40, 14, arm_dicke, 20, 0, arm_dicke/2.0) 
hub = Part.makeCylinder(16.0/2.0, arm_dicke) 
kurbel_arm = arm_box.fuse(hub)

hole_a = make_hex_prism(hex_loch_sw, arm_dicke + 2.0).translate(App.Vector(0,0,-1.0))
griff_steckplatz = make_hex_prism(6.2, 4.0).translate(App.Vector(35, 0, arm_dicke - 3.0)) 
griff_m3_loch = Part.makeCylinder(1.7, arm_dicke).translate(App.Vector(35, 0, 0)) 
senkkopf = Part.makeCone(3.2, 1.7, 2.5).translate(App.Vector(35, 0, 0)) 

kurbel_arm = kurbel_arm.cut(hole_a).cut(griff_steckplatz).cut(griff_m3_loch).cut(senkkopf).removeSplitter()
kurbel_arm.translate(App.Vector(130, 0, 0)) 
show_obj(kurbel_arm, "Kurbel_Arm")

griff_koerper = Part.makeCylinder(12.0/2.0, 30.0).translate(App.Vector(0, 0, 3.0))
griff_zapfen = make_hex_prism(5.8, 3.0) 
griff_teil = griff_koerper.fuse(griff_zapfen)
griff_freiraum = Part.makeCylinder(1.8, 35.0) 

griff_fin = griff_teil.cut(griff_freiraum).removeSplitter()
griff_fin.translate(App.Vector(130, 30, 0))
show_obj(griff_fin, "Kurbel_Griff")

# ==========================================
# 5. SPULE (Vierkant-Aufnahme)
# ==========================================
flansch_dicke = 3.0 
flansch_r = (spule_aussen_d / 2.0) + 2.0 
flansch_b = Part.makeCylinder(flansch_r, flansch_dicke)

core_b = Part.makeCylinder(spule_innen_d/2.0, spule_dicke + 1.0).translate(App.Vector(0,0,flansch_dicke))
hole_b = make_square_prism(quad_spindel_loch_sw, flansch_dicke + spule_dicke + 2.0).translate(App.Vector(0,0,-1.0))

slot_b = Part.makeBox(20, 1.2, 5).translate(App.Vector(0, -0.6, 0)) 
ring_out = Part.makeCylinder(spule_aussen_d / 2.0, 0.5)
ring_in = Part.makeCylinder((spule_aussen_d / 2.0) - 0.5, 0.5)
ring = ring_out.cut(ring_in)
ring_innen = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5)) 

spule_in = flansch_b.fuse(core_b).cut(hole_b).cut(slot_b).cut(ring_innen).removeSplitter()
spule_in.translate(App.Vector(130, -50, 0))
show_obj(spule_in, "Spule_Innen_Quad")

deckel = Part.makeCylinder(flansch_r, flansch_dicke)
recess = Part.makeCylinder((spule_innen_d + 0.4)/2.0, 1.0).translate(App.Vector(0,0, flansch_dicke - 1.0))
hole_d = make_square_prism(quad_spindel_loch_sw, flansch_dicke + 2.0).translate(App.Vector(0,0,-1.0))
senkkopf_d = Part.makeCone(3.2, 1.7, 2.5) 
ring_deckel = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5))

spule_out = deckel.cut(recess).cut(hole_d).cut(senkkopf_d).cut(ring_deckel).removeSplitter()
spule_out.translate(App.Vector(180, -50, 0))
show_obj(spule_out, "Spule_Deckel_Quad")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")