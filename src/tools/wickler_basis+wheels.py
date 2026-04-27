import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Basis_Raeder")

# ==========================================
# ⚙️ PARAMETER (Basis & Räder)
# ==========================================
hex_loch_sw = 8.4         
lager_loch_d = 12.0        
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
# BAUTEIL 1: DIE MASCHINEN-BASIS (Modulares Fundament)
# ==========================================
# Hauptplatte Rechts (X: -25 bis 50, Y: -5 bis 95)
base_right = make_centered_box(75, 100, 5, 12.5, 45, 2.5) 
# Erweiterung Links - Verlängert für mehr Platz! (X: -85 bis -25, Y: -5 bis 55)
base_left = make_centered_box(60, 60, 5, -55.0, 25, 2.5)
base_plate = base_right.fuse(base_left)

# 4 Bohrlöcher (D=4.4mm für M4 Schrauben) zur Befestigung am Tisch
m4_loch = Part.makeCylinder(2.2, 10)
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(40, 85, -2)))  
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(40, 5, -2)))   
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(-80, 5, -2)))  
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(-80, 45, -2))) 

# ==========================================
# WERKZEUGE FÜR DIE STECKVERBINDUNGEN
# ==========================================
recess_depth = 1.5
base_z_top = 5.0
pillar_bottom_z = base_z_top - recess_depth # Türme sinken auf Z=3.5 ein

m3_through = Part.makeCylinder(1.7, 10.0).translate(App.Vector(0,0,-2)) # Durchgangsloch
m3_head_sink = Part.makeCylinder(3.0, 3.1) # Senkkopf-Bohrung von unten (lässt 1.9mm dickes Plastik stehen)
m3_insert = Part.makeCylinder(2.1, 5.0) # Loch für die Einschmelzmutter im Turm/Dorn

# ==========================================
# DIE STECKBAREN TÜRME GENERIEREN
# ==========================================
def create_pluggable_pillar(name, cx, cy, target_top_z, target_hole_z, pr_x, pr_y):
    global base_plate
    
    # 1. Aussparung aus der Basisplatte schneiden
    pocket = make_centered_box(16.4, 12.4, recess_depth, cx, cy, base_z_top - (recess_depth/2.0))
    base_plate = base_plate.cut(pocket)
    
    # 2. Zwei Durchgangslöcher und Senkköpfe für die Basis
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx, cy + 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx, cy + 3.0, 0)))
    
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx, cy - 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx, cy - 3.0, 0)))
    
    # 3. Den Turm als separates Teil konstruieren
    local_h = target_top_z - pillar_bottom_z
    local_hz = target_hole_z - pillar_bottom_z
    
    p = make_centered_box(16, 12, local_h, 0, 0, local_h/2.0)
    
    # Achsen-Loch
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 18)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    p = p.cut(cut_cyl.translate(App.Vector(0, 9.0, local_hz)))
    
    # Zwei M3 Einschmelz-Löcher am Boden
    p = p.cut(m3_insert.copy().translate(App.Vector(0, 3.0, 0)))
    p = p.cut(m3_insert.copy().translate(App.Vector(0, -3.0, 0)))
    p = p.removeSplitter()
    
    # 4. Flach auf das Druckbett legen für maximale Layer-Stabilität!
    p.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
    p.translate(App.Vector(pr_x, pr_y, 6.0)) # 6mm = Halbe Dicke, liegt exakt auf Z=0
    show_obj(p, name)

# Türme mit exakten Z-Höhen generieren und als Druck-Teile ablegen
create_pluggable_pillar("Turm_Kurbel_Vorne",   35, 45, 55, 45,  70, 80)
create_pluggable_pillar("Turm_Kurbel_Hinten",  35, 71, 55, 45,  70, 50)
create_pluggable_pillar("Turm_Wickler_Vorne", -15, 45, 40, 30,  90, 80)
create_pluggable_pillar("Turm_Wickler_Hinten",-15, 71, 40, 30,  90, 50)

# ==========================================
# DER STECKBARE ROLLEN-DORN
# ==========================================
dcx, dcy = -68, 25 # Position weiter nach Links gerückt!

# Aussparung in der Basis
pocket_dorn = Part.makeCylinder(15.3, recess_depth).translate(App.Vector(dcx, dcy, base_z_top - recess_depth))
base_plate = base_plate.cut(pocket_dorn)

# Auch hier zwei Löcher für den Dorn
base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(dcx + 8.0, dcy, 0)))
base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(dcx + 8.0, dcy, 0)))

base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(dcx - 8.0, dcy, 0)))
base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(dcx - 8.0, dcy, 0)))


# Druckbarer Dorn
dorn_b = Part.makeCylinder(15, 2.0 + recess_depth)
dorn_p = Part.makeCylinder(4.5, 60).translate(App.Vector(0,0,2.0 + recess_depth))
dorn_full = dorn_b.fuse(dorn_p)

# Zwei Einschmelz-Löcher im Dorn
dorn_full = dorn_full.cut(m3_insert.copy().translate(App.Vector(8.0, 0, 0)))
dorn_full = dorn_full.cut(m3_insert.copy().translate(App.Vector(-8.0, 0, 0)))

dorn_full = dorn_full.removeSplitter()
dorn_full.translate(App.Vector(80, 10, 0)) # Zum Drucken aufrecht abgestellt (Basis ist breit genug)
show_obj(dorn_full, "Rollen_Dorn_Steckbar")

# ==========================================
# DIE T-SCHIENE (Auf X = -45 verschoben!)
# ==========================================
t_stem = make_centered_box(6.0, 50, 5.0, -45, 25, 7.5)  
t_top = make_centered_box(12.0, 50, 5.0, -45, 25, 12.5) 
schiene = t_stem.fuse(t_top)

stop_1 = Part.makeCylinder(1.4, 10).translate(App.Vector(-45, 46, 8))
stop_2 = Part.makeCylinder(1.4, 10).translate(App.Vector(-45, 4, 8))
schiene = schiene.cut(stop_1).cut(stop_2)

basis = base_plate.fuse(schiene).removeSplitter()
show_obj(basis, "Maschinen_Basis_Modular")

# ==========================================
# RÄDER & SCHLITTEN (Für Druck abgelegt)
# ==========================================
rad_k = make_wheel(grosses_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(30, -30, 0.0)) 
show_obj(rad_k, "Rad_Gross_Kurbel")

rad_w = make_wheel(kleines_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(-10, -30, 0.0))
show_obj(rad_w, "Rad_Klein_Wickler")

# Führungsschlitten
sled = make_centered_box(24, 16, 25, 0, 0, 12.5)
cut_stem = make_centered_box(6.6, 16.0, 5.0, 0, 0, 2.5)   
cut_top = make_centered_box(12.6, 16.0, 5.5, 0, 0, 7.75)  

wire_hole = Part.makeCylinder(0.5, 30)
wire_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
sled = sled.cut(cut_stem).cut(cut_top).cut(wire_hole.translate(App.Vector(-15, 0, 20)))

sled.translate(App.Vector(-50, -30, 0)) 
show_obj(sled.removeSplitter(), "Schlitten_Drahtfuehrung_T_Form")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")