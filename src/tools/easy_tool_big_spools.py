import FreeCAD as App
import Part
import math

doc = App.newDocument("Coil_Winder_Tool")

    # ==========================================
# ⚙️ PARAMETER FÜR DEN EASY COIL WINDER
# ==========================================
# Maße der Spule (Exakt abgestimmt auf die XXL-Kapsel-Spulen)
spule_innen_l = 22.0  
spule_innen_w = 8.0   
spule_dicke = 6.0     
spule_aussen_l = 40.0 # NEU: Zielmaß für die Markierung
spule_aussen_w = 26.0 # NEU: Zielmaß für die Markierung

# Winder-Wände (Sollen die Spule beim Wickeln sicher in Form halten)
wand_l = 44.0         
wand_w = 30.0         
wand_dicke = 2.0      

# Hex-Bit Aufnahme (Standard 1/4 Zoll Bit = 6.35mm)
bit_aufnahme_d = 6.5  # Minimales Spiel (Toleranz), damit der Metall-Bit satt passt
bit_tiefe = 10.0      

# Verschraubung (M3 Schraube hält den Deckel)
einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0 
    # ==========================================

def make_capsule(l, w, h):
    r = w / 2.0
    d = l - w
    cx = d / 2.0
    cyl1 = Part.makeCylinder(r, h).translate(App.Vector(cx, 0, 0))
    cyl2 = Part.makeCylinder(r, h).translate(App.Vector(-cx, 0, 0))
    box = Part.makeBox(d, w, h).translate(App.Vector(-cx, -r, 0))
    return cyl1.fuse(cyl2).fuse(box)

def make_hex_prism(flat_to_flat, height):
    # Umrechnung von Flat-to-Flat zu Radius für das Polygon
    r = (flat_to_flat / 2.0) / math.cos(math.radians(30))
    points = []
    for j in range(7):
        angle = math.radians(60 * j + 30) 
        points.append(App.Vector(r * math.cos(angle), r * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    return Part.Face(Part.Wire(polygon)).extrude(App.Vector(0, 0, height))

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

    # 1. BAUTEIL: BASIS MIT BIT-AUFNAHME
def make_winder_basis():
    # A) Zylindrischer Schaft für den Bit (Hinten)
    schaft = Part.makeCylinder(7.0, 12.0).translate(App.Vector(0, 0, -12.0))
        
    # B) Rückwand (Hält den Draht)
    back_wall = make_capsule(wand_l, wand_w, wand_dicke)
    
    # C) Der Wickel-Kern (Spulen-Innenmaß + 1mm für Arretierung in den Deckel)
    kern = make_capsule(spule_innen_l, spule_innen_w, spule_dicke + 1.0)
    kern.translate(App.Vector(0, 0, wand_dicke))
    
    basis = schaft.fuse(back_wall).fuse(kern)
    
    # D) Hex-Loch für den Akkuschrauber-Bit (Tiefe 10mm)
    bit_loch = make_hex_prism(bit_aufnahme_d, bit_tiefe).translate(App.Vector(0, 0, -12.0))
    basis = basis.cut(bit_loch)
    
    # E) Durchgangsloch für die M3 Schraube (Komplett durchlaufend)
    schrauben_loch = Part.makeCylinder(1.7, 30.0).translate(App.Vector(0, 0, -15.0))
    basis = basis.cut(schrauben_loch)
    
    # F) Tasche für M3 Einschmelzmutter (oben im Kern)
    # Du drückst die Mutter einfach von oben (vorne) heiß in den Kern
    mutter_loch = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
    mutter_loch.translate(App.Vector(0, 0, wand_dicke + spule_dicke + 1.0 - einschmelzmutter_t))
    basis = basis.cut(mutter_loch)
        
    # G) Einlegeschlitz für den Kupferdraht-Anfang!
    # Ein 1.5mm breiter Schnitt in der Rückwand, um den Draht sicher nach außen zu führen
    slit = Part.makeBox(1.5, wand_w, wand_dicke).translate(App.Vector(-0.75, spule_innen_w / 2.0, 0))
    basis = basis.cut(slit)
    
    # H) NEU: Füllstands-Markierung (0.5mm tiefe Rille auf der Innenseite)
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_basis = mark_out.cut(mark_in)
    markierung_basis.translate(App.Vector(0, 0, wand_dicke - 0.5))
    basis = basis.cut(markierung_basis)
    
    return basis.removeSplitter()

# 2. BAUTEIL: DECKEL
def make_winder_deckel():
    # A) Frontwand
    front_wall = make_capsule(wand_l, wand_w, wand_dicke)
        
        # B) Arretierungs-Tasche (Negativ des Kerns, 1mm tief, mit 0.4mm Toleranz für leichten Sitz)
    tasche = make_capsule(spule_innen_l + 0.4, spule_innen_w + 0.4, 1.0)
    deckel = front_wall.cut(tasche)
    
    # C) Durchgangsloch für M3 Schraube
    schrauben_loch = Part.makeCylinder(1.7, 10.0).translate(App.Vector(0, 0, -5.0))
    deckel = deckel.cut(schrauben_loch)
        
        # D) Senkung für den M3 Schraubenkopf (damit alles schön flach abschließt)
    senk = Part.makeCylinder(3.0, 1.5).translate(App.Vector(0, 0, wand_dicke - 1.5))
    deckel = deckel.cut(senk)
    
    # E) NEU: Füllstands-Markierung auch im Deckel (auf der Innenseite bei Z=0)
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_deckel = mark_out.cut(mark_in)
    markierung_deckel.translate(App.Vector(0, 0, 0))
    deckel = deckel.cut(markierung_deckel)
    
    return deckel.removeSplitter()

basis = make_winder_basis()
deckel = make_winder_deckel()

    # Positionierung für die Vorschau (Zusammenbau-Ansicht)
deckel.translate(App.Vector(0, 0, 15.0))

show_obj(basis, "Winder_Basis_Bit")
show_obj(deckel, "Winder_Deckel")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")