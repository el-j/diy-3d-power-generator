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
spule_aussen_l = 40.0 # Zielmaß für die Markierung
spule_aussen_w = 26.0 # Zielmaß für die Markierung

# Winder-Wände (Verstärkt für den Support-freien Druck)
wand_l = 44.0         
wand_w = 30.0         
wand_dicke = 3.0      # Erhöht auf 3mm für mehr Stabilität beim Festziehen

# Hex-Bit Aufnahme (Standard 1/4 Zoll Bit = 6.35mm)
bit_aufnahme_d = 6.5  
bit_tiefe = 10.0      

# Verschraubung (M3x12 Schraube empfohlen!)
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

# 1. BAUTEIL: BASIS MIT BIT-AUFNAHME (Support-frei: Z=0 liegt auf dem Druckbett)
def make_winder_basis():
    # A) Die Wand (Z=0 bis Z=3)
    basis = make_capsule(wand_l, wand_w, wand_dicke)
    
    # B) Zylindrischer Schaft für den Bit auf der Außenseite (Z=3 bis Z=19)
    schaft = Part.makeCylinder(12.0 / 2.0, 16.0).translate(App.Vector(0, 0, wand_dicke))
    basis = basis.fuse(schaft)
    
    # C) Hex-Loch für den Akkuschrauber-Bit (Z=9 bis Z=19)
    bit_loch = make_hex_prism(bit_aufnahme_d, bit_tiefe).translate(App.Vector(0, 0, wand_dicke + 16.0 - bit_tiefe))
    basis = basis.cut(bit_loch)
    
    # D) Arretierungs-Tasche für den Kern auf der Innenseite (Z=0 bis Z=1)
    # Druckt sich als perfektes Brücken-Infill (Bridging)
    pocket = make_capsule(spule_innen_l + 0.4, spule_innen_w + 0.4, 1.0)
    basis = basis.cut(pocket)
    
    # E) Tasche für M3 Einschmelzmutter (wird von der Innenseite Z=1 eingeschmolzen)
    mutter_loch = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(0, 0, 1.0))
    basis = basis.cut(mutter_loch)
    
    # F) Durchgangsloch für überstehendes Schraubengewinde
    schrauben_loch = Part.makeCylinder(3.4 / 2.0, 8.0).translate(App.Vector(0, 0, 1.0))
    basis = basis.cut(schrauben_loch)
    
    # G) Füllstands-Markierung (direkt auf der Druckbett-Fläche Z=0)
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_basis = mark_out.cut(mark_in)
    basis = basis.cut(markierung_basis)
    
    return basis.removeSplitter()

# 2. BAUTEIL: DECKEL MIT KERN (Support-frei: Z=0 liegt auf dem Druckbett)
def make_winder_deckel():
    # A) Die Wand (Z=0 bis Z=3)
    deckel = make_capsule(wand_l, wand_w, wand_dicke)
    
    # B) Der Wickel-Kern auf der Innenseite (Z=3 bis Z=10)
    # 6mm für die Spule + 1mm Überstand, der in die Tasche der Basis einrastet!
    kern = make_capsule(spule_innen_l, spule_innen_w, spule_dicke + 1.0).translate(App.Vector(0, 0, wand_dicke))
    deckel = deckel.fuse(kern)
    
    # C) Durchgangsloch für M3 Schraube (Z=0 bis Z=10)
    schrauben_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
    deckel = deckel.cut(schrauben_loch)
    
    # D) Senkung für den M3 Schraubenkopf auf der Druckbett-Seite (Z=0 bis Z=2.5)
    senk = Part.makeCylinder(6.0 / 2.0, 2.5)
    deckel = deckel.cut(senk)
    
    # E) Einlegeschlitz für den Kupferdraht-Anfang (schneidet komplett durch die Wand)
    slit = Part.makeBox(1.5, wand_w, wand_dicke).translate(App.Vector(-0.75, spule_innen_w / 2.0, 0))
    deckel = deckel.cut(slit)
    
    # F) Füllstands-Markierung auf der Innenseite der Wand (Z=2.5 bis Z=3.0)
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_deckel = mark_out.cut(mark_in).translate(App.Vector(0, 0, wand_dicke - 0.5))
    deckel = deckel.cut(markierung_deckel)
    
    return deckel.removeSplitter()

basis = make_winder_basis()
deckel = make_winder_deckel()

# Nebeneinander anordnen, wie sie auf dem Druckbett (Z=0) liegen würden!
basis.translate(App.Vector(30, 0, 0))
deckel.translate(App.Vector(-30, 0, 0))

show_obj(basis, "Winder_Basis_Bit")
show_obj(deckel, "Winder_Deckel_Kern")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")