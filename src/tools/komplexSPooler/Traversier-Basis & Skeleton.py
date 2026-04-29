import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Ortho_Basis")

# ==========================================
# ⚙️ PARAMETER (Kompakte Basis)
# ==========================================
hex_loch_sw = 8.4         
lager_loch_d = 12.0        
zahnrad_dicke = 8.0      
achse_z = 75.0
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_capsule_cut(l, w, h, cx, cy, cz):
    r = w / 2.0
    d = l - w
    if d < 0: d = 0
    offset = d / 2.0
    cyl1 = Part.makeCylinder(r, h).translate(App.Vector(cx + offset, cy, cz))
    cyl2 = Part.makeCylinder(r, h).translate(App.Vector(cx - offset, cy, cz))
    box = Part.makeBox(d, w, h)
    box.translate(App.Vector(cx - offset, cy - r, cz))
    return cyl1.fuse(cyl2).fuse(box)

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
    module = (2.0 * pitch_radius) / num_teeth
    r_out = pitch_radius + module
    r_root = pitch_radius - (1.25 * module)
    pitch_angle = 360.0 / num_teeth
    angle_tip = 0.25 * pitch_angle   
    angle_root = 0.50 * pitch_angle  
    
    points = []
    for i in range(num_teeth):
        center_angle = i * pitch_angle
        a1 = math.radians(center_angle - angle_root/2.0)
        a2 = math.radians(center_angle - angle_tip/2.0)
        a3 = math.radians(center_angle + angle_tip/2.0)
        a4 = math.radians(center_angle + angle_root/2.0)
        
        points.append(App.Vector(r_root * math.cos(a1), r_root * math.sin(a1), 0))
        points.append(App.Vector(r_out * math.cos(a2), r_out * math.sin(a2), 0))
        points.append(App.Vector(r_out * math.cos(a3), r_out * math.sin(a3), 0))
        points.append(App.Vector(r_root * math.cos(a4), r_root * math.sin(a4), 0))
        
        a5 = math.radians(center_angle + pitch_angle/2.0)
        points.append(App.Vector(r_root * math.cos(a5), r_root * math.sin(a5), 0))
        
    points.append(points[0])
    wire = Part.Wire(Part.makePolygon(points))
    gear = Part.Face(wire).extrude(App.Vector(0,0,thickness))
    
    hole = make_hex_prism(hex_sw, thickness + 10.0).translate(App.Vector(0,0,-5.0))
    gear = gear.cut(hole)
    
    if pitch_radius >= 20.0:
        spokes = 6
        hole_dist = pitch_radius * 0.6  
        hole_r = pitch_radius * 0.25    
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
# 1. BAUTEIL: FUNDAMENT (Kompakt, Y=130mm tief)
# ==========================================
base_plate = make_centered_box(200, 130, 5, -50.0, 60.0, 2.5)

# --- SKELETON BODENPLATTE ---
def add_base_capsule(cx, cy, l, w):
    global base_plate
    pocket = make_capsule_cut(l, w, 3.0, cx, cy, 0)
    base_plate = base_plate.cut(pocket)

# Reihe 1: Vordere Aussparungen (Y=20)
add_base_capsule(10, 20, 35, 18)
add_base_capsule(-40, 20, 35, 18)
add_base_capsule(-90, 20, 35, 18)
add_base_capsule(-135, 20, 20, 18)

# Reihe 2: Aussparungen zwischen den Türmen (Y=60)
add_base_capsule(10, 60, 35, 12)
add_base_capsule(-40, 60, 35, 12)
add_base_capsule(-80, 60, 18, 12)
add_base_capsule(-120, 60, 18, 12)

# Reihe 3: Hintere Aussparungen (Y=115) - T-Schiene liegt bei Y=95!
add_base_capsule(10, 115, 35, 12)
add_base_capsule(-40, 115, 35, 12)
add_base_capsule(-90, 115, 35, 12)
add_base_capsule(-135, 115, 20, 12)

recess_depth = 1.5
base_z_top = 5.0
pillar_bottom_z = base_z_top - recess_depth 

m3_through = Part.makeCylinder(1.7, 10.0).translate(App.Vector(0,0,-2)) 
m3_head_sink = Part.makeCylinder(3.0, 3.1) 
m3_insert = Part.makeCylinder(2.1, 5.0) 

def create_pluggable_pillar(name, cx, cy, pr_x, pr_y):
    global base_plate
    pocket = make_centered_box(16.4, 12.4, recess_depth, cx, cy, base_z_top - (recess_depth/2.0))
    base_plate = base_plate.cut(pocket)
    
    # DIAGONALE VERSCHRAUBUNG
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx + 4.5, cy + 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx + 4.5, cy + 3.0, 0)))
    base_plate = base_plate.cut(m3_through.copy().translate(App.Vector(cx - 4.5, cy - 3.0, 0)))
    base_plate = base_plate.cut(m3_head_sink.copy().translate(App.Vector(cx - 4.5, cy - 3.0, 0)))
    
    local_h = achse_z + 10.0 - pillar_bottom_z 
    local_hz = achse_z - pillar_bottom_z
    p = make_centered_box(16, 12, local_h, 0, 0, local_h/2.0)
    
    cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 18)
    cut_cyl.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    p = p.cut(cut_cyl.translate(App.Vector(0, 9.0, local_hz)))
    
    p = p.cut(m3_insert.copy().translate(App.Vector(4.5, 3.0, 0)))
    p = p.cut(m3_insert.copy().translate(App.Vector(-4.5, -3.0, 0)))

    cut_h = local_h - 36.0 
    if cut_h > 0:
        pillar_cut = make_centered_box(7.0, 20.0, cut_h, 0, 0, 16.0 + cut_h/2.0)
        p = p.cut(pillar_cut)

    insert_top = Part.makeCylinder(4.2 / 2.0, 5.0)
    screw_clearance = Part.makeCylinder(1.7, 15.0)
    p = p.cut(insert_top.translate(App.Vector(0, 0, local_h - 5.0)))
    p = p.cut(screw_clearance.translate(App.Vector(0, 0, local_h - 15.0)))

    p = p.removeSplitter()
    p.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
    p.translate(App.Vector(pr_x, pr_y, 6.0)) 
    show_obj(p, name)

# 4 ACHSEN IN REIHE (Türme liegen jetzt eng beieinander)
create_pluggable_pillar("Turm_1_Kurbel_V",   35, 45,  -130, 150)
create_pluggable_pillar("Turm_1_Kurbel_H",   35, 75,  -130, 250)

create_pluggable_pillar("Turm_2_Spule_V",   -15, 45,  -100, 150)
create_pluggable_pillar("Turm_2_Spule_H",   -15, 75,  -100, 250)

create_pluggable_pillar("Turm_3_Int_V",     -65, 45,  -70, 150)
create_pluggable_pillar("Turm_3_Int_H",     -65, 75,  -70, 250)

create_pluggable_pillar("Turm_4_Cam_V",    -135, 45,  -40, 150)
create_pluggable_pillar("Turm_4_Cam_H",    -135, 75,  -40, 250)

# ==========================================
# 2. BASIS FINALISIEREN (T-Schiene entfernt!)
# ==========================================
basis = base_plate.removeSplitter()
show_obj(basis, "Maschinen_Basis_Kompakt")

# ==========================================
# 3. ZAHNRÄDER (1:24 Ratio!)
# ==========================================
# Die Zahnräder werden flach auf das Druckbett generiert
rad_kurbel = make_gear(40.0, zahnrad_dicke, 40, hex_loch_sw).translate(App.Vector(35, -70, 0)) 
show_obj(rad_kurbel, "Z1_Kurbel_40Z")

rad_spule_fast = make_gear(10.0, zahnrad_dicke, 10, hex_loch_sw).translate(App.Vector(-15, -70, 0))
rad_spule_sync = make_gear(10.0, zahnrad_dicke, 10, hex_loch_sw).translate(App.Vector(-15, -40, 0))
show_obj(rad_spule_fast, "Z2_Spule_In_10Z")
show_obj(rad_spule_sync, "Z3_Spule_Out_10Z")

rad_int_in = make_gear(40.0, zahnrad_dicke, 40, hex_loch_sw).translate(App.Vector(-65, -70, 0))
rad_int_out = make_gear(10.0, zahnrad_dicke, 10, hex_loch_sw).translate(App.Vector(-65, -20, 0))
show_obj(rad_int_in, "Z4_Zwischen_In_40Z")
show_obj(rad_int_out, "Z5_Zwischen_Out_10Z")

rad_cam = make_gear(60.0, zahnrad_dicke, 60, hex_loch_sw).translate(App.Vector(-145, -80, 0))
show_obj(rad_cam, "Z6_Trommel_60Z")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")