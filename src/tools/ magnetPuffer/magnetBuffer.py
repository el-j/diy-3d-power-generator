import FreeCAD as App
import Part
import math

doc = App.newDocument("Wickelmaschine_Magnet_Spanner")

# ==========================================
# ⚙️ PARAMETER (Gizeh Magnet Puffer V4 - Pro Edition)
# ==========================================
magnet_d = 5.3        
magnet_tiefe = 6.0    # Platz um 2-3 Magnete pro Loch zu stapeln

basis_breite = 42.0   # EXTRA BREIT: Damit Schrauben nicht in die Nut ragen!
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_hex_prism(sw, height):
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

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# 1. DIE BASIS (Schiene + Filz-Bremse)
# ==========================================
# Massive Grundplatte (Länge 170mm, X=-85 bis 85)
base = make_centered_box(170, basis_breite, 18, 0, 0, 9.0)

# A) DIE T-NUT SCHIENE (Nach rechts offen!)
track_bot = make_centered_box(160, 20.5, 6.0, 10, 0, 7.0)  # Gleitfuß-Kanal (Z=4 bis 10)
track_top = make_centered_box(160, 10.5, 10.0, 10, 0, 15.0) # Hals-Kanal (Z=10 bis 20)
base = base.cut(track_bot).cut(track_top)

# B) DER TENSIONER TOWER (Integrierte Filz-Bremse ganz links)
tower = make_centered_box(20, basis_breite, 22, -75, 0, 29.0) # Steht auf der Base
base = base.fuse(tower)

# Schlitz für die Filz-Pads
felt_slit = make_centered_box(8, basis_breite + 2, 20, -75, 0, 32.0)
base = base.cut(felt_slit)

# Drahtführungs-Loch exakt auf Höhe Z=33 (nach hinten auf Y=12 versetzt!)
wire_in = Part.makeCylinder(1.5, 40)
wire_in.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
base = base.cut(wire_in.translate(App.Vector(-95, 12, 33)))

# Klemmschrauben-Loch (M3) um den Filz zusammenzupressen
tension_screw = Part.makeCylinder(1.7, 50)
tension_screw.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90) # Extrudiert in -Y Richtung
base = base.cut(tension_screw.translate(App.Vector(-75, 25, 38)))

# Echte Sechskant-Tasche für die M3 Mutter (verhindert Mitdrehen)
tension_nut = make_hex_prism(5.8, 6.0)
tension_nut.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90) # Extrudiert in -Y Richtung
base = base.cut(tension_nut.translate(App.Vector(-75, -15, 38)))

# C) EINSCHMELZMUTTERN FÜR DEN ABNEHMBAREN END-BLOCK (Rechts)
# NEU: ZWEI Einschmelzmuttern für absolute Verdrehsicherheit! (Y=0 und Y=-14)
m3_insert_vert = Part.makeCylinder(2.1, 8.0)
base = base.cut(m3_insert_vert.copy().translate(App.Vector(75, 0, 10)))   # Zentriert
base = base.cut(m3_insert_vert.copy().translate(App.Vector(75, -14, 10))) # Gegen Verdrehen

# D) NEU: STOPPER-MUTTERNAUFNAHMEN IN DER SCHIENE (Von unten)
# 3 Positionen für maximale Flexibilität!
stopper_hex = make_hex_prism(5.8, 3.0)
stopper_hole = Part.makeCylinder(1.7, 6.0)

for x_pos in [0, 20, 40]:
    base = base.cut(stopper_hex.copy().translate(App.Vector(x_pos, 0, 0)))
    base = base.cut(stopper_hole.copy().translate(App.Vector(x_pos, 0, 0)))

# E) Verschraubungslöcher für den Tisch (M4 Senkkopf) WEIT AUSSEN!
mount_hole = Part.makeCylinder(2.2, 25).translate(App.Vector(0, 0, -2))
sink = Part.makeCone(4.5, 2.2, 3.0).translate(App.Vector(0, 0, 15))

def add_mount(x, y):
    global base
    base = base.cut(mount_hole.copy().translate(App.Vector(x, y, 0)))
    base = base.cut(sink.copy().translate(App.Vector(x, y, 0)))

# Löcher liegen jetzt bei Y=16 und Y=-16 (Berühren die T-Nut absolut nicht mehr!)
add_mount(50, 16)
add_mount(50, -16)
add_mount(-45, 16)
add_mount(-45, -16)

show_obj(base.removeSplitter(), "Teil1_Basis_Mit_Bremse")


# ==========================================
# 2. DER ABNEHMBARE MAGNET-BLOCK (Schraubbarer Deckel mit Führung)
# ==========================================
block = make_centered_box(20, 38, 22, 0, 0, 11) # Lokales Z=0 bis 22

# ZENTRIER-FÜHRUNG FÜR DIE SCHIENE
guide = make_centered_box(20, 10.0, 5.0, 0, 0, -2.5)
block = block.fuse(guide)

# NEU: ZWEI SCHRAUBEN FÜR PERFEKTEN SITZ UND VERDREHSICHERHEIT
screw_hole = Part.makeCylinder(1.7, 30).translate(App.Vector(0, 0, -5))
screw_sink = Part.makeCylinder(3.2, 15.0).translate(App.Vector(0, 0, 10))

block = block.cut(screw_hole.copy().translate(App.Vector(0, 0, 0))).cut(screw_sink.copy().translate(App.Vector(0, 0, 0)))
block = block.cut(screw_hole.copy().translate(App.Vector(0, -14, 0))).cut(screw_sink.copy().translate(App.Vector(0, -14, 0)))

# Die 3 Magnetlöcher (Öffnung zeigt nach links zum Schlitten)
m_hole = Part.makeCylinder(magnet_d / 2.0, magnet_tiefe)
m_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90) # Zeigt in -X Richtung
m_hole.translate(App.Vector(-10 + magnet_tiefe, 0, 6.5)) # Lokales Z=6.5 ist absolut Z=24.5

block = block.cut(m_hole.copy().translate(App.Vector(0, 0, 0)))
block = block.cut(m_hole.copy().translate(App.Vector(0, 10, 0)))
block = block.cut(m_hole.copy().translate(App.Vector(0, -10, 0)))

# Drahtführungsloch auf Y=12 (Kollidiert nicht mit Schraube bei Y=0!)
wire_out = Part.makeCylinder(1.5, 30)
wire_out.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
block = block.cut(wire_out.translate(App.Vector(-15, 12, 15))) # Lokales Z=15 ist absolut Z=33

block.translate(App.Vector(75, 50, 0)) # Zum Drucken verschoben
show_obj(block.removeSplitter(), "Teil2_Endblock_Zentriert")


# ==========================================
# 3. DER "PILZ"-SCHLITTEN (Massiver Kopf, V-Shape Geometrie)
# ==========================================
runner = make_centered_box(28, 19.5, 5.0, 0, 0, 2.5) 
neck = make_centered_box(28, 9.5, 9.0, 0, 0, 9.5)    
head = make_centered_box(28, 38.0, 12.0, 0, 0, 20.0) 

sled = runner.fuse(neck).fuse(head)

# 3 Magnet-Löcher passend zum Endblock
s_hole = Part.makeCylinder(magnet_d / 2.0, magnet_tiefe)
s_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90) # Zeigt in +X Richtung
s_hole.translate(App.Vector(14 - magnet_tiefe, 0, 20.0)) 

sled = sled.cut(s_hole.copy().translate(App.Vector(0, 0, 0)))
sled = sled.cut(s_hole.copy().translate(App.Vector(0, 10, 0)))
sled = sled.cut(s_hole.copy().translate(App.Vector(0, -10, 0)))

# Der Führungs-Pin auf Y=-10 (Sorgt für die massive "V-Form" der Drahtspannung!)
pin = Part.makeCylinder(4.0, 7.0).translate(App.Vector(0, -10, 26.0))
pin_cap = Part.makeCylinder(6.0, 2.0).translate(App.Vector(0, -10, 33.0)) 

sled = sled.fuse(pin).fuse(pin_cap)

sled.translate(App.Vector(-50, 50, 0)) # Zum Drucken verschoben
show_obj(sled.removeSplitter(), "Teil3_Magnet_Schlitten")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")