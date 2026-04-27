import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Basis_Raeder")

# ==========================================
# ⚙️ PARAMETER (Teil 1: Basis & Räder)
# ==========================================
hex_loch_sw = 8.4         
lager_loch_d = 9.8        
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
# BAUTEIL 1: DIE MASCHINEN-BASIS (Tischkanten-Layout!)
# ==========================================
base_plate = make_centered_box(160, 100, 5, 0, 0, 2.5) # Y von -50 bis 50

def make_crank_pillar(cx, cy):
    p = make_centered_box(16, 12, 55, cx, cy, 32.5) 
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 15)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    cut_cyl.translate(App.Vector(cx, cy+7.5, 45)) 
    return p.cut(cut_cyl)

def make_spool_pillar(cx, cy):
    p = make_centered_box(16, 12, 40, cx, cy, 25) 
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 15)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    cut_cyl.translate(App.Vector(cx, cy+7.5, 30)) 
    return p.cut(cut_cyl)

# Türme jetzt ganz hinten an der Tischkante (Y=15 und Y=40)
p_cl = make_crank_pillar(-45, 40) 
p_cr = make_crank_pillar(-45, 15)  

p_wl = make_spool_pillar(0, 40)  
p_wr = make_spool_pillar(0, 15)   

# 3. Die T-Träger-Schiene (Perfekt auf den Schlitten abgestimmt!)
t_stem = make_centered_box(7.0, 45, 4.5, 35, -15, 7.25) # Z: 5 bis 9.5
t_top = make_centered_box(13.0, 45, 5.0, 35, -15, 12.0) # Z: 9.5 bis 14.5
schiene = t_stem.fuse(t_top)

stop_1 = Part.makeCylinder(1.4, 10).translate(App.Vector(35, 5, 8))
stop_2 = Part.makeCylinder(1.4, 10).translate(App.Vector(35, -35, 8))
schiene = schiene.cut(stop_1).cut(stop_2)

# 4. Dorn für die Kupferdraht-Rolle
dorn_base = Part.makeCylinder(15, 2).translate(App.Vector(65, -15, 5))
dorn = Part.makeCylinder(4.5, 60).translate(App.Vector(65, -15, 7))

basis = base_plate.fuse(p_wl).fuse(p_wr).fuse(p_cl).fuse(p_cr).fuse(dorn_base).fuse(dorn).fuse(schiene)
show_obj(basis.removeSplitter(), "Maschinen_Basis")

# ==========================================
# BAUTEILE 2 & 3: RÄDER & SCHLITTEN (Für Druck abgelegt)
# ==========================================
rad_k = make_wheel(grosses_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(-45, -90, 0.0)) 
show_obj(rad_k, "Rad_Gross_Kurbel")

rad_w = make_wheel(kleines_rad_d, 1.5, hex_loch_sw, 10.0).translate(App.Vector(0, -90, 0.0))
show_obj(rad_w, "Rad_Klein_Wickler")

sled = make_centered_box(24, 16, 20, 0, 0, 10)
cut_stem = make_centered_box(7.5, 16.0, 4.5, 0, 0, 2.25) 
cut_top = make_centered_box(13.5, 16.0, 5.0, 0, 0, 7.0) 
wire_hole = Part.makeCylinder(0.5, 24)
wire_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)

sled = sled.cut(cut_stem).cut(cut_top).cut(wire_hole.translate(App.Vector(-12, 0, 15)))
sled.translate(App.Vector(35, -90, 0)) 
show_obj(sled.removeSplitter(), "Schlitten_Drahtfuehrung_T_Form")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")