import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Virtueller_Aufbau")

# ==========================================
# ⚙️ GLOBALE PARAMETER
# ==========================================
achse_z = 75.0
hex_loch_sw = 8.4
hex_achse_sw = 8.0
quad_spindel_sw = 6.0
lager_loch_d = 12.0

# ==========================================
# 🛠️ HILFSFUNKTIONEN FÜR GEOMETRIE
# ==========================================
def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
    radius = (sw / 2.0) / math.cos(math.radians(30))
    points = [App.Vector(radius * math.cos(math.radians(60*j+30)), radius * math.sin(math.radians(60*j+30)), 0) for j in range(6)]
    points.append(points[0])
    return Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    return Part.makeBox(size, size, height).translate(App.Vector(-size/2.0, -size/2.0, 0))

def make_gear(pitch_radius, thickness, num_teeth, hex_sw):
    module = (2.0 * pitch_radius) / num_teeth
    r_out = pitch_radius + module
    r_root = pitch_radius - (1.25 * module)
    pitch_angle = 360.0 / num_teeth
    angle_tip, angle_root = 0.25 * pitch_angle, 0.50 * pitch_angle  
    
    points = []
    for i in range(num_teeth):
        ca = i * pitch_angle
        points.append(App.Vector(r_root * math.cos(math.radians(ca - angle_root/2.0)), r_root * math.sin(math.radians(ca - angle_root/2.0)), 0))
        points.append(App.Vector(r_out * math.cos(math.radians(ca - angle_tip/2.0)), r_out * math.sin(math.radians(ca - angle_tip/2.0)), 0))
        points.append(App.Vector(r_out * math.cos(math.radians(ca + angle_tip/2.0)), r_out * math.sin(math.radians(ca + angle_tip/2.0)), 0))
        points.append(App.Vector(r_root * math.cos(math.radians(ca + angle_root/2.0)), r_root * math.sin(math.radians(ca + angle_root/2.0)), 0))
        points.append(App.Vector(r_root * math.cos(math.radians(ca + pitch_angle/2.0)), r_root * math.sin(math.radians(ca + pitch_angle/2.0)), 0))
    points.append(points[0])
    
    gear = Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0,0,thickness))
    gear = gear.cut(make_hex_prism(hex_sw, thickness + 10.0).translate(App.Vector(0,0,-5.0)))
    return gear.removeSplitter()

def add_part(shape, name, color):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if App.GuiUp:
        obj.ViewObject.ShapeColor = color
    return obj

# ==========================================
# 1. RAHMEN & BASIS (Kompakte Variante)
# ==========================================
COLOR_FRAME = (0.25, 0.25, 0.25)
# Basis reicht bis Y=120, um die Schiene hinten abzustützen
base_plate = make_centered_box(200, 130, 5, -50.0, 60.0, 2.5) 

# T-Schiene (Sitzt jetzt zwischen Achse 3 und 4, exakt auf Y=95!)
t_stem = make_centered_box(6.0, 60, 5.0, -100, 95, 7.5)
t_top = make_centered_box(12.0, 60, 5.0, -100, 95, 12.5)
base_plate = base_plate.fuse(t_stem).fuse(t_top)
add_part(base_plate.removeSplitter(), "1_Basis_Kompakt", COLOR_FRAME)

# Türme (Stehen zentral bei Y=45 und Y=75)
for cx in [35, -15, -65, -135]:
    for cy in [45, 75]:
        local_h = achse_z + 10.0 - 3.5 
        turm = make_centered_box(16, 12, local_h, cx, cy, 3.5 + local_h/2.0)
        cut_cyl = Part.makeCylinder(lager_loch_d / 2.0, 18).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
        turm = turm.cut(cut_cyl.translate(App.Vector(cx, cy + 9.0, achse_z)))
        add_part(turm.removeSplitter(), f"1_Turm_{cx}_{cy}", COLOR_FRAME)

# Obergurte
for cy in [45, 75]:
    traeger = make_centered_box(190-12, 12, 6, -50, cy, achse_z + 10.0 + 3.0)
    add_part(traeger, f"1_Traeger_{cy}", (0.5, 0.5, 0.5))

# ==========================================
# 2. ACHSEN (Silber)
# ==========================================
COLOR_AXIS = (0.8, 0.8, 0.8)
# Kurbel Achse
a1 = make_hex_prism(hex_achse_sw, 110.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(35, -5, achse_z))

# Spulen Achse (Quad-Bereich hinten für die Spule, Y=80 bis 115)
a2_hex = make_hex_prism(hex_achse_sw, 80.0)
a2_quad = make_square_prism(quad_spindel_sw, 35.0).translate(App.Vector(0,0,80.0))
a2 = a2_hex.fuse(a2_quad).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(-15, -5, achse_z))

# Getriebe Achse
a3 = make_hex_prism(hex_achse_sw, 110.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(-65, -5, achse_z))

# Trommel Achse (Hex-Bereich reicht bis Y=115 für die Trommel)
a4 = make_hex_prism(hex_achse_sw, 120.0).rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(-135, -5, achse_z))

add_part(a1, "2_Achse_1", COLOR_AXIS)
add_part(a2, "2_Achse_2", COLOR_AXIS)
add_part(a3, "2_Achse_3", COLOR_AXIS)
add_part(a4, "2_Achse_4", COLOR_AXIS)

# ==========================================
# 3. ANTRIEBSSTRANG VORNE (Blau) - 1:24 Ratio
# ==========================================
COLOR_GEAR = (0.1, 0.4, 0.7)
add_part(make_gear(40, 8, 40, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(35, 30, achse_z)), "3_Z1_40Z", COLOR_GEAR)
add_part(make_gear(10, 8, 10, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(-15, 30, achse_z)), "3_Z2_10Z", COLOR_GEAR)
add_part(make_gear(10, 8, 10, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(-15, 15, achse_z)), "3_Z3_10Z", COLOR_GEAR)
add_part(make_gear(40, 8, 40, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(-65, 15, achse_z)), "3_Z4_40Z", COLOR_GEAR)
add_part(make_gear(10, 8, 10, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(-65, 30, achse_z)), "3_Z5_10Z", COLOR_GEAR)
add_part(make_gear(60, 8, 60, hex_loch_sw).rotate(App.Vector(0,0,0),App.Vector(1,0,0),90).translate(App.Vector(-135, 30, achse_z)), "3_Z6_60Z", COLOR_GEAR)

# ==========================================
# 4. TAUMEL-TROMMEL (Grün) - AUSSEN MONTIERT
# ==========================================
COLOR_GUIDE = (0.2, 0.8, 0.2)

def make_wobble_drum():
    # Massiver Zylinder mit schrägem Spalt (Nut)
    drum = Part.makeCylinder(20.0, 20.0)
    slot = Part.makeBox(50, 50, 2.5).translate(App.Vector(-25, -25, -1.25))
    slot.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 10.0) # 10 Grad Neigung
    slot.translate(App.Vector(0,0, 10.0))
    
    drum = drum.cut(slot)
    drum = drum.cut(make_hex_prism(hex_loch_sw, 25).translate(App.Vector(0,0,-2)))
    return drum.removeSplitter()

drum = make_wobble_drum()
drum.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
drum.translate(App.Vector(-135, 85, achse_z)) # Zentriert exakt auf Y=95!
add_part(drum, "4_Taumel_Trommel", COLOR_GUIDE)

# ==========================================
# 5. U-SCHLITTEN (Grün) - UMGREIFT DIE TÜRME
# ==========================================
# Basis auf der T-Schiene
sled_base = make_centered_box(30, 20, 22, -100, 95, 21.0)

# Linker Arm: Fährt in die Nut der Trommel (-X Richtung)
arm_l_bridge = make_centered_box(15, 10, 10, -107.5, 95, 26.0) 
arm_l_up = make_centered_box(10, 10, 49, -115, 95, 50.5) 
# Führungs-Pin in die Trommel (2mm Durchmesser, passt perfekt in 2.5mm Nut)
pin = Part.makeCylinder(1.0, 6.0).rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90).translate(App.Vector(-115, 95, 75))
arm_l = arm_l_bridge.fuse(arm_l_up).fuse(pin)

# Rechter Arm: Fährt über die Spule zur Drahtführung (+X Richtung)
arm_r_bridge = make_centered_box(85, 10, 10, -57.5, 95, 26.0) 
arm_r_up = make_centered_box(10, 10, 59, -15, 95, 55.5) 
# Drahtloch (Zeigt in Y-Richtung, damit der Draht von hinten kommt und exakt auf die Spule fällt)
wire_hole = Part.makeCylinder(1.0, 20).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90).translate(App.Vector(-15, 105, 80))
arm_r = arm_r_bridge.fuse(arm_r_up).cut(wire_hole)

full_sled = sled_base.fuse(arm_l).fuse(arm_r).removeSplitter()
add_part(full_sled, "4_Schlitten_U_Form", COLOR_GUIDE)

# ==========================================
# 6. SPULE & KURBEL (Orange)
# ==========================================
COLOR_TOOL = (0.9, 0.4, 0.1)

# Ovale Kapsel-Spule (Außen auf dem Vierkant montiert, zentriert auf Y=95)
kapsel = Part.makeCylinder(22, 3).fuse(Part.makeCylinder(7, 12).translate(App.Vector(0,0,3))).fuse(Part.makeCylinder(22, 3).translate(App.Vector(0,0,9)))
kapsel = kapsel.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90).translate(App.Vector(-15, 89, achse_z))
add_part(kapsel, "5_Spule_Montiert", COLOR_TOOL)

# Kurbel (Ganz vorne)
kurbel = make_centered_box(40, 14, 6, 35 - 20, 0, achse_z).fuse(Part.makeCylinder(6, 30).rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90).translate(App.Vector(0, 0, achse_z)))
add_part(kurbel, "5_Kurbel", COLOR_TOOL)

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")