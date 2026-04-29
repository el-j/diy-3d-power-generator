import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Zubehoer")

# ==========================================
# ⚙️ PARAMETER (Achsen & Zubehör)
# ==========================================
spule_innen_d = 14.0      # XXL: 14mm Kern
spule_aussen_d = 36.0     # XXL: 36mm Außen-D
spule_dicke = 6.0         # XXL: 6mm dick

hex_achse_sw = 8.0        
hex_loch_sw = 8.4         
quad_spindel_sw = 6.0      # NEU: 6mm Vierkant für extremen Halt
quad_spindel_loch_sw = 6.4 # NEU: 6.4mm Vierkant-Loch
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
# BAUTEILE 1 & 2: DIE ACHSEN 
# ==========================================
achse_k = make_hex_prism(hex_achse_sw, 95.0)
achse_k.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_k.translate(App.Vector(35, 85, 4.0)) 
show_obj(achse_k, "Achse_Kurbel_95mm")

achse_w_base = make_hex_prism(hex_achse_sw, 56.0)
achse_w_spindel = make_square_prism(quad_spindel_sw, 30.0).translate(App.Vector(0,0,56.0))
achse_w = achse_w_base.fuse(achse_w_spindel)

pas_w = Part.makeCylinder(2.5/2.0, 15.0).translate(App.Vector(0,0,76.0))
achse_w = achse_w.cut(pas_w).removeSplitter()

achse_w.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_w.translate(App.Vector(-15, 85, 4.0))
show_obj(achse_w, "Achse_Wickler_Zweistufig_Quad")

sp_spacer = Part.makeCylinder(16.0/2.0, 10.0) # Spacer dicker für Vierkant-Ausschnitt
sp_spacer = sp_spacer.cut(make_square_prism(quad_spindel_loch_sw, 20.0).translate(App.Vector(0,0,-2.0)))
sp_spacer.translate(App.Vector(10, 30, 0))
show_obj(sp_spacer, "Spulen_Distanz_Spacer_Quad")

# ==========================================
# BAUTEIL 3: DER KURBEL-ARM 
# ==========================================
arm_dicke = 6.0 
arm_box = make_centered_box(40, 12, arm_dicke, 20, 0, arm_dicke/2.0) 
hub = Part.makeCylinder(14.0/2.0, arm_dicke) 
kurbel_arm = arm_box.fuse(hub)

hole_a = make_hex_prism(hex_loch_sw, arm_dicke + 2.0).translate(App.Vector(0,0,-1.0))
m3_cut_arm = get_m3_insert_cutout().translate(App.Vector(0, 6.0, arm_dicke/2.0))

griff_steckplatz = make_hex_prism(6.2, 4.0).translate(App.Vector(35, 0, arm_dicke - 3.0)) 
griff_m3_loch = Part.makeCylinder(1.7, arm_dicke).translate(App.Vector(35, 0, 0)) 
senkkopf = Part.makeCone(3.2, 1.7, 2.5).translate(App.Vector(35, 0, 0)) 

kurbel_arm = kurbel_arm.cut(hole_a).cut(m3_cut_arm).cut(griff_steckplatz).cut(griff_m3_loch).cut(senkkopf).removeSplitter()
kurbel_arm.translate(App.Vector(35, -20, 0)) 
show_obj(kurbel_arm, "Kurbel_Arm_Schlank")

# ==========================================
# BAUTEIL 3b: DER SEPARATE KURBEL-GRIFF
# ==========================================
griff_koerper = Part.makeCylinder(10.0/2.0, 26.0).translate(App.Vector(0, 0, 3.0))
griff_zapfen = make_hex_prism(5.8, 3.0) 
griff_teil = griff_koerper.fuse(griff_zapfen)
griff_insert = Part.makeCylinder(4.2/2.0, 6.0)
griff_freiraum = Part.makeCylinder(1.8, 10.0) 

griff_fin = griff_teil.cut(griff_insert).cut(griff_freiraum).removeSplitter()
griff_fin.translate(App.Vector(70, -20, 0))
show_obj(griff_fin, "Kurbel_Griff_Steckbar")

# ==========================================
# BAUTEIL 4: SPULE - INNENTEIL
# ==========================================
flansch_dicke = 3.0 
flansch_r = (spule_aussen_d / 2.0) + 2.0 # Extra großer Flansch für die XXL Spulen (D=40mm)
flansch_b = Part.makeCylinder(flansch_r, flansch_dicke)

core_b = Part.makeCylinder(spule_innen_d/2.0, spule_dicke + 1.0).translate(App.Vector(0,0,flansch_dicke))
hole_b = make_square_prism(quad_spindel_loch_sw, flansch_dicke + spule_dicke + 2.0).translate(App.Vector(0,0,-1.0))

# Längerer & breiterer Schlitz für dickeren Kupferdraht
slot_b = Part.makeBox(20, 1.2, 5).translate(App.Vector(0, -0.6, 0)) 

ring_out = Part.makeCylinder(spule_aussen_d / 2.0, 0.5)
ring_in = Part.makeCylinder((spule_aussen_d / 2.0) - 0.5, 0.5)
ring = ring_out.cut(ring_in)
ring_innen = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5)) 

basis_w = flansch_b.fuse(core_b).cut(hole_b).cut(slot_b).cut(ring_innen).removeSplitter()
basis_w.translate(App.Vector(10, 5, 0))
show_obj(basis_w, "Spule_Inneres_Teil")

# ==========================================
# BAUTEIL 5: SPULE - DECKEL
# ==========================================
deckel = Part.makeCylinder(flansch_r, flansch_dicke)
recess = Part.makeCylinder((spule_innen_d + 0.4)/2.0, 1.0).translate(App.Vector(0,0, flansch_dicke - 1.0))

# M3 Senkkopf wie gehabt, aber mit dem neuen Vierkant-Loch
hole_d = make_square_prism(quad_spindel_loch_sw, flansch_dicke + 2.0).translate(App.Vector(0,0,-1.0))
senkkopf_d = Part.makeCone(3.2, 1.7, 2.5) 
ring_deckel = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5))

deckel_fin = deckel.cut(recess).cut(hole_d).cut(senkkopf_d).cut(ring_deckel).removeSplitter()
deckel_fin.translate(App.Vector(60, 5, 0)) # Auf X=60 gerückt, da der Radius jetzt riesig ist
show_obj(deckel_fin, "Spule_Aeusserer_Deckel_Flach")

# ==========================================
# BAUTEIL 6: LAGERHÜLSEN (Anti-Reibungs-Edition!)
# ==========================================
def make_bearing_sleeve(x_pos, y_pos):
    # Zapfen auf 11.4mm geschrumpft! (Gibt fette 0.6mm Spiel in den Türmen)
    zapfen = Part.makeCylinder(11.4/2.0, 14.0) 
    kragen = Part.makeCylinder(16.0/2.0, 8.0).translate(App.Vector(0,0,14.0))
    huelse = zapfen.fuse(kragen)
    
    hole = make_hex_prism(hex_loch_sw, 30.0).translate(App.Vector(0,0,-2.0))
    m3_cut = get_m3_insert_cutout().translate(App.Vector(0, 8.0, 18.0))
    
    fin = huelse.cut(hole).cut(m3_cut).removeSplitter()
    fin.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 180)
    fin.translate(App.Vector(x_pos, y_pos, 22.0))
    return fin

show_obj(make_bearing_sleeve(-20, 45), "Lagerhuelse_1_Lose")
show_obj(make_bearing_sleeve(-20, 65), "Lagerhuelse_2_Lose")
show_obj(make_bearing_sleeve(0, 45), "Lagerhuelse_3_Lose")
show_obj(make_bearing_sleeve(0, 65), "Lagerhuelse_4_Lose")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")