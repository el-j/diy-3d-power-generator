import FreeCAD as App
import Part
import math

doc = App.newDocument("Ortho_Kapsel_Spule")

# ==========================================
# ⚙️ PARAMETER (Kapsel-Spule für Ortho-Maschine)
# ==========================================
# Maße der Spule (Dein Original-Kapsel-Maß)
spule_innen_l = 22.0  
spule_innen_w = 8.0   
spule_dicke = 6.0     
spule_aussen_l = 40.0 
spule_aussen_w = 26.0 

# Flansch-Wände
wand_l = 44.0         
wand_w = 30.0         
wand_dicke = 3.0      

# Vierkant-Aufnahme (jetzt komplett durchgehend!)
quad_spindel_loch_sw = 6.4 
hub_tiefe = 12.0 # Tiefe des Sockels auf der Rückseite der Basis
# ==========================================

def make_capsule(l, w, h):
    r = w / 2.0
    d = l - w
    if d < 0: d = 0
    cx = d / 2.0
    cyl1 = Part.makeCylinder(r, h).translate(App.Vector(cx, 0, 0))
    cyl2 = Part.makeCylinder(r, h).translate(App.Vector(-cx, 0, 0))
    box = Part.makeBox(d, w, h).translate(App.Vector(-cx, -r, 0))
    return cyl1.fuse(cyl2).fuse(box)

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# 1. BAUTEIL: BASIS MIT DURCHGEHENDEM VIERKANT
# ==========================================
def make_winder_basis():
    # A) Die Wand / Der Flansch (Z=0 bis Z=3)
    basis = make_capsule(wand_l, wand_w, wand_dicke)
    
    # B) Zylindrischer Sockel auf der Außenseite für mehr Halt (Z=3 bis Z=15)
    schaft = Part.makeCylinder(14.0 / 2.0, hub_tiefe).translate(App.Vector(0, 0, wand_dicke))
    basis = basis.fuse(schaft)
    
    # C) Arretierungs-Tasche für den Kern (Z=0 bis Z=1)
    pocket = make_capsule(spule_innen_l + 0.4, spule_innen_w + 0.4, 1.0)
    basis = basis.cut(pocket)
    
    # D) DURCHGEHENDES Vierkant-Loch (Schneidet komplett durch!)
    quad_loch = make_square_prism(quad_spindel_loch_sw, 30.0).translate(App.Vector(0, 0, -5.0))
    basis = basis.cut(quad_loch)
    
    # E) Schlitz für den Drahtausgang
    slit = Part.makeBox(wand_l, 1.5, 5.0).translate(App.Vector(0, -0.75, 0))
    basis = basis.cut(slit)
    
    # F) Füllstands-Markierung
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_basis = mark_out.cut(mark_in)
    basis = basis.cut(markierung_basis)
    
    return basis.removeSplitter()

# ==========================================
# 2. BAUTEIL: DECKEL MIT DURCHGEHENDEM VIERKANT
# ==========================================
def make_winder_deckel():
    # A) Die Wand (Z=0 bis Z=3)
    deckel = make_capsule(wand_l, wand_w, wand_dicke)
    
    # B) Der Wickel-Kern auf der Innenseite (Z=3 bis Z=10)
    kern = make_capsule(spule_innen_l, spule_innen_w, spule_dicke + 1.0).translate(App.Vector(0, 0, wand_dicke))
    deckel = deckel.fuse(kern)
    
    # C) DURCHGEHENDES Vierkant-Loch (Schneidet komplett durch!)
    quad_loch = make_square_prism(quad_spindel_loch_sw, 30.0).translate(App.Vector(0, 0, -5.0))
    deckel = deckel.cut(quad_loch)
    
    # D) Einlegeschlitz für den Kupferdraht
    slit = Part.makeBox(1.5, wand_w, wand_dicke).translate(App.Vector(-0.75, spule_innen_w / 2.0, 0))
    deckel = deckel.cut(slit)
    
    # E) Füllstands-Markierung
    mark_out = make_capsule(spule_aussen_l + 0.5, spule_aussen_w + 0.5, 0.5)
    mark_in = make_capsule(spule_aussen_l - 0.5, spule_aussen_w - 0.5, 0.5)
    markierung_deckel = mark_out.cut(mark_in).translate(App.Vector(0, 0, wand_dicke - 0.5))
    deckel = deckel.cut(markierung_deckel)
    
    return deckel.removeSplitter()


basis = make_winder_basis()
deckel = make_winder_deckel()

# Nebeneinander anordnen, bereit für den Slicer
basis.translate(App.Vector(30, 0, 0))
deckel.translate(App.Vector(-30, 0, 0))

show_obj(basis, "Kapsel_Spule_Basis_Vierkant")
show_obj(deckel, "Kapsel_Spule_Deckel_Kern")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")