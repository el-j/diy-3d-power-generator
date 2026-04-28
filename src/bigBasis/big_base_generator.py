import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Kraftpaket_Generator")

# ==========================================
# ⚙️ PARAMETER (XXL 20-Pol Sandwich Generator)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Die 20 eckigen Magnete (20 Oben, 20 Unten)
magnet_l = 20.0  
magnet_w = 5.0   
magnet_h = 3.0   
anzahl_magnete = 20       
mag_kreis_r = 74.0 # Extrem weit außen für massives Drehmoment & Geschwindigkeit!

# Die NEUEN ovalen Gigant-Spulen (Capsules)
anzahl_spulen = 12
spule_innen_l = 22.0      # 2mm länger als der Magnet (Keine Auslöschung!)
spule_innen_w = 8.0       # 3mm breiter als der Magnet
spule_aussen_l = 40.0     # Riesiger Außendurchmesser
spule_aussen_w = 26.0     
spule_dicke = 6.0         # 6mm tiefe Taschen für massiv Kupfer

stator_radius = 99.0      # Schlitten-Basis (Passt saugend in R=100 der Base Station)
stator_dicke = 8.0        # 8mm massives Plastik für Stabilität
rotor_radius = 90.0       # 180mm Rotor-Teller
rotor_platte_h = 6.0  
backplate_h = 4.0
kragen_d = 20.0
kragen_h = 12.0

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

rotor_schraub_r = 50.0    # Perfekt zentriert zwischen Welle und Magneten
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

# Hilfsfunktion für Ovale/Kapseln (Perfekt für Spulen!)
def make_capsule(l, w, h):
    r = w / 2.0
    d = l - w
    cx = d / 2.0
    cyl1 = Part.makeCylinder(r, h).translate(App.Vector(cx, 0, 0))
    cyl2 = Part.makeCylinder(r, h).translate(App.Vector(-cx, 0, 0))
    box = Part.makeBox(d, w, h).translate(App.Vector(-cx, -r, 0))
    return cyl1.fuse(cyl2).fuse(box)

def create_capsule_array(radius, l, w, depth, count):
    items = []
    for i in range(count):
        angle_deg = i * (360.0 / count)
        angle_rad = math.radians(angle_deg)
        cap = make_capsule(l, w, depth)
        cap.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        cap.translate(App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0))
        items.append(cap)
    res = items[0]
    for m in items[1:]: res = res.fuse(m)
    return res

def create_rectangular_array(radius, length, width, depth, count):
    items = []
    for i in range(count):
        angle_deg = i * (360.0 / count)
        angle_rad = math.radians(angle_deg)
        box = Part.makeBox(length, width, depth)
        box.translate(App.Vector(-length / 2.0, -width / 2.0, 0))
        box.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        box.translate(App.Vector(radius * math.cos(angle_rad), radius * math.sin(angle_rad), 0))
        items.append(box)
    res = items[0]
    for m in items[1:]: res = res.fuse(m)
    return res

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# 1. ROTOR (20 Rechteck-Magnete + Leichtbau)
def make_rotor(is_top):
    r = Part.makeCylinder(rotor_radius, rotor_platte_h)
    
    mag_cut_l = magnet_l + 0.4
    mag_cut_w = magnet_w + 0.4
    mags = create_rectangular_array(mag_kreis_r, mag_cut_l, mag_cut_w, rotor_platte_h, anzahl_magnete)
    r = r.cut(mags)
    
    lip_z = 0 if is_top else rotor_platte_h - 0.6
    for i in range(anzahl_magnete):
        angle_deg = i * (360.0 / anzahl_magnete)
        angle_rad = math.radians(angle_deg)
        
        lip_outer = Part.makeBox(mag_cut_l, mag_cut_w, 0.6)
        lip_outer.translate(App.Vector(-mag_cut_l/2.0, -mag_cut_w/2.0, 0))
        lip_inner = Part.makeBox(magnet_l - 1.5, magnet_w - 1.5, 0.6)
        lip_inner.translate(App.Vector(-(magnet_l-1.5)/2.0, -(magnet_w-1.5)/2.0, 0))
        
        lip = lip_outer.cut(lip_inner)
        lip.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        lip.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), lip_z))
        r = r.fuse(lip)
        
        # Spitze Dreiecks-Markierung nach INNEN (nur bei jedem 2. Magneten)
        if i % 2 == 0:
            base_x = mag_kreis_r - (mag_cut_w / 2.0) - 1.0
            p1 = App.Vector(base_x, 3.5, 0)
            p2 = App.Vector(base_x, -3.5, 0)
            p3 = App.Vector(base_x - 4.5, 0, 0) 
            wire = Part.Wire(Part.makePolygon([p1, p2, p3, p1]))
            tri = Part.Face(wire).extrude(App.Vector(0, 0, rotor_platte_h))
            tri.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
            r = r.cut(tri)
        
    r = r.cut(make_square_prism(achse_kantenlaenge + toleranz, rotor_platte_h))
    
    # 5 Verschraubungslöcher! (Exakt 9 Grad Offset zwischen den 20 Magneten)
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        r = r.cut(Part.makeCylinder(3.4 / 2.0, rotor_platte_h).translate(App.Vector(x, y, 0)))
        taschen_z = rotor_platte_h - einschmelzmutter_t if is_top else 0
        r = r.cut(Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, taschen_z)))

    # NEU: Leichtbau-Skelettierung (5 Große Löcher zur Gewichtsreduktion & Kühlung)
    # Perfekt versetzt zu den Schraubenlöchern (45 Grad Offset)
    for i in range(5):
        angle = math.radians(i * 72 + 45)
        x = 42.0 * math.cos(angle)
        y = 42.0 * math.sin(angle)
        loch = Part.makeCylinder(16.0, rotor_platte_h).translate(App.Vector(x, y, 0))
        r = r.cut(loch)

    # Große Ausrichtungs-Kerbe (bei 45 Grad - trifft genau in ein Leichtbau-Loch, was gut aussieht)
    notch_angle = math.radians(45)
    align_notch = Part.makeCylinder(4.0, rotor_platte_h)
    align_notch.translate(App.Vector(rotor_radius * math.cos(notch_angle), rotor_radius * math.sin(notch_angle), 0))
    r = r.cut(align_notch)

    # Oben/Unten Indikator (Punkte an der Seite bei 117 Grad)
    marker_cyl = Part.makeCylinder(1.5, 5.0)
    marker_cyl.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    marker_cyl.translate(App.Vector(rotor_radius - 2.0, 0, rotor_platte_h / 2.0))
    if is_top:
        m1 = marker_cyl.copy()
        m1.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 117)
        r = r.cut(m1)
    else:
        m1 = marker_cyl.copy()
        m1.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 113)
        m2 = marker_cyl.copy()
        m2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 121)
        r = r.cut(m1).cut(m2)
        
    return r.removeSplitter()

# 2. BACKPLATE (DECKEL)
def make_backplate(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    k = Part.makeCylinder(kragen_d/2.0, kragen_h)
    if is_top: k.translate(App.Vector(0,0, backplate_h))
    else: k.translate(App.Vector(0,0, -kragen_h))
    p = p.fuse(k).cut(make_square_prism(achse_kantenlaenge+toleranz, 30.0).translate(App.Vector(0,0,-5)))
    
    plug_h = rotor_platte_h - magnet_h - 0.6 
    plugs = create_rectangular_array(mag_kreis_r, magnet_l + 0.1, magnet_w + 0.1, plug_h, anzahl_magnete)
    plug_z = -plug_h if is_top else backplate_h
    plugs.translate(App.Vector(0, 0, plug_z))
    p = p.fuse(plugs)
    
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        p = p.cut(Part.makeCylinder(3.4 / 2.0, backplate_h + plug_h + 10.0).translate(App.Vector(x, y, -5)))
        senk_z = backplate_h - 1.5 if is_top else 0
        p = p.cut(Part.makeCylinder(6.0 / 2.0, 1.5).translate(App.Vector(x, y, senk_z)))
        
    # NEU: Exakt dieselben Leichtbau-Löcher wie im Rotor
    for i in range(5):
        angle = math.radians(i * 72 + 45)
        x = 42.0 * math.cos(angle)
        y = 42.0 * math.sin(angle)
        loch = Part.makeCylinder(16.0, 30.0).translate(App.Vector(x, y, -5))
        p = p.cut(loch)

    return p.removeSplitter()

# 3. XXL STATOR SCHLITTEN (Mit ovalen Taschen & Leichtbau!)
def make_stator_schlitten():
    schlitten_b = Part.makeCylinder(stator_radius, stator_dicke)
    schlitten_f = Part.makeBox(stator_radius*2, 140.0, stator_dicke).translate(App.Vector(-stator_radius, -140.0, 0))
    s = schlitten_b.fuse(schlitten_f)
    griff = Part.makeBox(50.0, 20.0, stator_dicke).translate(App.Vector(-25.0, -160.0, 0))
    s = s.fuse(griff)
    
    # Zentrale Aussparung für die Achse
    s = s.cut(Part.makeCylinder(16.0, stator_dicke))
    
    # NEU: Leichtbau-Löcher im ungenutzten Zentrum (Bilden stabile "Speichen")
    for i in range(6):
        angle = math.radians(i * 60)
        x = 35.0 * math.cos(angle)
        y = 35.0 * math.sin(angle)
        s = s.cut(Part.makeCylinder(12.0, stator_dicke).translate(App.Vector(x, y, 0)))

    # Die Ovalen Spulentaschen (Capsules)
    for i in range(anzahl_spulen):
        angle_deg = i * (360.0 / anzahl_spulen)
        angle_rad = math.radians(angle_deg)
        
        pocket = make_capsule(spule_aussen_l + 0.4, spule_aussen_w + 0.4, stator_dicke - 1.5)
        pocket.translate(App.Vector(0,0, 1.5))
        
        thru_hole = make_capsule(spule_aussen_l - 1.5, spule_aussen_w - 1.5, stator_dicke)
        
        spulen_loch = pocket.fuse(thru_hole)
        spulen_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        spulen_loch.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), 0))
        s = s.cut(spulen_loch)
    
    # Ring-Kanal (Angepasst auf die neuen ovalen Spulen)
    ring_kanal = Part.makeCylinder(88.0, 3.5).cut(Part.makeCylinder(82.0, 3.5))
    ring_kanal.translate(App.Vector(0, 0, stator_dicke - 3.5))
    s = s.cut(ring_kanal)
    
    kanal = Part.makeBox(12.0, 120.0, 3.5).translate(App.Vector(-6.0, -140.0, stator_dicke - 3.5))
    s = s.cut(kanal)
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(-15, -150, 0)))
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(15, -150, 0)))
    
    # Schrauben für den Deckel (Sicher zwischen den Spulen platziert)
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 94.0 * math.cos(angle)
        y = 94.0 * math.sin(angle)
        s = s.cut(Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(x, y, 0)))
        
    return s.removeSplitter()

# 4. DECKEL (STATOR-HALTERUNG)
def make_deckel():
    d = Part.makeCylinder(stator_radius, 1.2).cut(Part.makeCylinder(18.0/2.0, 1.2))
    
    # NEU: Belüftungs- und Leichtbaulöcher (Wie im Schlitten)
    for i in range(6):
        angle = math.radians(i * 60)
        x = 35.0 * math.cos(angle)
        y = 35.0 * math.sin(angle)
        d = d.cut(Part.makeCylinder(12.0, 1.2).translate(App.Vector(x, y, 0)))

    # Deckel-Ausschnitte halten die ovale Spule von oben fest
    ch = create_capsule_array(mag_kreis_r, spule_aussen_l - 1.0, spule_aussen_w - 1.0, 1.2, anzahl_spulen)
    d = d.cut(ch)

    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 94.0 * math.cos(angle)
        y = 94.0 * math.sin(angle)
        d = d.cut(Part.makeCylinder(1.7, 1.2).translate(App.Vector(x,y,0)))
        
    return d

r_o = make_rotor(True); r_u = make_rotor(False)
b_o = make_backplate(True); b_u = make_backplate(False)
s_schlitten = make_stator_schlitten(); s_d = make_deckel()

r_o.translate(App.Vector(0,0,30)); b_o.translate(App.Vector(0,0,45))
s_d.translate(App.Vector(0,0,15))
r_u.translate(App.Vector(0,0,-20)); b_u.translate(App.Vector(0,0,-40))

show_obj(r_o, "Rotor_Oben_XXL"); show_obj(r_u, "Rotor_Unten_XXL")
show_obj(b_o, "Backplate_Oben_XXL"); show_obj(b_u, "Backplate_Unten_XXL")
show_obj(s_schlitten, "Stator_Schlitten_XXL"); show_obj(s_d, "Stator_Deckel_XXL")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")