import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Mini_Generator")

# ==========================================
# ⚙️ PARAMETER (Industrial Sandwich Generator)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Deine 20 eckigen Magnete (10 Oben, 10 Unten)
magnet_l = 20.0  # Länge
magnet_w = 5.0   # Breite
magnet_h = 3.0   # Dicke
anzahl_magnete = 10       
mag_kreis_r = 27.0 # Leicht nach innen gezogen für perfekten Randabstand

anzahl_spulen = 12
spule_innen_d = 7.0       
spule_aussen_d = 14.0     
spule_dicke = 3.5         

stator_radius = 45.0
stator_dicke = 5.0 
rotor_radius = 38.0
rotor_platte_h = 6.0  
backplate_h = 3.0
kragen_d = 16.0
kragen_h = 12.0

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

rotor_schraub_r = 34.5 
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def create_circular_array(radius, item_radius, depth, count):
    items = []
    for i in range(count):
        angle = math.radians(i * (360.0 / count))
        x = radius * math.cos(angle); y = radius * math.sin(angle)
        items.append(Part.makeCylinder(item_radius, depth).translate(App.Vector(x, y, 0)))
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

# 1. ROTOR (Rechteck-Magnete, Dreiecks-Markierungen & Ausrichtungs-Hilfen)
def make_rotor(is_top):
    r = Part.makeCylinder(rotor_radius, rotor_platte_h)
    
    # Toleranz für den Magnet-Ausschnitt
    mag_cut_l = magnet_l + 0.4
    mag_cut_w = magnet_w + 0.4
    
    mags = create_rectangular_array(mag_kreis_r, mag_cut_l, mag_cut_w, rotor_platte_h, anzahl_magnete)
    r = r.cut(mags)
    
    # Lippe auf der Statorseite & NEUE Dreiecks-Markierungen
    lip_z = 0 if is_top else rotor_platte_h - 0.6
    for i in range(anzahl_magnete):
        angle_deg = i * (360.0 / anzahl_magnete)
        angle_rad = math.radians(angle_deg)
        
        # 1. Lippe erzeugen
        lip_outer = Part.makeBox(mag_cut_l, mag_cut_w, 0.6)
        lip_outer.translate(App.Vector(-mag_cut_l/2.0, -mag_cut_w/2.0, 0))
        
        lip_inner = Part.makeBox(magnet_l - 1.5, magnet_w - 1.5, 0.6)
        lip_inner.translate(App.Vector(-(magnet_l-1.5)/2.0, -(magnet_w-1.5)/2.0, 0))
        
        lip = lip_outer.cut(lip_inner)
        lip.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        lip.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), lip_z))
        r = r.fuse(lip)
        
        # 2. Spitze Dreiecks-Markierung nach INNEN (nur bei jedem 2. Magneten)
        if i % 2 == 0:
            # Dreieck zeichnen: Basis parallel zum Magneten, Spitze zeigt zum Zentrum
            base_x = mag_kreis_r - (mag_cut_w / 2.0) - 0.8
            p1 = App.Vector(base_x, 2.5, 0)
            p2 = App.Vector(base_x, -2.5, 0)
            p3 = App.Vector(base_x - 3.5, 0, 0) # Spitze
            
            wire = Part.Wire(Part.makePolygon([p1, p2, p3, p1]))
            tri = Part.Face(wire).extrude(App.Vector(0, 0, rotor_platte_h))
            
            tri.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
            r = r.cut(tri)
        
    r = r.cut(make_square_prism(achse_kantenlaenge + toleranz, rotor_platte_h))
    
    # 5 Verschraubungslöcher! (Bei 18, 90, 162, 234, 306 Grad)
    for i in range(5):
        angle = math.radians(i * 72 + 18)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        
        r = r.cut(Part.makeCylinder(3.4 / 2.0, rotor_platte_h).translate(App.Vector(x, y, 0)))
        
        taschen_z = rotor_platte_h - einschmelzmutter_t if is_top else 0
        r = r.cut(Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, taschen_z)))

    # ==========================================
    # SICHERHEITS-FEATURES ZUR MONTAGE (Repariert)
    # ==========================================
    # 1. Große Ausrichtungs-Kerbe (Notch) am Außenrand bei exakt 54 Grad! 
    # (Genau zwischen Magnet 1 bei 36° und Magnet 2 bei 72° sowie Schraube bei 18°/90°)
    notch_angle = math.radians(54)
    align_notch = Part.makeCylinder(3.0, rotor_platte_h)
    align_notch.translate(App.Vector(rotor_radius * math.cos(notch_angle), rotor_radius * math.sin(notch_angle), 0))
    r = r.cut(align_notch)

    # 2. Oben/Unten Indikator (Punkte an der Seite bei exakt 126 Grad!)
    # (Genau zwischen Magnet 3 bei 108° und Magnet 4 bei 144°)
    marker_cyl = Part.makeCylinder(1.5, 5.0)
    marker_cyl.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90) # Entlang X drehen
    marker_cyl.translate(App.Vector(rotor_radius - 2.0, 0, rotor_platte_h / 2.0))
    
    if is_top:
        m1 = marker_cyl.copy()
        m1.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 126)
        r = r.cut(m1)
    else:
        m1 = marker_cyl.copy()
        m1.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 122)
        m2 = marker_cyl.copy()
        m2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 130)
        r = r.cut(m1).cut(m2)
        
    return r.removeSplitter()

# 2. BACKPLATE (DECKEL)
def make_backplate(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    k = Part.makeCylinder(kragen_d/2.0, kragen_h)
    if is_top: k.translate(App.Vector(0,0, backplate_h))
    else: k.translate(App.Vector(0,0, -kragen_h))
    p = p.fuse(k).cut(make_square_prism(achse_kantenlaenge+toleranz, 30.0).translate(App.Vector(0,0,-5)))
    
    # Integrierte Stempel (Plugs)
    plug_h = rotor_platte_h - magnet_h - 0.6 
    plug_l = magnet_l + 0.1 
    plug_w = magnet_w + 0.1 
    
    plugs = create_rectangular_array(mag_kreis_r, plug_l, plug_w, plug_h, anzahl_magnete)
    plug_z = -plug_h if is_top else backplate_h
    plugs.translate(App.Vector(0, 0, plug_z))
    p = p.fuse(plugs)
    
    for i in range(5):
        angle = math.radians(i * 72 + 18)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        
        p = p.cut(Part.makeCylinder(3.4 / 2.0, backplate_h + plug_h + 10.0).translate(App.Vector(x, y, -5)))
        senk_z = backplate_h - 1.5 if is_top else 0
        p = p.cut(Part.makeCylinder(6.0 / 2.0, 1.5).translate(App.Vector(x, y, senk_z)))
        
    return p.removeSplitter()

# 3. STATOR WIRD ZUM SCHLITTEN
def make_stator_schlitten():
    s_rad = 47.0
    schlitten_b = Part.makeCylinder(s_rad, stator_dicke)
    schlitten_f = Part.makeBox(s_rad*2, 70.0, stator_dicke).translate(App.Vector(-s_rad, -70.0, 0))
    s = schlitten_b.fuse(schlitten_f)
    griff = Part.makeBox(30.0, 15.0, stator_dicke).translate(App.Vector(-15.0, -85.0, 0))
    s = s.fuse(griff)
    s = s.cut(Part.makeCylinder(12.0, stator_dicke))
    
    spulen_r_oben = (spule_aussen_d + 0.4) / 2.0 
    spulen_r_unten = 5.0 
    
    for i in range(anzahl_spulen):
        angle = math.radians(i * (360.0 / anzahl_spulen))
        x = mag_kreis_r * math.cos(angle)
        y = mag_kreis_r * math.sin(angle)
        fase = Part.makeCone(spulen_r_unten, spulen_r_oben, 1.5)
        zyl = Part.makeCylinder(spulen_r_oben, stator_dicke - 1.5).translate(App.Vector(0, 0, 1.5))
        spulen_loch = fase.fuse(zyl).translate(App.Vector(x, y, 0))
        s = s.cut(spulen_loch)
    
    ring_kanal = Part.makeCylinder(mag_kreis_r + 8.0, 2.5).cut(Part.makeCylinder(mag_kreis_r + 4.0, 2.5))
    ring_kanal.translate(App.Vector(0, 0, stator_dicke - 2.5))
    s = s.cut(ring_kanal)
    
    kanal = Part.makeBox(12.0, 60.0, 2.5).translate(App.Vector(-6.0, -90.0, stator_dicke - 2.5))
    s = s.cut(kanal)
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(-10, -75, 0)))
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(10, -75, 0)))
    
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 41.5 * math.cos(angle)
        y = 41.5 * math.sin(angle)
        loch = Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(x, y, 0))
        s = s.cut(loch)
        
    return s.removeSplitter()

# 4. DECKEL (STATOR-HALTERUNG)
def make_deckel():
    d = Part.makeCylinder(stator_radius, 1.2).cut(Part.makeCylinder(18.0/2.0, 1.2))
    ch = create_circular_array(mag_kreis_r, (spule_aussen_d-1.6)/2.0, 1.2, anzahl_spulen)
    d = d.cut(ch)

    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 41.5 * math.cos(angle)
        y = 41.5 * math.sin(angle)
        d = d.cut(Part.makeCylinder(1.7, 1.2).translate(App.Vector(x,y,0)))
        
    return d

r_o = make_rotor(True); r_u = make_rotor(False)
b_o = make_backplate(True); b_u = make_backplate(False)
s_schlitten = make_stator_schlitten(); s_d = make_deckel()

r_o.translate(App.Vector(0,0,30)); b_o.translate(App.Vector(0,0,45))
s_d.translate(App.Vector(0,0,15))
r_u.translate(App.Vector(0,0,-20)); b_u.translate(App.Vector(0,0,-40))

show_obj(r_o, "Rotor_Oben"); show_obj(r_u, "Rotor_Unten")
show_obj(b_o, "Backplate_Oben"); show_obj(b_u, "Backplate_Unten")
show_obj(s_schlitten, "Stator_Schlitten_KOMBI"); show_obj(s_d, "Stator_Deckel")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")