import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Basis_Raeder")

# ==========================================
# ⚙️ PARAMETER (Basis & Räder)
# ==========================================
hex_loch_sw = 8.4         
lager_loch_d = 12.0        # Für die neuen, massiven 11.8mm Hülsen
kleines_rad_d = 20.0      
grosses_rad_d = 70.0      
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
    radius = (sw / 2.0) / math.cos(math.radians(30))
    points = []
    for j in range(6):
        angle = math.radians(60 * j + 30)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append(App.Vector(x, y, 0))
    points.append(points[0])
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def make_wheel(outer_d, groove_r, hex_sw, thickness):
    w = Part.makeCylinder(outer_d/2.0, thickness)
    nut = Part.makeTorus(outer_d/2.0, groove_r)
    w = w.cut(nut.translate(App.Vector(0,0,thickness/2.0)))
    hole = make_hex_prism(hex_sw, thickness + 10.0).translate(App.Vector(0,0,-5.0))
    return w.cut(hole).removeSplitter()

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DIE MASCHINEN-BASIS (L-Form mit Löchern)
# ==========================================
# Hauptplatte Rechts (Für die Türme): X von -25 bis 50 (Breite 75), Y von -5 bis 95 (Länge 100)
base_right = make_centered_box(75, 100, 5, 12.5, 45, 2.5) 
# Erweiterung Links (Für Dorn und Schiene): X von -80 bis -25 (Breite 55), Y von -5 bis 55 (Länge 60)
base_left = make_centered_box(55, 60, 5, -52.5, 25, 2.5)
base_plate = base_right.fuse(base_left)

# 4 Bohrlöcher (D=4.4mm für M4 Schrauben) zur Befestigung am Tisch
m4_loch = Part.makeCylinder(2.2, 10)
loch1 = m4_loch.copy().translate(App.Vector(40, 85, -2))  # Hinten Rechts
loch2 = m4_loch.copy().translate(App.Vector(40, 5, -2))   # Vorne Rechts
loch3 = m4_loch.copy().translate(App.Vector(-70, 5, -2))  # Vorne Links
loch4 = m4_loch.copy().translate(App.Vector(-70, 45, -2)) # Ecke der L-Form
base_plate = base_plate.cut(loch1).cut(loch2).cut(loch3).cut(loch4)

def make_pillar(cx, cy, height, hole_z):
    p = make_centered_box(16, 12, height, cx, cy, height/2.0 + 5.0) 
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 18)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    cut_cyl.translate(App.Vector(cx, cy+9.0, hole_z)) 
    return p.cut(cut_cyl)

# Kurbel-Türme (Rechts, X=35. Achse Z=45) 
p_cl = make_pillar(35, 45, 55, 45) 
p_cr = make_pillar(35, 71, 55, 45)  

# Wickler-Türme (Mitte, X=-15. Achse Z=30)
p_wl = make_pillar(-15, 45, 40, 30)  
p_wr = make_pillar(-15, 71, 40, 30)   

# 3. T-Träger-Schiene (Näher an die Spindel gerückt! Jetzt auf X=-30)
t_stem = make_centered_box(6.0, 50, 5.0, -30, 25, 7.5)  
t_top = make_centered_box(12.0, 50, 5.0, -30, 25, 12.5) 
schiene = t_stem.fuse(t_top)

stop_1 = Part.makeCylinder(1.4, 10).translate(App.Vector(-30, 46, 8))
stop_2 = Part.makeCylinder(1.4, 10).translate(App.Vector(-30, 4, 8))
schiene = schiene.cut(stop_1).cut(stop_2)

# 4. Dorn für die Kupferdraht-Rolle (Ganz Links, X=-65)
dorn_base = Part.makeCylinder(15, 2).translate(App.Vector(-65, 25, 5))
dorn = Part.makeCylinder(4.5, 60).translate(App.Vector(-65, 25, 7))

basis = base_plate.fuse(p_wl).fuse(p_wr).fuse(p_cl).fuse(p_cr).fuse(dorn_base).fuse(dorn).fuse(schiene)
show_obj(basis.removeSplitter(), "Maschinen_Basis_L_Shape")

# ==========================================
# BAUTEILE 2 & 3: RÄDER & SCHLITTEN (Für Druck abgelegt)
# ==========================================
rad_k = make_wheel(grosses_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(35, -50, 0.0)) 
show_obj(rad_k, "Rad_Gross_Kurbel")

rad_w = make_wheel(kleines_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(-15, -50, 0.0))
show_obj(rad_w, "Rad_Klein_Wickler")

# Der Führungsschlitten
sled = make_centered_box(24, 16, 25, 0, 0, 12.5)
cut_stem = make_centered_box(6.6, 16.0, 5.0, 0, 0, 2.5)   
cut_top = make_centered_box(12.6, 16.0, 5.5, 0, 0, 7.75)  

# Loch geht durch die X-Achse
wire_hole = Part.makeCylinder(0.5, 30)
wire_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
sled = sled.cut(cut_stem).cut(cut_top).cut(wire_hole.translate(App.Vector(-15, 0, 20)))

sled.translate(App.Vector(-65, -50, 0)) 
show_obj(sled.removeSplitter(), "Schlitten_Drahtfuehrung_T_Form")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")