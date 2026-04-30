import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Kraftpaket_Generator")

# ==========================================
# ⚙️ PARAMETER (XXL 20-Pol Sandwich Generator)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Die 20 eckigen Magnete 
magnet_l = 20.0  
magnet_w = 5.0   
magnet_h = 3.0   
anzahl_magnete = 20       
mag_kreis_r = 74.0 

# Die ovalen Gigant-Spulen
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

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

rotor_schraub_r = 50.0    

# LAGER-ZENTRIERUNG
lager_innen_d = 29.0      
adapter_pressfit = 0.15

# DAS NEUE UNIFIED VIELZAHN-CLAMP-SYSTEM!
vielzahn_zaehne = 12       
vielzahn_r_out = 9.0       
vielzahn_r_in = 7.8        
# 10.0mm hoch = Passt EXAKT bündig durch 1 Lüfter (10mm) ODER 1 Rotor-Sandwich (4+6=10mm)
vielzahn_h = 10.0          
kragen_d = 20.0            # Standard Durchmesser für alle Universal-Klemmen
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


# ==========================================
# DAS HERZSTÜCK: DIE UNIVERSAL VIELZAHN-CLAMP
# Ersetzt alle starren Kragen und Abstandshülsen!
# ==========================================
def make_universal_clamp(kragen_laenge, with_m3=True):
    # Der Stecker (Männlich), auf den alles aufgesteckt wird
    plug = make_vielzahn_prism(vielzahn_r_out, vielzahn_r_in, vielzahn_zaehne, vielzahn_h)
    plug.translate(App.Vector(0, 0, kragen_laenge))
    
    # Der Kragen (Bestimmt den Abstand / Spacing)
    kragen = Part.makeCylinder(kragen_d / 2.0, kragen_laenge)
    clamp = kragen.fuse(plug)
    
    # Durchgehendes 10x10 Achsloch
    hole = make_square_prism(achse_kantenlaenge + toleranz, kragen_laenge + vielzahn_h + 2.0)
    hole.translate(App.Vector(0, 0, -1.0))
    clamp = clamp.cut(hole)
    
    # 4x M3 Fixierung (nur wenn der Kragen hoch genug ist)
    if with_m3 and kragen_laenge >= 6.0:
        for i in range(4):
            angle = i * 90
            m3_loch = Part.makeCylinder(3.4 / 2.0, 20.0)
            m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            m3_loch.translate(App.Vector(0, 0, kragen_laenge / 2.0))
            m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            
            m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
            m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
            m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t, 0, kragen_laenge / 2.0))
            m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
            
            clamp = clamp.cut(m3_loch).cut(m3_insert)
            
    return clamp.removeSplitter()


# 1. ROTOR (Jetzt mit Vielzahn-Loch statt Vierkant!)
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
        
    # NEU: Das Loch in der Mitte ist nun eine Vielzahn-Kupplung!
    vz_cut = make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, rotor_platte_h + 2.0)
    vz_cut.translate(App.Vector(0, 0, -1.0))
    r = r.cut(vz_cut)
    
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

# 2. BACKPLATE (Jetzt absolut flach und mit Vielzahn!)
def make_backplate(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    
    # NEU: Auch die Backplate nutzt die Universal-Vielzahn Kupplung!
    vz_cut = make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, backplate_h + 2.0)
    vz_cut.translate(App.Vector(0, 0, -1.0))
    p = p.cut(vz_cut)
    
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


# ==========================================
# 6. LAGER-REDUZIERUNG
# ==========================================
def make_lager_reduzierung():
    adapter_d = lager_innen_d + adapter_pressfit
    fase = Part.makeCone((adapter_d - 1.5)/2.0, adapter_d/2.0, 2.0)
    schaft = Part.makeCylinder(adapter_d/2.0, 13.0).translate(App.Vector(0,0,2.0))
    kragen = Part.makeCylinder(34.0/2.0, 2.0).translate(App.Vector(0,0,15.0))
    hole = make_square_prism(achse_kantenlaenge + toleranz, 20.0).translate(App.Vector(0,0,-1.0))
    return fase.fuse(schaft).fuse(kragen).cut(hole).removeSplitter()


# ==========================================
# 7. KÜHL-LÜFTER RAD (Jetzt rein modular mit Vielzahn-Loch!)
# ==========================================
def make_cooling_fan():
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
        
    fan = fan.common(Part.makeCylinder(fan_r - 2.0, fan_h))
    
    ring_out = Part.makeCylinder(fan_r, fan_h)
    ring_in = Part.makeCylinder(fan_r - 2.0, fan_h)
    fan = fan.fuse(ring_out.cut(ring_in))
    
    # NEU: Das universelle weibliche Vielzahn-Loch!
    vz_cut = make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, fan_h + 2.0)
    vz_cut.translate(App.Vector(0,0,-1.0))
    fan = fan.cut(vz_cut)
    
    cut_top = Part.makeBox(200, 200, 20).translate(App.Vector(-100, -100, fan_h))
    cut_bot = Part.makeBox(200, 200, 20).translate(App.Vector(-100, -100, -20))
    fan = fan.cut(cut_top).cut(cut_bot)
    
    return fan.removeSplitter()



# --- BAUTEILE GENERIEREN ---
r_o = make_rotor(True); r_u = make_rotor(False)
b_o = make_backplate(True); b_u = make_backplate(False)
s_schlitten = make_stator_schlitten(); s_d = make_deckel()
m_plug = make_magnet_plug()

reduzierung_unten = make_lager_reduzierung()
reduzierung_oben = make_lager_reduzierung()
luefter_unten = make_cooling_fan()
luefter_oben = make_cooling_fan()

# NEU: Die modularen "Universal Clamps" in verschiedenen Spacer-Längen!
clamp_luefter_unten = make_universal_clamp(8.0)  # Kragen sitzt auf unterem Lager
clamp_generator_unten = make_universal_clamp(8.0) # Hebt Generator an
clamp_generator_mitte = make_universal_clamp(12.0) # Sichert Stator-Luftspalt (Geht durch den Stator!)
clamp_luefter_oben = make_universal_clamp(25.0)   # Längerer Spacer nach oben zum Lüfter
clamp_turm_adapter = make_universal_clamp(8.0)   # Sitzt oben auf dem Deckel, empfängt den Turm!


# --- EXPLOSIONS-ANSICHT ANORDNEN ---
reduzierung_unten.translate(App.Vector(0, 0, -60))
clamp_luefter_unten.translate(App.Vector(0, 0, -45))
luefter_unten.translate(App.Vector(0, 0, -37))

clamp_generator_unten.translate(App.Vector(0, 0, -22))
b_u.translate(App.Vector(0, 0, -14))
r_u.translate(App.Vector(0, 0, -10))

clamp_generator_mitte.translate(App.Vector(0, 0, 5))
s_d.translate(App.Vector(0, 0, 10))
s_schlitten.translate(App.Vector(0, 0, 12))

r_o.translate(App.Vector(0, 0, 27))
b_o.translate(App.Vector(0, 0, 33))

clamp_luefter_oben.translate(App.Vector(0, 0, 37))
luefter_oben.translate(App.Vector(0, 0, 62))

clamp_turm_adapter.translate(App.Vector(0, 0, 77))
reduzierung_oben.translate(App.Vector(0, 0, 95))

m_plug.translate(App.Vector(120, 0, 0))


show_obj(reduzierung_unten, "1_Lager_Reduzierung_Unten")
show_obj(clamp_luefter_unten, "2_Clamp_Luefter_Unten")
show_obj(luefter_unten, "3_Kuehl_Luefter_Unten")

show_obj(clamp_generator_unten, "4_Clamp_Generator_Unten")
show_obj(b_u, "5_Backplate_Unten_XXL")
show_obj(r_u, "6_Rotor_Unten_XXL")

show_obj(clamp_generator_mitte, "7_Clamp_Generator_Mitte_Luftspalt")
show_obj(s_d, "8_Stator_Deckel_XXL")
show_obj(s_schlitten, "9_Stator_Schlitten_XXL")

show_obj(r_o, "10_Rotor_Oben_XXL")
show_obj(b_o, "11_Backplate_Oben_XXL")

show_obj(clamp_luefter_oben, "12_Clamp_Luefter_Oben")
show_obj(luefter_oben, "13_Kuehl_Luefter_Oben")

show_obj(clamp_turm_adapter, "14_Clamp_Turm_Adapter")
show_obj(reduzierung_oben, "15_Lager_Reduzierung_Oben")

show_obj(m_plug, "Magnet_Spacer_Kloetzchen")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")