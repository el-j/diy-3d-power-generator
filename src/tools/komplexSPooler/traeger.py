import FreeCAD as App
import Part

doc = App.newDocument("Wickelmaschine_Traeger_Technic")

# ==========================================
# ⚙️ PARAMETER (Skeleton Träger - Ultra Leicht & Steif)
# ==========================================
# Die X-Koordinaten der 4 Türme aus der Basis
turm_x_positionen = [35.0, -15.0, -65.0, -135.0]

traeger_breite = 12.0
traeger_dicke = 6.0
schrauben_loch_d = 3.4 # Durchgangsloch für M3 Schrauben in die Türme

# Skeleton-Parameter
aussparung_breite = 7.6 # Lässt 2.2mm massive Außenwände (Perfekt für 5 Perimeter bei 0.4er Düse!)
# ==========================================

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

def make_capsule_cut(l, w, h):
    # Erstellt ein abgerundetes Langloch für das Skeleton-Design
    r = w / 2.0
    d = l - w
    if d < 0: d = 0
    cx = d / 2.0
    cyl1 = Part.makeCylinder(r, h).translate(App.Vector(cx, 0, 0))
    cyl2 = Part.makeCylinder(r, h).translate(App.Vector(-cx, 0, 0))
    box = Part.makeBox(d, w, h).translate(App.Vector(-cx, -r, 0))
    return cyl1.fuse(cyl2).fuse(box)

# 1. GRUNDKÖRPER (Mit abgerundeten Enden)
l_total = 190.0
cx_main = (35.0 + (-135.0)) / 2.0 # Mitte bei X = -50

box = make_centered_box(l_total - traeger_breite, traeger_breite, traeger_dicke, cx_main, 0, traeger_dicke/2.0)
cyl_vorne = Part.makeCylinder(traeger_breite / 2.0, traeger_dicke).translate(App.Vector(35.0 + traeger_breite / 2.0, 0, 0))
cyl_hinten = Part.makeCylinder(traeger_breite / 2.0, traeger_dicke).translate(App.Vector(-135.0 - traeger_breite / 2.0, 0, 0))

traeger = box.fuse(cyl_vorne).fuse(cyl_hinten)

# 2. BEFESTIGUNGSLÖCHER (Für M3 Schrauben)
screw_hole = Part.makeCylinder(schrauben_loch_d / 2.0, traeger_dicke + 2.0).translate(App.Vector(0, 0, -1.0))
sink_hole = Part.makeCylinder(6.0 / 2.0, 3.0).translate(App.Vector(0, 0, traeger_dicke - 2.5)) # Senkkopf

for x in turm_x_positionen:
    traeger = traeger.cut(screw_hole.copy().translate(App.Vector(x, 0, 0)))
    traeger = traeger.cut(sink_hole.copy().translate(App.Vector(x, 0, 0)))

# 3. SKELETON-AUSSPARUNGEN (Materialersparnis & Fachwerk-Stabilität)
# Wir lassen 12mm massives Material um die Schraublöcher stehen.
# Segment 1: Zwischen X=35 und X=-15 (Distanz 50, Mitte = 10)
len_1 = 50.0 - 12.0
cut1 = make_capsule_cut(len_1, aussparung_breite, traeger_dicke + 2.0).translate(App.Vector(10, 0, -1.0))
traeger = traeger.cut(cut1)

# Segment 2: Zwischen X=-15 und X=-65 (Distanz 50, Mitte = -40)
len_2 = 50.0 - 12.0
cut2 = make_capsule_cut(len_2, aussparung_breite, traeger_dicke + 2.0).translate(App.Vector(-40, 0, -1.0))
traeger = traeger.cut(cut2)

# Segment 3: Zwischen X=-65 und X=-135 (Distanz 70, Mitte = -100)
len_3 = 70.0 - 12.0
cut3 = make_capsule_cut(len_3, aussparung_breite, traeger_dicke + 2.0).translate(App.Vector(-100, 0, -1.0))
traeger = traeger.cut(cut3)

# Träger bereinigen für sauberes Mesh
traeger = traeger.removeSplitter()

# ZWEIMAL anzeigen (Einen für die vordere Turmreihe, einen für die hintere)
obj1 = doc.addObject("Part::Feature", "Skeleton_Traeger_Vorne")
obj1.Shape = traeger.copy().translate(App.Vector(0, 45, 60)) # Setzt ihn virtuell auf die vorderen Türme

obj2 = doc.addObject("Part::Feature", "Skeleton_Traeger_Hinten")
obj2.Shape = traeger.copy().translate(App.Vector(0, 75, 60)) # Setzt ihn virtuell auf die hinteren Türme

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")