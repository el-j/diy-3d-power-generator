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
mag_kreis_r = 74.0 

# Die NEUEN ovalen Gigant-Spulen (Capsules)
anzahl_spulen = 12
spule_innen_l = 22.0      
spule_innen_w = 8.0       
spule_aussen_l = 40.0     
spule_aussen_w = 26.0     
spule_dicke = 6.0         

stator_radius = 99.0      
stator_dicke = 8.0        
rotor_radius = 90.0       
rotor_platte_h = 6.0  
backplate_h = 4.0
kragen_d = 20.0
kragen_h = 12.0

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

rotor_schraub_r = 50.0    

# NEU: UNIFIED VIELZAHN-SYSTEM (Aus deinem Flügel-Projekt übernommen!)
vielzahn_zaehne = 12       
vielzahn_r_out = 9.0       
vielzahn_r_in = 7.8        
vielzahn_h = 8.0
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

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

def make_vielzahn_prism(r_out, r_in, teeth, height):
    points = []
    for j in range(teeth * 2):
        angle = math.radians(j * (360.0 / (teeth * 2)) + 15)
        r = r_out if j % 2 == 0 else r_in
        points.append(App.Vector(r * math.cos(angle), r * math.sin(angle), 0))
    points.append(points[0]) 
    return Part.Face(Part.Wire(Part.makePolygon(points))).extrude(App.Vector(0, 0, height))

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# 1. ROTOR 
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
    
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        r = r.cut(Part.makeCylinder(3.4 / 2.0, rotor_platte_h).translate(App.Vector(x, y, 0)))
        taschen_z = rotor_platte_h - einschmelzmutter_t if is_top else 0
        r = r.cut(Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, taschen_z)))

    for i in range(5):
        angle = math.radians(i * 72 + 45)
        x = 42.0 * math.cos(angle)
        y = 42.0 * math.sin(angle)
        loch = Part.makeCylinder(16.0, rotor_platte_h).translate(App.Vector(x, y, 0))
        r = r.cut(loch)

    notch_angle = math.radians(45)
    align_notch = Part.makeCylinder(4.0, rotor_platte_h)
    align_notch.translate(App.Vector(rotor_radius * math.cos(notch_angle), rotor_radius * math.sin(notch_angle), 0))
    r = r.cut(align_notch)

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

# 2. BACKPLATE 
def make_backplate(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    k = Part.makeCylinder(kragen_d/2.0, kragen_h)
    if is_top: k.translate(App.Vector(0,0, backplate_h))
    else: k.translate(App.Vector(0,0, -kragen_h))
    p = p.fuse(k).cut(make_square_prism(achse_kantenlaenge+toleranz, 30.0).translate(App.Vector(0,0,-5)))
    
    plug_h = rotor_platte_h - magnet_h - 0.6 
    
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x = rotor_schraub_r * math.cos(angle)
        y = rotor_schraub_r * math.sin(angle)
        p = p.cut(Part.makeCylinder(3.4 / 2.0, backplate_h + plug_h + 10.0).translate(App.Vector(x, y, -5)))
        senk_z = backplate_h - 1.5 if is_top else 0
        p = p.cut(Part.makeCylinder(6.0 / 2.0, 1.5).translate(App.Vector(x, y, senk_z)))
        
    for i in range(5):
        angle = math.radians(i * 72 + 45)
        x = 42.0 * math.cos(angle)
        y = 42.0 * math.sin(angle)
        loch = Part.makeCylinder(16.0, 30.0).translate(App.Vector(x, y, -5))
        p = p.cut(loch)

    kragen_mitte_z = backplate_h + (kragen_h / 2.0) if is_top else -(kragen_h / 2.0)
    for i in range(4):
        angle = i * 90
        m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
        m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        m3_loch.translate(App.Vector(0, 0, kragen_mitte_z))
        m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
        
        m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
        m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, kragen_mitte_z))
        m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
        
        p = p.cut(m3_loch).cut(m3_insert)

    return p.removeSplitter()

# 3. XXL STATOR SCHLITTEN
def make_stator_schlitten():
    schlitten_b = Part.makeCylinder(stator_radius, stator_dicke)
    schlitten_f = Part.makeBox(stator_radius*2, 120.0, stator_dicke).translate(App.Vector(-stator_radius, -120.0, 0))
    s = schlitten_b.fuse(schlitten_f)
    griff = Part.makeBox(50.0, 15.0, stator_dicke).translate(App.Vector(-25.0, -135.0, 0))
    s = s.fuse(griff)
    
    s = s.cut(Part.makeCylinder(16.0, stator_dicke))
    
    for i in range(6):
        angle = math.radians(i * 60)
        x = 35.0 * math.cos(angle)
        y = 35.0 * math.sin(angle)
        s = s.cut(Part.makeCylinder(12.0, stator_dicke).translate(App.Vector(x, y, 0)))

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
    
    ring_kanal = Part.makeCylinder(88.0, 3.5).cut(Part.makeCylinder(82.0, 3.5))
    ring_kanal.translate(App.Vector(0, 0, stator_dicke - 3.5))
    s = s.cut(ring_kanal)
    
    kanal = Part.makeBox(12.0, 115.0, 3.5).translate(App.Vector(-6.0, -135.0, stator_dicke - 3.5))
    s = s.cut(kanal)
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(-15, -127.5, 0)))
    s = s.cut(Part.makeCylinder(1.5, stator_dicke).translate(App.Vector(15, -127.5, 0)))
    
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 94.0 * math.cos(angle)
        y = 94.0 * math.sin(angle)
        s = s.cut(Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(x, y, 0)))
        
    return s.removeSplitter()

# 4. DECKEL (STATOR-HALTERUNG)
def make_deckel():
    d = Part.makeCylinder(stator_radius, 1.2).cut(Part.makeCylinder(16.0, 1.2))
    
    for i in range(6):
        angle = math.radians(i * 60)
        x = 35.0 * math.cos(angle)
        y = 35.0 * math.sin(angle)
        d = d.cut(Part.makeCylinder(12.0, 1.2).translate(App.Vector(x, y, 0)))

    ch = create_capsule_array(mag_kreis_r, spule_aussen_l - 1.0, spule_aussen_w - 1.0, 1.2, anzahl_spulen)
    d = d.cut(ch)

    for i in range(4):
        angle = math.radians(i * 90 + 45)
        x = 94.0 * math.cos(angle)
        y = 94.0 * math.sin(angle)
        d = d.cut(Part.makeCylinder(1.7, 1.2).translate(App.Vector(x,y,0)))
        
    return d

# 5. EINZELNER MAGNET-SPACER
def make_magnet_plug():
    plug_h = rotor_platte_h - magnet_h - 0.6 
    plug = Part.makeBox(magnet_l + 0.1, magnet_w + 0.1, plug_h)
    plug.translate(App.Vector(-(magnet_l + 0.1)/2.0, -(magnet_w + 0.1)/2.0, 0))
    return plug

# 6. ABSTANDS-HÜLSEN
def make_spacer(length, outer_d):
    cyl = Part.makeCylinder(outer_d / 2.0, length)
    hole = make_square_prism(achse_kantenlaenge + toleranz, length)
    return cyl.cut(hole).removeSplitter()


# ==========================================
# 7. KÜHL-LÜFTER RAD (Jetzt Fehlerfrei getrimmt & Optional mit Vielzahn!)
# ==========================================
def make_cooling_fan(with_vielzahn=False):
    fan_r = 85.0           
    fan_h = 10.0           
    hub_r = 16.0           
    blade_count = 11       
    
    fan = Part.makeCylinder(hub_r, fan_h)
    
    def make_blade_profile(radius, chord, thickness, pitch_angle, sweep_angle):
        p1 = App.Vector(-thickness/2.0, -chord/2.0, 0)
        p2 = App.Vector(thickness/2.0, -chord/2.0, 0)
        p3 = App.Vector(thickness/2.0, chord/2.0, 0)
        p4 = App.Vector(-thickness/2.0, chord/2.0, 0)
        w = Part.Wire(Part.makePolygon([p1, p2, p3, p4, p1]))
        w.rotate(App.Vector(0,0,0), App.Vector(1,0,0), pitch_angle)
        w.translate(App.Vector(radius, 0, 0))
        w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), sweep_angle)
        return w

    profiles = [
        make_blade_profile(hub_r - 0.5, 14.0, 1.2, 45, 0),      
        make_blade_profile((hub_r + fan_r)/2.0, 19.0, 1.2, 30, 20), 
        make_blade_profile(fan_r + 0.5, 25.0, 1.2, 20, 45)      
    ]
    
    base_blade = Part.makeLoft(profiles, True)
    base_blade.translate(App.Vector(0, 0, fan_h / 2.0))
    
    for i in range(blade_count):
        angle_deg = i * (360.0 / blade_count)
        b = base_blade.copy()
        b.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        fan = fan.fuse(b)
        
    # BUGFIX: Die Klingen knallhart am inneren Rand des äußeren Schutzrings abschneiden!
    # Verhindert, dass Zacken aus der Hülle ragen.
    fan = fan.common(Part.makeCylinder(fan_r - 2.0, fan_h))
    
    # Schutzring hinzufügen
    ring_out = Part.makeCylinder(fan_r, fan_h)
    ring_in = Part.makeCylinder(fan_r - 2.0, fan_h)
    fan = fan.fuse(ring_out.cut(ring_in))
    
    if with_vielzahn:
        # 2-in-1 Modus: Den Vielzahn Stecker direkt auf den Hub setzen!
        vz_plug = make_vielzahn_prism(vielzahn_r_out, vielzahn_r_in, vielzahn_zaehne, vielzahn_h)
        vz_plug.translate(App.Vector(0,0, fan_h))
        fan = fan.fuse(vz_plug)
        
        # 4x M3 Gewinde in den Kern, um den Lüfter an der Alu-Achse festzuknallen!
        for i in range(4):
            angle = i * 90
            m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
            m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            m3_loch.translate(App.Vector(0, 0, fan_h / 2.0))
            m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            
            m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
            m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            m3_insert.translate(App.Vector(hub_r - einschmelzmutter_t, 0, fan_h / 2.0))
            m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            fan = fan.cut(m3_loch).cut(m3_insert)
            
        hole_h = fan_h + vielzahn_h + 2.0
    else:
        hole_h = fan_h + 2.0
        
    # Zentrales 10x10 Achsenloch ausstanzen
    hole = make_square_prism(achse_kantenlaenge + toleranz, hole_h)
    hole.translate(App.Vector(0,0,-1.0))
    fan = fan.cut(hole)
    
    cut_top = Part.makeBox(200, 200, 20).translate(App.Vector(-100, -100, fan_h + (vielzahn_h if with_vielzahn else 0)))
    cut_bot = Part.makeBox(200, 200, 20).translate(App.Vector(-100, -100, -20))
    fan = fan.cut(cut_top).cut(cut_bot)
    
    return fan.removeSplitter()



r_o = make_rotor(True); r_u = make_rotor(False)
b_o = make_backplate(True); b_u = make_backplate(False)
s_schlitten = make_stator_schlitten(); s_d = make_deckel()
m_plug = make_magnet_plug()
spacer_innen = make_spacer(10.0, kragen_d)
spacer_unten = make_spacer(7.0, 28.0)

# Zwei Versionen des Lüfters generieren:
luefter_unten = make_cooling_fan(with_vielzahn=False)
luefter_oben = make_cooling_fan(with_vielzahn=True)

r_o.translate(App.Vector(0,0,30)); b_o.translate(App.Vector(0,0,45))
s_d.translate(App.Vector(0,0,15))
r_u.translate(App.Vector(0,0,-20)); b_u.translate(App.Vector(0,0,-40))
m_plug.translate(App.Vector(120, 0, 0))

spacer_innen.translate(App.Vector(130, 30, 0))
spacer_unten.translate(App.Vector(130, -30, 0))

luefter_unten.translate(App.Vector(-130, -45, 0))
luefter_oben.translate(App.Vector(-130, 45, 0))

show_obj(r_o, "Rotor_Oben_XXL"); show_obj(r_u, "Rotor_Unten_XXL")
show_obj(b_o, "Backplate_Oben_XXL"); show_obj(b_u, "Backplate_Unten_XXL")
show_obj(s_schlitten, "Stator_Schlitten_XXL"); show_obj(s_d, "Stator_Deckel_XXL")
show_obj(m_plug, "Magnet_Spacer_Kloetzchen")
show_obj(spacer_innen, "Abstands_Huelse_Rotoren")
show_obj(spacer_unten, "Abstands_Huelse_Lager")
show_obj(luefter_unten, "Kuehl_Luefter_Unten")
show_obj(luefter_oben, "Kuehl_Luefter_Oben_Mit_Vielzahn")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")