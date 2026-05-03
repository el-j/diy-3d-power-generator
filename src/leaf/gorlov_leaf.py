import FreeCAD as App
import Part
import math

# Neues Dokument erstellen
doc = App.newDocument("Gorlov_Modular_System")

# ==========================================
# ⚙️ PARAMETER
# ==========================================
# Allgemeine Maße
hohe = 240.0              # Gesamthöhe des Rotors
blatt_radius = 66.0       # Radius bis zur Mitte der Flügel
airfoil_chord = 16.0      # Breite des Flügels (Sehnenlänge)
airfoil_thickness = 3.4   # Dicke des Flügels
twist_winkel = 120.0      # Drehung der Flügel von unten nach oben
loft_steps = 48           

# Modulares Steck-System (Lego-Technic Style)
profil_size = 8.0         # 8x8mm Vierkant (für Alu-Profil oder Druckteil)
hub_radius = 22.0         # Radius der zentralen Naben-Scheibe
hub_hoehe = 14.0          # Höhe der Naben-Scheibe
einsteck_tiefe = 12.0     # Wie tief das Profil in die Nabe/Flügel gesteckt wird
pin_radius = 1.7          # 3.4mm Loch für M3 Schrauben/Bolzen zur Fixierung

# Verbinder / Achse (für den Turmbau)
achse_kantenlaenge = 10.0 
toleranz = 0.5            
kappen_dicke = 8.0        
vielzahn_zaehne = 12      
vielzahn_r_out = 9.0      
vielzahn_r_in = 7.8       

# ==========================================
# 🛠️ HILFSFUNKTIONEN
# ==========================================
def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

def make_vielzahn_prism(r_out, r_in, teeth, height):
    points = []
    for j in range(teeth * 2):
        angle = math.radians(j * (360.0 / (teeth * 2)) + 15)
        r = r_out if j % 2 == 0 else r_in
        points.append(App.Vector(r * math.cos(angle), r * math.sin(angle), 0))
    points.append(points[0])
    return Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def make_airfoil_wire(chord, thickness):
    x0 = -chord / 2.0
    x1 = chord / 2.0
    top_mid = App.Vector(0, thickness / 2.0, 0)
    bot_mid = App.Vector(0, -thickness / 2.0, 0)
    top = Part.Arc(App.Vector(x0, 0, 0), top_mid, App.Vector(x1, 0, 0)).toShape()
    bottom = Part.Arc(App.Vector(x1, 0, 0), bot_mid, App.Vector(x0, 0, 0)).toShape()
    return Part.Wire([top, bottom])

def make_gorlov_blade(radius, chord, thickness, height, twist_deg, steps, base_angle_deg):
    base = make_airfoil_wire(chord, thickness)
    wires = []
    for i in range(steps + 1):
        z = height * (float(i) / float(steps))
        ang = base_angle_deg + twist_deg * (float(i) / float(steps))
        wire = base.copy()
        wire.translate(App.Vector(radius, 0, 0))
        wire.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), ang)
        wire.translate(App.Vector(0, 0, z))
        wires.append(wire)
    return Part.makeLoft(wires, True)

# ==========================================
# 🚀 1. MODULARE NABEN-SCHEIBE (2x drucken!)
# ==========================================
print("Generiere modulare Naben-Scheibe...")
hub = Part.makeCylinder(hub_radius, hub_hoehe)

# Zentrale 10x10 Achse
achse_cut = make_square_prism(achse_kantenlaenge + toleranz, hub_hoehe + 10.0)
achse_cut.translate(App.Vector(0, 0, -5.0))
hub = hub.cut(achse_cut)

# Steckdosen (Sockets) und Pin-Löcher
for i in range(3):
    angle = i * 120.0
    # Cutter für die Profil-Tasche (reicht von Mitte nach außen)
    sock_w = profil_size + toleranz
    socket = Part.makeBox(einsteck_tiefe + 5.0, sock_w, sock_w)
    socket.translate(App.Vector(hub_radius - einsteck_tiefe, -sock_w/2.0, (hub_hoehe - sock_w)/2.0))
    socket.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    # M3 Verschraubungsloch von oben nach unten
    pin_r_pos = hub_radius - (einsteck_tiefe / 2.0)
    pin_hole = Part.makeCylinder(pin_radius, hub_hoehe + 10.0)
    pin_hole.translate(App.Vector(pin_r_pos, 0, -5.0))
    pin_hole.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    hub = hub.cut(socket).cut(pin_hole)

hub = hub.removeSplitter()
show_obj(hub, "Hub_Scheibe_Unten")

# Eine Kopie für Oben generieren (inkl. Rotation um twist_winkel!)
hub_top = hub.copy()
hub_top.rotate(App.Vector(0,0,0), App.Vector(0,0,1), twist_winkel)
hub_top.translate(App.Vector(0, 0, hohe - hub_hoehe))
show_obj(hub_top, "Hub_Scheibe_Oben")

# ==========================================
# 🚀 2. FLÜGEL MIT EINSTECK-HALTERUNGEN
# ==========================================
print("Generiere modulare Flügel...")
mount_length = 16.0
mount_width = profil_size + 6.0    
mount_hoehe = profil_size + 6.0    
blade_sock_tiefe = 12.0

def make_blade_mount(z_pos, angle_deg):
    # Basis-Block der an den Flügel gegossen wird
    block = Part.makeBox(mount_length, mount_width, mount_hoehe)
    block_x = blatt_radius - mount_length + 1.0 # Leichte Überschneidung mit dem Flügel
    block.translate(App.Vector(block_x, -mount_width/2.0, 0))
    
    # Socket Cut von innen in den Block
    sock_w = profil_size + toleranz
    sock_end_x = block_x + blade_sock_tiefe
    socket = Part.makeBox(sock_end_x, sock_w, sock_w)
    socket.translate(App.Vector(0, -sock_w/2.0, (mount_hoehe - sock_w)/2.0))
    block = block.cut(socket)
    
    # M3 Verschraubungsloch
    pin_x = block_x + (blade_sock_tiefe / 2.0)
    pin_hole = Part.makeCylinder(pin_radius, mount_hoehe + 10.0)
    pin_hole.translate(App.Vector(pin_x, 0, -5.0))
    block = block.cut(pin_hole)
    
    # Positionieren
    block.translate(App.Vector(0, 0, z_pos))
    block.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
    return block

for i in range(3):
    base_angle = i * 120.0
    blade = make_gorlov_blade(
        blatt_radius, airfoil_chord, airfoil_thickness, 
        hohe, twist_winkel, loft_steps, base_angle
    )
    
    mount_bottom = make_blade_mount(0, base_angle)
    mount_top = make_blade_mount(hohe - mount_hoehe, base_angle + twist_winkel)
    
    blade = blade.fuse(mount_bottom).fuse(mount_top).removeSplitter()
    show_obj(blade, f"Gorlov_Blade_Modul_{i+1}")


# ==========================================
# 🚀 3. DRUCKBARE STREBE (Ersatz für Alu-Profil)
# ==========================================
# Distanz-Berechnung:
# Start in Hub: Radius = 10.0, Ende in Blade: Radius = 63.0. Gesamtlänge = 53.0
# Wir nehmen 52.0 für 0.5mm Spiel an beiden Seiten, damit nichts klemmt.
strut_length = 52.0

strut = Part.makeBox(strut_length, profil_size - 0.2, profil_size - 0.2)
strut.translate(App.Vector(0, -(profil_size - 0.2)/2.0, -(profil_size - 0.2)/2.0))

# Löcher exakt bohren
# Hub Loch ist bei R=16. Strut Start ist R=10.5 => Distanz 5.5mm
# Blade Loch ist bei R=57. Strut Ende ist R=62.5 => Distanz 5.5mm
for hole_x in [5.5, strut_length - 5.5]:
    hole = Part.makeCylinder(pin_radius, profil_size + 5.0)
    hole.translate(App.Vector(hole_x, 0, -(profil_size + 5.0)/2.0))
    strut = strut.cut(hole)

strut.translate(App.Vector(blatt_radius + 20, 0, 0))
show_obj(strut, "Strebe_8x8_Alu_Ersatz")


# ==========================================
# 🚀 4. VERBINDER-RING & PLUG (Wie gehabt)
# ==========================================
connector = Part.makeCylinder(blatt_radius + 6.0, kappen_dicke)
connector = connector.cut(Part.makeCylinder(13.0, kappen_dicke))
connector = connector.cut(make_vielzahn_prism(
    vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, kappen_dicke
))
connector.translate(App.Vector((blatt_radius + 15.0) * 2.3, 0, 0))
show_obj(connector, "Gorlov_Connector_Ring")

plug = make_vielzahn_prism(vielzahn_r_out, vielzahn_r_in, vielzahn_zaehne, kappen_dicke)
shaft_cut = make_square_prism(achse_kantenlaenge + toleranz, kappen_dicke + 2.0)
shaft_cut.translate(App.Vector(0, 0, -1.0))
plug = plug.cut(shaft_cut)
plug.translate(App.Vector((blatt_radius + 15.0) * 2.3, 36.0, 0))
show_obj(plug, "Gorlov_Spline_Plug")

# ==========================================
# Ansicht aktualisieren
# ==========================================
doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Modulares Gorlov System erfolgreich generiert!")