import FreeCAD as App
import Part
import math

doc = App.newDocument("Coil_Winder_Tool")

# ==========================================
# ⚙️ PARAMETER (Offene Tisch-Wickelmaschine)
# ==========================================
# Spulen-Maße des Generators
spule_innen_d = 7.0       
spule_aussen_d = 14.0     
spule_dicke = 3.5         

# M3 Hardware (Für Klemmschraube)
m3_loch = 3.6             
m3_mutter_sw = 5.8        # Leichtes Spiel für M3 Mutter (SW 5.5)
m3_mutter_tiefe = 2.5     

# Antrieb & Mechanik
uebersetzung = 4.0        # 4:1 Getriebe per Gummiband
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
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DIE TISCH-BASIS
# ==========================================
# Grundplatte
basis = make_centered_box(180, 120, 5, 0, 0, 2.5)

# Turm Links (Für die Kurbel)
turm_k = make_centered_box(10, 20, 50, -20, -30, 30)
loch_k = Part.makeCylinder(4.25, 20)
loch_k.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
turm_k = turm_k.cut(loch_k.translate(App.Vector(-30, -30, 45)))

# Turm Rechts (Für die Spule)
turm_w = make_centered_box(10, 20, 50, 20, 30, 30)
loch_w = Part.makeCylinder(4.25, 20)
loch_w.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
turm_w = turm_w.cut(loch_w.translate(App.Vector(10, 30, 45)))

# Dorn für die Kupferdraht-Rolle
pin_base = Part.makeCylinder(15, 2).translate(App.Vector(60, -30, 5))
pin = Part.makeCylinder(4.5, 60).translate(App.Vector(60, -30, 7))

# Gleitschiene für die Drahtführung
schiene = make_centered_box(60, 8, 8, 43, 45, 9)

basis = basis.fuse(turm_k).fuse(turm_w).fuse(pin_base).fuse(pin).fuse(schiene)
show_obj(basis.removeSplitter(), "Maschinen_Basis")


# ==========================================
# BAUTEIL 2: DER WICKELKOPF (Hängt frei in der Luft!)
# ==========================================
# Wir bauen ihn entlang der Z-Achse und rotieren ihn dann in Position
hex_drive = make_hex_prism(8.0, 10.0) # Sechskant für Akkuschrauber-Option
pulley_w = Part.makeCylinder(10.0, 10.0).translate(App.Vector(0,0,10))
nut_w = Part.makeTorus(10.0, 1.5).translate(App.Vector(0,0,15))
pulley_w = pulley_w.cut(nut_w)

shaft_w = Part.makeCylinder(4.0, 33.0).translate(App.Vector(0,0,20))
flansch_w = Part.makeCylinder(9.0, 3.0).translate(App.Vector(0,0,53))
core_w = Part.makeCylinder(spule_innen_d / 2.0, spule_dicke).translate(App.Vector(0,0,56))

wickelkopf = hex_drive.fuse(pulley_w).fuse(shaft_w).fuse(flansch_w).fuse(core_w)

# M3 Loch & Draht-Klemmschlitz
wickelkopf = wickelkopf.cut(Part.makeCylinder(m3_loch / 2.0, 40.0).translate(App.Vector(0,0,30)))
slot_w = make_centered_box(9, 0.8, 4, 4.5, 0, 54.5)
wickelkopf = wickelkopf.cut(slot_w)

# 14mm Füllstands-Markierung (Gravur)
ring = Part.makeCylinder(7, 0.5).cut(Part.makeCylinder(6.5, 0.5))
wickelkopf = wickelkopf.cut(ring.translate(App.Vector(0,0,53)))

# In Arbeits-Position bringen (Rotiert & Verschoben)
wickelkopf.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
wickelkopf.translate(App.Vector(-15, 30, 45))
show_obj(wickelkopf.removeSplitter(), "Wickelkopf_Spindel")


# ==========================================
# BAUTEIL 3: DER DECKEL (Wird mit M3 Schraube fixiert)
# ==========================================
deckel = Part.makeCylinder(9.0, 3.0)
deckel = deckel.cut(Part.makeCylinder(m3_loch / 2.0, 10.0).translate(App.Vector(0,0,-1)))
deckel = deckel.cut(make_hex_prism(m3_mutter_sw, 2.5).translate(App.Vector(0,0,0.5)))
deckel = deckel.cut(ring) # Markierung auch hier

deckel.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
deckel.translate(App.Vector(44.5, 30, 45)) # Sitzt exakt auf der Spule!
show_obj(deckel.removeSplitter(), "Spulen_Deckel")


# ==========================================
# BAUTEIL 4: DAS KURBELRAD
# ==========================================
pulley_k = Part.makeCylinder(40.0, 10.0)
nut_k = Part.makeTorus(40.0, 1.5).translate(App.Vector(0,0,5))
pulley_k = pulley_k.cut(nut_k)

shaft_k = Part.makeCylinder(4.0, 40.0).translate(App.Vector(0,0,10))
arm_k = make_centered_box(35, 15, 10, 17.5, 0, 55)
griff_k = Part.makeCylinder(6.0, 30.0).translate(App.Vector(30, 0, 60))

kurbelrad = pulley_k.fuse(shaft_k).fuse(arm_k).fuse(griff_k)

kurbelrad.rotate(App.Vector(0,0,0), App.Vector(0,1,0), -90)
kurbelrad.translate(App.Vector(5, -30, 45))
show_obj(kurbelrad.removeSplitter(), "Kurbelrad_Antrieb")


# ==========================================
# BAUTEIL 5: DER DRAHTFÜHRUNGS-SCHLITTEN
# ==========================================
schlitten = Part.makeBox(15.0, 16.0, 12.0).translate(App.Vector(-7.5, -8.0, 0))
schlitten = schlitten.cut(Part.makeBox(16.0, 8.5, 8.5).translate(App.Vector(-8.0, -8.0, 0)))

# Winziges Loch für den 0.1mm Kupferdraht
loch_s = Part.makeCylinder(1.0, 20.0)
loch_s.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
schlitten = schlitten.cut(loch_s.translate(App.Vector(0, 10, 8)))

schlitten.translate(App.Vector(43, 45, 5)) # Sitzt exakt auf der Schiene
show_obj(schlitten.removeSplitter(), "Draht_Schlitten")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Offene Tisch-Wickelmaschine generiert! (Vollständig montierte Ansicht)")