import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Basis_Raeder")

# ==========================================
# ⚙️ PARAMETER (Teil 1: Basis & Räder)
# ==========================================
m3_loch = 3.6             
hex_loch_sw = 8.4         # 8.4mm Loch (Toleranz fürs leichte Aufschieben auf 8mm Achse)
lager_loch_d = 9.6        # 9.6mm Rundloch für perfekten Lauf der Sechskant-Wellen

kleines_rad_d = 20.0      
grosses_rad_d = 80.0 
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
    points.append(points[0]) # Polygon schließen
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def make_wheel(outer_d, groove_r, hex_sw, thickness):
    w = Part.makeCylinder(outer_d/2.0, thickness)
    nut = Part.makeTorus(outer_d/2.0, groove_r)
    w = w.cut(nut.translate(App.Vector(0,0,thickness/2.0)))
    
    # Integrierte Abstandshalter (Spacer) - 2mm auf jeder Seite
    hub = Part.makeCylinder(14.0/2.0, thickness + 4.0).translate(App.Vector(0,0,-2.0))
    w = w.fuse(hub)
    
    # Sechskant-Loch für das Steck-System
    hole = make_hex_prism(hex_sw, thickness + 10.0).translate(App.Vector(0,0,-5.0))
    return w.cut(hole).removeSplitter()

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DIE MASCHINEN-BASIS (Flach liegend)
# ==========================================
base_plate = make_centered_box(150, 90, 5, 0, 0, 2.5)

# Die 4 Stütztürme (Abstand jetzt extrem großzügige 24mm!)
def make_pillar(cx, cy):
    p = make_centered_box(16, 12, 40, cx, cy, 25) # Z: 5 bis 45
    # Drop-In Schlitz von oben (Breite 9.6mm)
    cut_box = make_centered_box(9.6, 13, 15, cx, cy, 37.5) 
    # Rundes Bett für die Achse
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 13)
    cut_cyl.rotate(App.Vector(1,0,0), 90)
    cut_cyl.translate(App.Vector(cx, cy+6.5, 30))
    return p.cut(cut_box).cut(cut_cyl)

# Platzierung der Türme:
p_wl = make_pillar(40, -18)  # Wickler Front
p_wr = make_pillar(40, 18)   # Wickler Hinten
p_cl = make_pillar(-35, -18) # Kurbel Front
p_cr = make_pillar(-35, 18)  # Kurbel Hinten

# Dorn für die Kupferdraht-Rolle
dorn_base = Part.makeCylinder(15, 2).translate(App.Vector(55, 25, 5))
dorn = Part.makeCylinder(4.5, 60).translate(App.Vector(55, 25, 7))

# Gleitschiene für die Drahtführung
schiene = make_centered_box(50, 8, 8, 40, -35, 9)

basis = base_plate.fuse(p_wl).fuse(p_wr).fuse(p_cl).fuse(p_cr).fuse(dorn_base).fuse(dorn).fuse(schiene)
show_obj(basis.removeSplitter(), "Maschinen_Basis")


# ==========================================
# BAUTEIL 2: GROSSES KURBEL-RAD (Flach liegend)
# ==========================================
rad_k = make_wheel(grosses_rad_d, 1.5, hex_loch_sw, 10.0)
rad_k.translate(App.Vector(-45, 95, 2.0)) # Flach über der Basis platzieren
show_obj(rad_k, "Rad_Gross_Kurbel")


# ==========================================
# BAUTEIL 3: KLEINES WICKEL-RAD (Flach liegend)
# ==========================================
rad_w = make_wheel(kleines_rad_d, 1.5, hex_loch_sw, 10.0)
rad_w.translate(App.Vector(20, 95, 2.0))
show_obj(rad_w, "Rad_Klein_Wickler")


# ==========================================
# BAUTEIL 4: DRAHTFÜHRUNGS-SCHLITTEN (Flach liegend)
# ==========================================
sled = make_centered_box(16, 14, 12, 0, 0, 6)
sled = sled.cut(make_centered_box(8.6, 16, 8.6, 0, 0, 2)) # Schienen-Nut
# 1mm Führung-Loch
loch_s = Part.makeCylinder(1.0, 20)
loch_s.rotate(App.Vector(1,0,0), 90)
sled = sled.cut(loch_s.translate(App.Vector(0, 10, 9)))
sled.translate(App.Vector(60, 95, 0))
show_obj(sled.removeSplitter(), "Schlitten_Drahtfuehrung")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Teil 1: Basis & Räder erfolgreich generiert und flach ausgelegt!")