import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Mini_Generator")

# ==========================================
# ⚙️ PARAMETER (Industrial Sandwich Generator)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

magnet_d = 6.2  
mag_h_gesamt = 4.4 
anzahl_magnete = 16       
mag_kreis_r = 28.0 

anzahl_spulen = 12
spule_innen_d = 7.0       
spule_aussen_d = 14.0     
spule_dicke = 3.5         

stator_radius = 45.0
stator_dicke = spule_dicke
rotor_radius = 38.0
rotor_platte_h = 6.0  
backplate_h = 3.0
kragen_d = 16.0
kragen_h = 12.0

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

# NEU: Der perfekte Radius für die Rotor-Backplate Verschraubung 
# (Zentral zwischen Magneten und Außenkante)
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

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# 1. ROTOR
def make_rotor(is_top):
    r = Part.makeCylinder(rotor_radius, rotor_platte_h)
    mags = create_circular_array(mag_kreis_r, magnet_d/2.0, rotor_platte_h, anzahl_magnete)
    r = r.cut(mags)
    lip_z = 0 if is_top else rotor_platte_h - 0.6
    for i in range(anzahl_magnete):
        angle = math.radians(i * (360.0 / anzahl_magnete))
        x = mag_kreis_r * math.cos(angle); y = mag_kreis_r * math.sin(angle)
        lip = Part.makeCylinder(magnet_d/2.0, 0.6).cut(Part.makeCylinder((magnet_d-1.2)/2.0, 0.6))
        r = r.fuse(lip.translate(App.Vector(x,y,lip_z)))
    r = r.cut(make_square_prism(achse_kantenlaenge + toleranz, rotor_platte_h))
    
    # NEU: 4 Verschraubungslöcher & Muttern-Taschen (von außen!)
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        
        # Durchgangsloch für die M3 Schraube
        r = r.cut(Part.makeCylinder(3.4 / 2.0, rotor_platte_h).translate(App.Vector(x, y, 0)))
        
        # Tasche für Einschmelzmutter (exakt auf der Außenseite, wo die Backplate anliegt)
        taschen_z = rotor_platte_h - einschmelzmutter_t if is_top else 0
        r = r.cut(Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, taschen_z)))
        
    return r

# 2. BACKPLATE (DECKEL)
def make_backplate(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    k = Part.makeCylinder(kragen_d/2.0, kragen_h)
    if is_top: k.translate(App.Vector(0,0, backplate_h))
    else: k.translate(App.Vector(0,0, -kragen_h))
    p = p.fuse(k).cut(make_square_prism(achse_kantenlaenge+toleranz, 30.0).translate(App.Vector(0,0,-5)))
    
    # NEU: 4 Durchgangslöcher & Schraubenkopf-Senkungen (von ganz außen!)
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        
        # Durchgangsloch
        p = p.cut(Part.makeCylinder(3.4 / 2.0, backplate_h).translate(App.Vector(x, y, 0)))
        
        # 1.5mm tiefe Senkung für den M3 Schraubenkopf
        senk_z = backplate_h - 1.5 if is_top else 0
        p = p.cut(Part.makeCylinder(6.0 / 2.0, 1.5).translate(App.Vector(x, y, senk_z)))
        
    return p

# 3. STATOR
def make_stator():
    s = Part.makeCylinder(stator_radius, stator_dicke)
    win = create_circular_array(mag_kreis_r, (spule_aussen_d+0.4)/2.0, stator_dicke, anzahl_spulen)
    s = s.cut(win).cut(Part.makeCylinder(18.0/2.0, stator_dicke))
    term = Part.makeBox(25, 15, stator_dicke).translate(App.Vector(-12.5, -stator_radius-10, 0))
    s = s.fuse(term)
    
    # Schraublöcher außen (Radius 41.5)
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 41.5 * math.cos(angle)
        y = 41.5 * math.sin(angle)
        loch = Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(x, y, 0))
        s = s.cut(loch)
        
    return s

# 4. DECKEL (STATOR-HALTERUNG)
def make_deckel():
    d = Part.makeCylinder(stator_radius, 1.2).cut(Part.makeCylinder(18.0/2.0, 1.2))
    ch = create_circular_array(mag_kreis_r, (spule_aussen_d-1.6)/2.0, 1.2, anzahl_spulen)
    d = d.cut(ch)
    for i in range(6):
        angle = math.radians(i * 60 + 15)
        x = (stator_radius - 3.5) * math.cos(angle); y = (stator_radius - 3.5) * math.sin(angle)
        d = d.cut(Part.makeCylinder(1.7, 1.2).translate(App.Vector(x,y,0)))
    return d

r_o = make_rotor(True); r_u = make_rotor(False)
b_o = make_backplate(True); b_u = make_backplate(False)
s_b = make_stator(); s_d = make_deckel()

r_o.translate(App.Vector(0,0,30)); b_o.translate(App.Vector(0,0,45))
s_d.translate(App.Vector(0,0,15))
r_u.translate(App.Vector(0,0,-20)); b_u.translate(App.Vector(0,0,-40))

show_obj(r_o, "Rotor_Oben"); show_obj(r_u, "Rotor_Unten")
show_obj(b_o, "Backplate_Oben"); show_obj(b_u, "Backplate_Unten")
show_obj(s_b, "Stator_Basis"); show_obj(s_d, "Stator_Deckel")

doc.recompute()