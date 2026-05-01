import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Kraftpaket_Generator")

# ==========================================
# ⚙️ PARAMETER (Aero-Donut Generator)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

magnet_l = 20.0  
magnet_w = 5.0   
magnet_h = 3.0   
anzahl_magnete = 20       
mag_kreis_r = 74.0 

anzahl_spulen = 12
spule_innen_l = 22.0      
spule_innen_w = 8.0       
spule_aussen_l = 40.0     
spule_aussen_w = 26.0     
spule_dicke = 6.0         

stator_radius = 99.0      
stator_dicke = 9.0        

# ==========================================
# 🔥 OPTIMIERTE MAßE FÜR 0.6mm NOZZLE & PLA-CF
# ==========================================
rotor_radius = 98.0       
rotor_platte_h = 10.0     
backplate_h = 4.0         
rotor_schraub_r = 74.0    

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       

lager_innen_d = 29.0      
adapter_pressfit = 0.15

# UNIFIED VIELZAHN-SYSTEM
vielzahn_zaehne = 12       
vielzahn_r_out = 9.0       
vielzahn_r_in = 7.8        
kragen_d = 20.0            
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

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

# ==========================================
# 🛸 DER MASSIVE PANZER-ROTOR (MIT MATERIAL-SPAR-TASCHEN)
# ==========================================
def make_aero_rotor(is_top):
    fan_r = rotor_radius    
    fan_h = rotor_platte_h  
    hub_r = 16.5  
    blade_count = 11       
    hub = Part.makeCylinder(hub_r, fan_h)
    
    def make_blade_profile(radius, chord, thickness, pitch_angle, sweep_angle):
        p1 = App.Vector(-thickness/2.0, -chord/2.0, 0)
        p2 = App.Vector(thickness/2.0, -chord/2.0, 0)
        p3 = App.Vector(thickness/2.0, chord/2.0, 0)
        p4 = App.Vector(-thickness/2.0, chord/2.0, 0)
        w = Part.Wire(Part.makePolygon([p1, p2, p3, p4, p1]))
        w.rotate(App.Vector(0,0,0), App.Vector(1,0,0), pitch_angle)
        w.translate(App.Vector(radius, 0, 0))
        w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), sweep_angle)
        return Part.Face(w)

    blade_thick = 4.2
    p_inner = make_blade_profile(hub_r - 5.0, 22.0, blade_thick, 75, 0)
    p_outer = make_blade_profile(fan_r + 15.0, 32.0, blade_thick, 50, 45)
    one_blade = Part.makeLoft([p_inner, p_outer], True, True)
    one_blade.translate(App.Vector(0, 0, fan_h / 2.0))
    all_blades = one_blade.copy()
    for i in range(1, blade_count):
        b = one_blade.copy()
        b.rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * (360.0 / blade_count))
        all_blades = all_blades.fuse(b)
    
    outer_ring = Part.makeCylinder(fan_r + 10.0, fan_h).cut(Part.makeCylinder(fan_r - 3.0, fan_h))
    donut = Part.makeCylinder(86.0, fan_h).cut(Part.makeCylinder(62.0, fan_h))
    combined = hub.fuse(all_blades).fuse(outer_ring).fuse(donut)
    for i in range(5):
        spoke = Part.makeBox(60.0, 5.0, 3.0).translate(App.Vector(14.0, -2.5, 0)).rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * 72 + 9)
        combined = combined.fuse(spoke)
    fan = combined.common(Part.makeCylinder(fan_r, fan_h))
    vz_cut = make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, fan_h + 2.0).translate(App.Vector(0,0,-1.0))
    mags = create_rectangular_array(mag_kreis_r, magnet_l + 0.4, magnet_w + 0.4, fan_h + 2.0, anzahl_magnete).translate(App.Vector(0, 0, -1.0))
    fan = fan.cut(vz_cut).cut(mags)
    
    # 🔥 NEU: KORRIGIERTE MATERIAL-EINSPARUNG (Exakt 15 Taschen)
    for i in range(anzahl_magnete):
        # Die Schrauben sitzen bei i=0, 4, 8, 12, 16. (Da 360/20 = 18 Grad. 18*0=0, 18*4=72. Das passt nicht zu den 9 Grad der Schrauben.)
        # Schrauben sitzen exakt bei 9, 81, 153, 225, 297 Grad.
        # Magnet-Zwischenräume (Zentrum des Zwischenraums) liegen bei: 9, 27, 45, 63, 81, 99... Grad.
        # Das bedeutet, die Schrauben (9, 81, 153...) liegen GENAU auf den Zwischenräumen i=0, 4, 8, 12, 16!
        # Wenn i = 0, 4, 8, 12, 16 -> DIESE AUSLASSEN!
        if i % 4 == 0:
            continue
            
        # Winkel für das Zentrum des Zwischenraums berechnen
        angle_deg = i * (360.0 / anzahl_magnete) + (360.0 / anzahl_magnete / 2.0)
        angle_rad = math.radians(angle_deg)
        pocket = make_capsule(18.0, 10.0, fan_h + 2.0)
        pocket.translate(App.Vector(0, 0, -1.0))
        pocket.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        pocket.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), 0))
        fan = fan.cut(pocket)
    
    lip_z = 0 if is_top else fan_h - 0.6
    for i in range(anzahl_magnete):
        angle = math.radians(i * (360.0 / anzahl_magnete))
        lip = Part.makeBox(magnet_l+0.4, magnet_w+0.4, 0.6).translate(App.Vector(-(magnet_l+0.4)/2, -(magnet_w+0.4)/2, 0)).cut(Part.makeBox(magnet_l-1.5, magnet_w-1.5, 0.6).translate(App.Vector(-(magnet_l-1.5)/2, -(magnet_w-1.5)/2, 0)))
        lip.rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * (360.0 / anzahl_magnete))
        lip.translate(App.Vector(mag_kreis_r * math.cos(angle), mag_kreis_r * math.sin(angle), lip_z))
        fan = fan.fuse(lip)
    
    # Verschraubungen (Sitzen exakt in den unbeschnittenen Segmenten!)
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x, y = rotor_schraub_r * math.cos(angle), rotor_schraub_r * math.sin(angle)
        fan = fan.cut(Part.makeCylinder(3.4 / 2.0, 15.0).translate(App.Vector(x, y, -1.0)))
        tz = fan_h - einschmelzmutter_t if is_top else 0
        fan = fan.cut(Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t).translate(App.Vector(x, y, tz)))
    return fan.removeSplitter()

# ==========================================
# 🧱 SKELETON STATOR (MIT PRÄZISER SCHICHTUNG & TASCHEN)
# ==========================================
def make_stator_schlitten():
    base = Part.makeCylinder(stator_radius, stator_dicke)
    front = Part.makeBox(stator_radius*2, 120.0, stator_dicke).translate(App.Vector(-stator_radius, -120.0, 0))
    griff = Part.makeBox(50.0, 15.0, stator_dicke).translate(App.Vector(-25.0, -135.0, 0))
    s = base.fuse(front).fuse(griff)
    
    s = s.cut(Part.makeCylinder(16.0, stator_dicke))
    
    # Materialeinsparung in der Mitte (Zentrum)
    for i in range(6):
        angle = math.radians(i * 60 + 30)
        hole = Part.makeCylinder(14.0, stator_dicke).translate(App.Vector(35.0 * math.cos(angle), 35.0 * math.sin(angle), 0))
        s = s.cut(hole)

    # Spulenkammern 
    for i in range(anzahl_spulen):
        angle = math.radians(i * (360.0 / anzahl_spulen))
        pocket = make_capsule(spule_aussen_l + 0.4, spule_aussen_w + 0.4, 6.0).rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * (360.0/anzahl_spulen)).translate(App.Vector(mag_kreis_r * math.cos(angle), mag_kreis_r * math.sin(angle), 0.5))
        thru = make_capsule(spule_aussen_l - 1.5, spule_aussen_w - 1.5, stator_dicke).rotate(App.Vector(0,0,0), App.Vector(0,0,1), i * (360.0/anzahl_spulen)).translate(App.Vector(mag_kreis_r * math.cos(angle), mag_kreis_r * math.sin(angle), 0))
        s = s.cut(pocket).cut(thru)

    # MATERIALEINSPARUNG ZWISCHEN DEN SPULEN
    for i in range(anzahl_spulen):
        angle_deg = i * (360.0 / anzahl_spulen) + (360.0 / anzahl_spulen / 2.0)
        angle_rad = math.radians(angle_deg)
        pocket = make_capsule(20.0, 6.0, stator_dicke + 2.0).translate(App.Vector(0,0,-1.0))
        pocket.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        pocket.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), 0))
        s = s.cut(pocket)
    
    # Kabel-Kanäle 
    ring_kanal = Part.makeCylinder(88.0, 1.0).cut(Part.makeCylinder(82.0, 1.0)).translate(App.Vector(0, 0, 6.5))
    s = s.cut(ring_kanal)
    
    kanal_radial = Part.makeBox(12.0, 70.0, 2.5).translate(App.Vector(-6.0, -135.0, 6.5))
    s = s.cut(kanal_radial)

    lid_pocket = Part.makeCylinder(96.0, 1.5).cut(Part.makeCylinder(50.0, 1.5)).translate(App.Vector(0, 0, 7.5))
    s = s.cut(lid_pocket)
    
    # Verschraubung 
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        s = s.cut(Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(91.0 * math.cos(angle), 91.0 * math.sin(angle), 0)))
        
    return s.removeSplitter()

# ==========================================
# 🧱 STATOR DONUT-DECKEL (BÜNDIG + MATERIAL-SPAREND)
# ==========================================
def make_stator_deckel():
    d = Part.makeCylinder(95.5, 1.5).cut(Part.makeCylinder(50.5, 1.5))
    ch = create_capsule_array(mag_kreis_r, spule_aussen_l - 1.0, spule_aussen_w - 1.0, 1.5, anzahl_spulen)
    d = d.cut(ch)
    
    # MATERIALEINSPARUNG ZWISCHEN DEN SPULEN (Synchron zum Stator)
    for i in range(anzahl_spulen):
        angle_deg = i * (360.0 / anzahl_spulen) + (360.0 / anzahl_spulen / 2.0)
        angle_rad = math.radians(angle_deg)
        pocket = make_capsule(20.0, 6.0, 3.0).translate(App.Vector(0,0,-1.0))
        pocket.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        pocket.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), 0))
        d = d.cut(pocket)
    
    for i in range(4):
        angle = math.radians(i * 90 + 45)
        d = d.cut(Part.makeCylinder(1.7, 1.5).translate(App.Vector(91.0 * math.cos(angle), 91.0 * math.sin(angle), 0)))
    return d.removeSplitter()

# ==========================================
# 🧱 ROTOR BACKPLATE (MATERIAL-SPAREND)
# ==========================================
def make_aero_backplate(is_top):
    p = Part.makeCylinder(86.0, backplate_h).cut(Part.makeCylinder(62.0, backplate_h))
    
    # 🔥 NEU: Material-Einsparung exakt synchron zum Rotor (15 Taschen)
    for i in range(anzahl_magnete):
        if i % 4 == 0:  # Die 5 Schraubenlöcher überspringen
            continue
        angle_deg = i * (360.0 / anzahl_magnete) + (360.0 / anzahl_magnete / 2.0)
        angle_rad = math.radians(angle_deg)
        pocket = make_capsule(18.0, 10.0, backplate_h + 2.0).translate(App.Vector(0,0,-1.0))
        pocket.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle_deg)
        pocket.translate(App.Vector(mag_kreis_r * math.cos(angle_rad), mag_kreis_r * math.sin(angle_rad), 0))
        p = p.cut(pocket)
    
    # Verschraubungen
    for i in range(5):
        angle = math.radians(i * 72 + 9)
        x, y = rotor_schraub_r * math.cos(angle), rotor_schraub_r * math.sin(angle)
        p = p.cut(Part.makeCylinder(3.4 / 2.0, 15.0).translate(App.Vector(x, y, -5)))
        sz = backplate_h - 1.5 if is_top else 0
        p = p.cut(Part.makeCylinder(6.0 / 2.0, 1.5).translate(App.Vector(x, y, sz)))
    return p.removeSplitter()

# --- HILFSKOMPONENTEN ---
def make_universal_clamp(kl, pl):
    c = Part.makeCylinder(kragen_d / 2.0, kl)
    if pl > 0: c = c.fuse(make_vielzahn_prism(vielzahn_r_out, vielzahn_r_in, vielzahn_zaehne, pl).translate(App.Vector(0,0,kl)))
    c = c.cut(make_square_prism(achse_kantenlaenge + toleranz, kl + pl + 2.0).translate(App.Vector(0,0,-1.0)))
    return c.removeSplitter()

def make_vielzahn_spacer(l, od):
    return Part.makeCylinder(od / 2.0, l).cut(make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, l + 2.0).translate(App.Vector(0,0,-1.0))).removeSplitter()


def make_magnet_plug():
    plug_h = rotor_platte_h - magnet_h - 0.6 
    plug = Part.makeBox(magnet_l + 0.1, magnet_w + 0.1, plug_h)
    plug.translate(App.Vector(-(magnet_l + 0.1)/2.0, -(magnet_w + 0.1)/2.0, 0))
    return plug


def make_lager_reduzierung():
    adapter_d = lager_innen_d + adapter_pressfit
    fase = Part.makeCone((adapter_d - 1.5)/2.0, adapter_d/2.0, 2.0)
    schaft = Part.makeCylinder(adapter_d/2.0, 16.0).translate(App.Vector(0,0,2.0))
    kragen = Part.makeCylinder(34.0/2.0, 2.0).translate(App.Vector(0,0,18.0))
    
    vz_cut = make_vielzahn_prism(vielzahn_r_out + 0.2, vielzahn_r_in + 0.2, vielzahn_zaehne, 22.0)
    vz_cut.translate(App.Vector(0,0,-1.0))
    
    return fase.fuse(schaft).fuse(kragen).cut(vz_cut).removeSplitter()

# --- BAUTEILE GENERIEREN ---
r_u = make_aero_rotor(False); r_o = make_aero_rotor(True)
b_u = make_aero_backplate(False); b_o = make_aero_backplate(True)
stator = make_stator_schlitten(); deckel = make_stator_deckel()
clamp_mega = make_universal_clamp(8.0, 30.0)
st_spacer = make_vielzahn_spacer(10.0, kragen_d)
reduzierung_unten = make_lager_reduzierung()
reduzierung_oben = make_lager_reduzierung()
m_plug = make_magnet_plug()


# ==========================================
# DAS MASTER-SETUP (Der ultra-kompakte 30mm Core!)
# ==========================================
clamp_lager_unten = make_universal_clamp(kragen_laenge=8.0, plug_laenge=20.0, with_m3=True)
clamp_lager_oben = make_universal_clamp(kragen_laenge=8.0, plug_laenge=20.0, with_m3=True)

# --- EXPLOSIONS-ANSICHT ANORDNEN ---
reduzierung_unten.translate(App.Vector(0, 0, -80))
clamp_lager_unten.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 180) 
clamp_lager_unten.translate(App.Vector(0, 0, -60))

clamp_mega.translate(App.Vector(0, 0, -50))
b_u.translate(App.Vector(0, 0, -30))
r_u.translate(App.Vector(0, 0, -20))
st_spacer.translate(App.Vector(0, 0, -5))
stator.translate(App.Vector(0, 0, 10))
deckel.translate(App.Vector(0, 0, 25)) 
r_o.translate(App.Vector(0, 0, 35))
b_o.translate(App.Vector(0, 0, 50))

clamp_lager_oben.translate(App.Vector(0, 0, 90))
reduzierung_oben.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 180) 
reduzierung_oben.translate(App.Vector(0, 0, 110))


m_plug.translate(App.Vector(120, 0, 0))

# --- ANZEIGEN ---
show_obj(clamp_lager_unten, "01_Clamp_Lager_Unten")
show_obj(reduzierung_unten, "02_Lager_Reduzierung_Unten")


show_obj(clamp_mega, "03_Clamp_Rotor_Stack_Mega_30mm")
show_obj(b_u, "04_Backplate_Ring_FLACH_Unten")
show_obj(r_u, "05_Rotor_AeroFan_TANK_FINAL_Unten")
show_obj(stator, "07_Stator_Schlitten_XXL")
show_obj(deckel, "08_Stator_Donut_Deckel_INSET")
show_obj(r_o, "09_Rotor_AeroFan_TANK_FINAL_Oben")
show_obj(b_o, "10_Backplate_Ring_FLACH_Oben")
show_obj(st_spacer, "11_Stator_Abstands_Spacer_10mm")

show_obj(clamp_lager_oben, "12_Clamp_Lager_Oben")
show_obj(reduzierung_oben, "13_Lager_Reduzierung_Oben")
show_obj(m_plug, "14_Magnet_Spacer_Kloetzchen")

doc.recompute()