import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Zubehoer")

# ==========================================
# ⚙️ PARAMETER (Teil 2: Achsen & Zubehör)
# ==========================================
spule_innen_d = 7.0       
spule_aussen_d = 14.0     
spule_dicke = 3.5         

hex_achse_sw = 8.0        # Haupt-Antriebsachse
hex_loch_sw = 8.4         
hex_spindel_sw = 4.0      # NEU: Dünne Achsenspitze für kleine Spulen!
hex_spindel_loch_sw = 4.4 # NEU: Passendes Loch in der Spule
m3_loch = 3.6             
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
    # Durch den 30° Offset liegen die Sechskant-Achsen beim Rotieren perfekt flach!
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

def get_m3_insert_cutout():
    # Schneidet das Loch für Einschmelzmutter (D=4.2, T=5) + Madenschraube (D=3.2)
    ins = Part.makeCylinder(4.2/2.0, 5.0)
    pas = Part.makeCylinder(3.2/2.0, 15.0)
    cut = ins.fuse(pas).removeSplitter()
    cut.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90) # Rotiert in -Y Richtung
    return cut

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEILE 1 & 2: DIE GERADEN STECK-ACHSEN
# ==========================================
achse_k = make_hex_prism(hex_achse_sw, 90.0)
achse_k.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_k.translate(App.Vector(-30, 30, 4.0)) 
show_obj(achse_k, "Achse_Kurbel_90mm")

# Die NEUE Wickler-Achse (Zweistufig: 8mm für Lager -> 4mm für Spule)
achse_w_base = make_hex_prism(hex_achse_sw, 95.0)
achse_w_spindel = make_hex_prism(hex_spindel_sw, 25.0).translate(App.Vector(0,0,95.0))
achse_w = achse_w_base.fuse(achse_w_spindel)

# 2.5mm Loch an der Spitze für eine sich selbst schneidende M3 Schraube!
pas_w = Part.makeCylinder(2.5/2.0, 15.0).translate(App.Vector(0,0,105.0))
achse_w = achse_w.cut(pas_w).removeSplitter()

achse_w.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
achse_w.translate(App.Vector(-30, 45, 4.0))
show_obj(achse_w, "Achse_Wickler_Zweistufig")

# ==========================================
# BAUTEIL 3: DER KURBEL-ARM (Schlank & Bündig)
# ==========================================
arm_dicke = 6.0 # HALBIERT! (Vorher 12mm)
arm_box = make_centered_box(40, 18, arm_dicke, 20, 0, arm_dicke/2.0) 
hub = Part.makeCylinder(18.0/2.0, arm_dicke) 

kurbel_arm = arm_box.fuse(hub)
hole_a = make_hex_prism(hex_loch_sw, arm_dicke + 2.0).translate(App.Vector(0,0,-1.0))

# M3 Ausschnitt angepasst auf 6mm Dicke (Z=3.0)
m3_cut_arm = get_m3_insert_cutout().translate(App.Vector(0, 9.0, arm_dicke/2.0))

# Steckplatz für Griff (X=35)
griff_steckplatz = make_hex_prism(6.2, 4.0).translate(App.Vector(35, 0, arm_dicke - 3.0)) 
griff_m3_loch = Part.makeCylinder(1.7, arm_dicke).translate(App.Vector(35, 0, 0)) 
senkkopf = Part.makeCone(3.2, 1.7, 2.5).translate(App.Vector(35, 0, 0)) 

kurbel_arm = kurbel_arm.cut(hole_a).cut(m3_cut_arm).cut(griff_steckplatz).cut(griff_m3_loch).cut(senkkopf).removeSplitter()
kurbel_arm.translate(App.Vector(-10, 80, 0)) 
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
griff_fin.translate(App.Vector(40, 80, 0))
show_obj(griff_fin, "Kurbel_Griff_Steckbar")

# ==========================================
# BAUTEIL 4: SPULE - INNENTEIL (Universell für 4mm Achse)
# ==========================================
flansch_dicke = 3.0 # Schön flach!
flansch_b = Part.makeCylinder(18.0/2.0, flansch_dicke)

# Kern: 7.0mm Durchmesser. 3.5mm Spulendicke + 1mm Zentrierzapfen = 4.5mm hoch
core_b = Part.makeCylinder(spule_innen_d/2.0, spule_dicke + 1.0).translate(App.Vector(0,0,flansch_dicke))

# Das Loch ist jetzt ein dünner 4.4mm Hex und geht durch das KOMPLETTE Teil!
hole_b = make_hex_prism(hex_spindel_loch_sw, flansch_dicke + spule_dicke + 2.0).translate(App.Vector(0,0,-1.0))
slot_b = Part.makeBox(10, 0.8, 5).translate(App.Vector(0, -0.4, 0))

ring_out = Part.makeCylinder(spule_aussen_d / 2.0, 0.5)
ring_in = Part.makeCylinder((spule_aussen_d / 2.0) - 0.5, 0.5)
ring = ring_out.cut(ring_in)
ring_innen = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5)) 

basis_w = flansch_b.fuse(core_b).cut(hole_b).cut(slot_b).cut(ring_innen).removeSplitter()
basis_w.translate(App.Vector(15, 10, 0))
show_obj(basis_w, "Spule_Inneres_Teil")

# ==========================================
# BAUTEIL 5: SPULE - DECKEL (Flach & Ohne Kragen!)
# ==========================================
deckel = Part.makeCylinder(18.0/2.0, flansch_dicke)

# Nut für den 1mm Zentrier-Zapfen
recess = Part.makeCylinder((spule_innen_d + 0.4)/2.0, 1.0).translate(App.Vector(0,0, flansch_dicke - 1.0))

# 4.4mm Hex Loch für die feine Spindel-Achse
hole_d = make_hex_prism(hex_spindel_loch_sw, flansch_dicke + 2.0).translate(App.Vector(0,0,-1.0))

# Senkkopf für die zentrale M3 Befestigungsschraube (Kein dicker Kragen mehr nötig!)
senkkopf_d = Part.makeCone(3.2, 1.7, 2.5) 
ring_deckel = ring.copy().translate(App.Vector(0,0, flansch_dicke - 0.5))

deckel_fin = deckel.cut(recess).cut(hole_d).cut(senkkopf_d).cut(ring_deckel).removeSplitter()
deckel_fin.translate(App.Vector(45, 10, 0))
show_obj(deckel_fin, "Spule_Aeusserer_Deckel_Flach")

# ==========================================
# BAUTEIL 6: LAGERHÜLSEN (Bearing Sleeves)
# ==========================================
def make_bearing_sleeve(x_pos, y_pos):
    zapfen = Part.makeCylinder(9.5/2.0, 18.0) 
    kragen = Part.makeCylinder(16.0/2.0, 8.0).translate(App.Vector(0,0,18.0))
    huelse = zapfen.fuse(kragen)
    
    hole = make_hex_prism(hex_loch_sw, 30.0).translate(App.Vector(0,0,-2.0))
    m3_cut = get_m3_insert_cutout().translate(App.Vector(0, 8.0, 22.0))
    
    fin = huelse.cut(hole).cut(m3_cut).removeSplitter()
    fin.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 180)
    fin.translate(App.Vector(x_pos, y_pos, 26.0))
    return fin

show_obj(make_bearing_sleeve(75, 10), "Lagerhuelse_1")
show_obj(make_bearing_sleeve(75, 30), "Lagerhuelse_2")
show_obj(make_bearing_sleeve(95, 10), "Lagerhuelse_3")
show_obj(make_bearing_sleeve(95, 30), "Lagerhuelse_4")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Dünne 4mm Spindel-Achse, flacher Deckel und halbierter Kurbelarm generiert!")