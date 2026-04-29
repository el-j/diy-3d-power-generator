import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Basis_Raeder")

# ==========================================
# ⚙️ PARAMETER (Basis & ZAHNRÄDER)
# ==========================================
hex_loch_sw = 8.4         
lager_loch_d = 12.0        
# Abstand der Türme in der Basis ist exakt 50mm!
# Radius 40mm (Groß) + Radius 10mm (Klein) = 50mm! Perfekter Eingriff!
zahnrad_dicke = 10.0      
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

def make_gear(pitch_radius, thickness, num_teeth, hex_sw):
    # ECHTER POLYGON-GENERATOR (Perfekt für den 3D-Druck!)
    module = (2.0 * pitch_radius) / num_teeth
    r_out = pitch_radius + module
    r_root = pitch_radius - (1.25 * module)
    
    pitch_angle = 360.0 / num_teeth
    
    # Zahn-Proportionen (Optimiert für 0.6mm Nozzle & reibungslosen Lauf)
    # Die Zähne sind an der Spitze schmal und an der Wurzel breit, das garantiert perfekten Mesh!
    angle_tip = 0.25 * pitch_angle   
    angle_root = 0.50 * pitch_angle  
    
    points = []
    for i in range(num_teeth):
        center_angle = i * pitch_angle
        
        # Die 4 Ecken eines jeden Zahns berechnen
        a1 = math.radians(center_angle - angle_root/2.0)
        a2 = math.radians(center_angle - angle_tip/2.0)
        a3 = math.radians(center_angle + angle_tip/2.0)
        a4 = math.radians(center_angle + angle_root/2.0)
        
        points.append(App.Vector(r_root * math.cos(a1), r_root * math.sin(a1), 0))
        points.append(App.Vector(r_out * math.cos(a2), r_out * math.sin(a2), 0))
        points.append(App.Vector(r_out * math.cos(a3), r_out * math.sin(a3), 0))
        points.append(App.Vector(r_root * math.cos(a4), r_root * math.sin(a4), 0))
        
        # Ein Punkt in der Mitte der Zahnlücke, um den Boden schön abzurunden
        a5 = math.radians(center_angle + pitch_angle/2.0)
        points.append(App.Vector(r_root * math.cos(a5), r_root * math.sin(a5), 0))
        
    points.append(points[0]) # Polygon schließen
    
    # Zahnrad extrudieren
    wire = Part.Wire(Part.makePolygon(points))
    gear = Part.Face(wire).extrude(App.Vector(0,0,thickness))
    
    # ZU 100% FLACH! Keine Nabe (Hub) mehr!
    # Die Kragen der Lagerhülsen in den Türmen dienen nun als alleinige Abstandshalter.
    
    # Sechskant-Loch zum sicheren Ausstanzen der Mitte
    hole = make_hex_prism(hex_sw, thickness + 10.0).translate(App.Vector(0,0,-5.0))
    gear = gear.cut(hole)
    
    # === NEU: MATERIALSPARENDE LÖCHER (Lego Technic Style) ===
    # Nur für große Zahnräder anwenden (Radius >= 20mm), das kleine Rad bleibt massiv.
    if pitch_radius >= 20.0:
        spokes = 6
        hole_dist = pitch_radius * 0.6  # Zentren der Löcher bei 60% des Radius
        hole_r = pitch_radius * 0.25    # Radius der Löcher ist 25% des Zahnrad-Radius
        
        for i in range(spokes):
            angle = math.radians(i * (360.0 / spokes))
            hx = hole_dist * math.cos(angle)
            hy = hole_dist * math.sin(angle)
            cyl = Part.makeCylinder(hole_r, thickness + 4.0).translate(App.Vector(hx, hy, -2.0))
            gear = gear.cut(cyl)
            
    return gear.removeSplitter()

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DIE MASCHINEN-BASIS (Modulares Fundament)
# ==========================================
base_right = make_centered_box(75, 100, 5, 12.5, 45, 2.5) 
base_left = make_centered_box(60, 60, 5, -55.0, 25, 2.5)
base_plate = base_right.fuse(base_left)

m4_loch = Part.makeCylinder(2.2, 10)
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(40, 85, -2)))  
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(40, 5, -2)))   
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(-80, 5, -2)))  
base_plate = base_plate.cut(m4_loch.copy().translate(App.Vector(-80, 45, -2))) 

recess_depth = 1.5
base_z_top = 5.0
pillar_bottom_z = base_z_top - recess_depth 

m3_through = Part.makeCylinder(1.7, 10.0).translate(App.Vector(0,0,-2)) 
m3_head_sink = Part.makeCylinder(3.0, 3.1) 
m3_insert = Part.makeCylinder(2.1, 5.0) 

def create_pluggable_pillar(name, cx, cy, target_top_z, target_hole_z, pr_x, pr_y):
    global base_plate
    
    pocket = make_centered_box(16.4, 12.4, recess_depth, cx, cy, base_z_top - (recess_depth/2.0))
    base_plate = base_plate.cut(pocket)
    
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx, cy + 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx, cy + 3.0, 0)))
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx, cy - 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx, cy - 3.0, 0)))
    
    local_h = target_top_z - pillar_bottom_z
    local_hz = target_hole_z - pillar_bottom_z
    p = make_centered_box(16, 12, local_h, 0, 0, local_h/2.0)
    
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 18)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    p = p.cut(cut_cyl.translate(App.Vector(0, 9.0, local_hz)))
    
    p = p.cut(m3_insert.copy().translate(App.Vector(0, 3.0, 0)))
    p = p.cut(m3_insert.copy().translate(App.Vector(0, -3.0, 0)))
    p = p.removeSplitter()
    
    p.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
    p.translate(App.Vector(pr_x, pr_y, 6.0)) 
    show_obj(p, name)

create_pluggable_pillar("Turm_Kurbel_Vorne",   35, 45, 55, 45,  70, 80)
create_pluggable_pillar("Turm_Kurbel_Hinten",  35, 71, 55, 45,  70, 50)
create_pluggable_pillar("Turm_Wickler_Vorne", -15, 45, 40, 30,  90, 80)
create_pluggable_pillar("Turm_Wickler_Hinten",-15, 71, 40, 30,  90, 50)

dcx, dcy = -68, 25 
pocket_dorn = Part.makeCylinder(15.3, recess_depth).translate(App.Vector(dcx, dcy, base_z_top - recess_depth))
base_plate = base_plate.cut(pocket_dorn)

base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(dcx + 8.0, dcy, 0)))
base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(dcx + 8.0, dcy, 0)))
base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(dcx - 8.0, dcy, 0)))
base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(dcx - 8.0, dcy, 0)))

dorn_b = Part.makeCylinder(15, 2.0 + recess_depth)
dorn_p = Part.makeCylinder(4.5, 60).translate(App.Vector(0,0,2.0 + recess_depth))
dorn_full = dorn_b.fuse(dorn_p)
dorn_full = dorn_full.cut(m3_insert.copy().translate(App.Vector(8.0, 0, 0)))
dorn_full = dorn_full.cut(m3_insert.copy().translate(App.Vector(-8.0, 0, 0)))
dorn_full = dorn_full.removeSplitter()
dorn_full.translate(App.Vector(80, 10, 0)) 
show_obj(dorn_full, "Rollen_Dorn_Steckbar")

t_stem = make_centered_box(6.0, 50, 5.0, -45, 25, 7.5)  
t_top = make_centered_box(12.0, 50, 5.0, -45, 25, 12.5) 
schiene = t_stem.fuse(t_top)
stop_1 = Part.makeCylinder(1.4, 10).translate(App.Vector(-45, 46, 8))
stop_2 = Part.makeCylinder(1.4, 10).translate(App.Vector(-45, 4, 8))
schiene = schiene.cut(stop_1).cut(stop_2)

basis = base_plate.fuse(schiene).removeSplitter()
show_obj(basis, "Maschinen_Basis_Modular")

# ==========================================
# DIE NEUEN ZAHNRÄDER (Exakt 50mm Achsabstand, 100% flach!)
# ==========================================
# Kurbel-Rad: 40 Zähne, 40mm Radius.
rad_k = make_gear(40.0, zahnrad_dicke, 40, hex_loch_sw).translate(App.Vector(30, -45, 0.0)) 
show_obj(rad_k, "Zahnrad_Gross_Kurbel_40Z")

# Wickler-Rad: 10 Zähne, 10mm Radius. 
# Zähne passend rotiert für perfekten Mesh bei der Montage!
rad_w = make_gear(10.0, zahnrad_dicke, 10, hex_loch_sw)
rad_w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 18) # 18 Grad = Ein halber Zahn Versatz
rad_w.translate(App.Vector(-25, -45, 0.0))
show_obj(rad_w, "Zahnrad_Klein_Wickler_10Z")

# ==========================================
# SCHLITTEN
# ==========================================
sled = make_centered_box(24, 16, 25, 0, 0, 12.5)
cut_stem = make_centered_box(6.6, 16.0, 5.0, 0, 0, 2.5)   
cut_top = make_centered_box(12.6, 16.0, 5.5, 0, 0, 7.75)  

wire_hole = Part.makeCylinder(0.5, 30)
wire_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
sled = sled.cut(cut_stem).cut(cut_top).cut(wire_hole.translate(App.Vector(-15, 0, 20)))

sled.translate(App.Vector(-50, -45, 0)) 
show_obj(sled.removeSplitter(), "Schlitten_Drahtfuehrung_T_Form")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")