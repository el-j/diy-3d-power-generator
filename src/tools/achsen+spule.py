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

m3_loch = 3.6             
m3_mutter_sw = 5.8        
hex_achse_sw = 8.0        # Massiver 8mm Sechskant
hex_loch_sw = 8.4         
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
    radius = sw / math.sqrt(3)
    points = []
    for j in range(6):
        angle = math.radians(60 * j)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append(App.Vector(x, y, 0))
    points.append(points[0])
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: KURBEL-ACHSE (Flach liegend)
# ==========================================
shaft_k = make_hex_prism(hex_achse_sw, 65.0)
stopper_k = Part.makeCylinder(14.0/2.0, 3.0).translate(App.Vector(0,0,-3.0)) # Anschlag-Teller
achse_k = shaft_k.fuse(stopper_k).cut(Part.makeCylinder(m3_loch/2.0, 70.0).translate(App.Vector(0,0,-5.0)))
achse_k = achse_k.removeSplitter()

# Für den Druck flach auf den Boden legen
achse_k.rotate(App.Vector(0,1,0), 90)
achse_k.translate(App.Vector(-30, 20, 4.0))
show_obj(achse_k, "Achse_Kurbel_Steck")


# ==========================================
# BAUTEIL 2: KURBEL-ARM (Flach liegend)
# ==========================================
arm = make_centered_box(45, 16, 8, 22.5, 0, 4)
hub_a = Part.makeCylinder(14.0/2.0, 2.0).translate(App.Vector(0,0,-2.0)) # Spacer zum Turm
griff = Part.makeCylinder(6.0/2.0, 30.0).translate(App.Vector(40, 0, 8.0))
hole_a = make_hex_prism(hex_loch_sw, 15.0).translate(App.Vector(0,0,-5.0))

kurbel_arm = arm.fuse(hub_a).fuse(griff).cut(hole_a).removeSplitter()
kurbel_arm.translate(App.Vector(-30, -30, 2.0))
show_obj(kurbel_arm, "Kurbel_Arm")


# ==========================================
# BAUTEIL 3: WICKEL-ACHSE (Flach liegend)
# ==========================================
# Diese Achse ist länger, da sie auch die Spulenteile aufnehmen muss
shaft_w = make_hex_prism(hex_achse_sw, 80.0)
stopper_w = Part.makeCylinder(14.0/2.0, 3.0).translate(App.Vector(0,0,-3.0)) # Anschlag-Teller
# Akkuschrauber-Antrieb auf der anderen Seite des Tellers
drive_w = make_hex_prism(hex_achse_sw, 15.0).translate(App.Vector(0,0,-18.0)) 

achse_w = shaft_w.fuse(stopper_w).fuse(drive_w).cut(Part.makeCylinder(m3_loch/2.0, 105.0).translate(App.Vector(0,0,-20.0)))
achse_w = achse_w.removeSplitter()

achse_w.rotate(App.Vector(0,1,0), 90)
achse_w.translate(App.Vector(30, 20, 4.0))
show_obj(achse_w, "Achse_Wickler_Steck")


# ==========================================
# BAUTEIL 4: SPULE - INNENTEIL (Flach liegend)
# ==========================================
flansch_b = Part.makeCylinder(18.0/2.0, 3.0)
core_b = Part.makeCylinder(spule_innen_d/2.0, spule_dicke).translate(App.Vector(0,0,3.0))
hub_b = Part.makeCylinder(12.0/2.0, 2.0).translate(App.Vector(0,0,-2.0)) # Spacer zum Turm
hole_b = make_hex_prism(hex_loch_sw, 15.0).translate(App.Vector(0,0,-5.0))
# Schlitz für den Drahtanfang
slot_b = make_centered_box(10, 0.8, 5, 5, 0, 1.5)

basis_w = flansch_b.fuse(core_b).fuse(hub_b).cut(hole_b).cut(slot_b).removeSplitter()
basis_w.translate(App.Vector(30, -30, 2.0))
show_obj(basis_w, "Spule_Inneres_Teil")


# ==========================================
# BAUTEIL 5: SPULE - DECKEL (Flach liegend)
# ==========================================
deckel = Part.makeCylinder(18.0/2.0, 3.0)
deckel = deckel.cut(Part.makeCylinder(m3_loch/2.0, 10.0).translate(App.Vector(0,0,-5.0)))
deckel = deckel.cut(make_hex_prism(m3_mutter_sw, 2.5).translate(App.Vector(0,0,0.5))) # M3 Mutter Nut

# Gravur für 14mm Füllstand
ring_out = Part.makeCylinder(spule_aussen_d / 2.0, 0.5)
ring_in = Part.makeCylinder((spule_aussen_d / 2.0) - 0.5, 0.5)
ring = ring_out.cut(ring_in)
deckel = deckel.cut(ring)

deckel.translate(App.Vector(60, -30, 0))
show_obj(deckel.removeSplitter(), "Spule_Aeusserer_Deckel")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Teil 2: Achsen & Zubehör erfolgreich generiert und flach ausgelegt!")