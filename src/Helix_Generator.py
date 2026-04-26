import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Mini_Generator")

# ==========================================
# ⚙️ PARAMETER (Industrial Sandwich Generator - V4 SOLID & CLEAN)
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Magnete (Gizeh-Filter) - 2 Lagen
magnet_d = 6.2  
mag_h_einzel = 2.2
mag_lagen = 2           
mag_h_gesamt = mag_h_einzel * mag_lagen
anzahl_magnete = 16       
mag_kreis_r = 28.0 

# Kupferspulen 
anzahl_spulen = 12
spule_innen_d = 7.0       
spule_aussen_d = 14.0     
spule_dicke = 3.5         

# Bauteil-Stärken
stator_radius = 45.0
stator_dicke = spule_dicke
rotor_radius = 38.0
rotor_platte_h = 6.0  
backplate_h = 3.0
lip_h = 0.6 # Haltekante (Richtung Stator)
kragen_d = 16.0 # Stabilerer Kragen
kragen_h = 12.0

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0       
senkkopf_d = 6.2         
senkkopf_t = 2.0  
schlitten_lochabstand = 31.0 
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def create_circular_array(radius, item_radius, depth, count):
    items = []
    for i in range(count):
        angle = math.radians(i * (360.0 / count))
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        item = Part.makeCylinder(item_radius, depth)
        item.translate(App.Vector(x, y, 0))
        items.append(item)
    array_shape = items[0]
    for m in items[1:]:
        array_shape = array_shape.fuse(m)
    return array_shape

# ==========================================
# BAUTEIL 1: MODULARER ROTOR
# ==========================================
def erstelle_rotor_solid(name, is_top_rotor):
    r = Part.makeCylinder(rotor_radius, rotor_platte_h)
    mag_holes = create_circular_array(mag_kreis_r, magnet_d / 2.0, rotor_platte_h, anzahl_magnete)
    r = r.cut(mag_holes)
    lip_z = 0 if is_top_rotor else rotor_platte_h - lip_h
    for i in range(anzahl_magnete):
        angle = math.radians(i * (360.0 / anzahl_magnete))
        lx = mag_kreis_r * math.cos(angle); ly = mag_kreis_r * math.sin(angle)
        outer_c = Part.makeCylinder(magnet_d / 2.0, lip_h)
        inner_c = Part.makeCylinder((magnet_d - 1.2) / 2.0, lip_h)
        lip = outer_c.cut(inner_c); lip.translate(App.Vector(lx, ly, lip_z)); r = r.fuse(lip)
    achse = make_square_prism(achse_kantenlaenge + toleranz, rotor_platte_h)
    r = r.cut(achse)
    for i in range(4):
        angle = math.radians(i * 90 + 45); x = (rotor_radius - 5.0) * math.cos(angle); y = (rotor_radius - 5.0) * math.sin(angle)
        hole = Part.makeCylinder(3.4 / 2.0, rotor_platte_h)
        insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t)
        iz = rotor_platte_h - einschmelzmutter_t if not is_top_rotor else 0
        insert.translate(App.Vector(x,y,iz)); r = r.cut(hole).cut(insert)
    return r.removeSplitter()

# ==========================================
# BAUTEIL 2: DIE SCHAFT-BACKPLATE
# ==========================================
def erstelle_backplate_mit_schaft(is_top):
    p = Part.makeCylinder(rotor_radius, backplate_h)
    k = Part.makeCylinder(kragen_d / 2.0, kragen_h)
    if is_top: k.translate(App.Vector(0,0, backplate_h))
    else: k.translate(App.Vector(0,0, -kragen_h))
    p = p.fuse(k)
    achse = make_square_prism(achse_kantenlaenge + toleranz, kragen_h + backplate_h + 10)
    achse.translate(App.Vector(0,0, -5)); p = p.cut(achse)
    for i in range(4):
        angle = math.radians(i * 90 + 45); x = (rotor_radius - 5.0) * math.cos(angle); y = (rotor_radius - 5.0) * math.sin(angle)
        hole = Part.makeCylinder(3.4 / 2.0, backplate_h); p = p.cut(hole)
    m3_lock = Part.makeCylinder(3.4 / 2.0, 20.0); m3_lock.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    z_pos = backplate_h + (kragen_h/2.0) if is_top else -(kragen_h/2.0)
    m3_lock.translate(App.Vector(-10, 0, z_pos)); p = p.cut(m3_lock)
    return p.removeSplitter()

# ==========================================
# BAUTEIL 3: FENSTER-STATOR 
# ==========================================
def erstelle_stator():
    st = Part.makeCylinder(stator_radius, stator_dicke)
    windows = create_circular_array(mag_kreis_r, (spule_aussen_d + 0.4) / 2.0, stator_dicke, anzahl_spulen)
    st = st.cut(windows)
    for i in range(anzahl_spulen):
        angle = math.radians(i * 30); x = mag_kreis_r * math.cos(angle); y = mag_kreis_r * math.sin(angle)
        lip = Part.makeCylinder((spule_aussen_d+0.4)/2, 0.4).cut(Part.makeCylinder((spule_aussen_d-1.2)/2, 0.4))
        lip.translate(App.Vector(x,y,0)); st = st.fuse(lip)
    terminal = Part.makeBox(25, 15, stator_dicke)
    terminal.translate(App.Vector(-12.5, -stator_radius - 10.0, 0)); st = st.fuse(terminal)
    st = st.cut(Part.makeCylinder(18.0 / 2.0, stator_dicke))
    for dx in [-15.5, 15.5]:
        for dy in [-15.5, 15.5]:
            st = st.cut(Part.makeCylinder(1.7, stator_dicke).translate(App.Vector(dx,dy,0)))
    return st.removeSplitter()

# ==========================================
# BAUTEIL 4: SKELETT-DECKEL & WICKEL-TOOL
# ==========================================
def erstelle_stator_deckel():
    d = Part.makeCylinder(stator_radius, 1.2).cut(Part.makeCylinder(18.0 / 2.0, 1.2))
    copper_holes = create_circular_array(mag_kreis_r, (spule_aussen_d - 1.6) / 2.0, 1.2, anzahl_spulen)
    d = d.cut(copper_holes)
    t_cut = Part.makeBox(25, 15, 1.2)
    t_cut.translate(App.Vector(-12.5, -stator_radius - 10.0, 0)); d = d.fuse(t_cut)
    return d.removeSplitter()

def erstelle_wickel_tool():
    wb = Part.makeCylinder(15, 2).fuse(Part.makeCylinder(spule_innen_d/2, spule_dicke).translate(App.Vector(0,0,2)))
    wb = wb.cut(Part.makeCylinder(1.7, 10))
    wd = Part.makeCylinder(15, 2).cut(Part.makeCylinder(1.7, 2))
    return wb.removeSplitter(), wd.removeSplitter()

# ==========================================
# LAYOUT & ANORDNUNG
# ==========================================
rotor_oben = erstelle_rotor_solid("Rotor_Oben", True)
rotor_unten = erstelle_rotor_solid("Rotor_Unten", False)
back_oben = erstelle_backplate_mit_schaft(True)
back_unten = erstelle_backplate_mit_schaft(False)
stator_basis = erstelle_stator()
stator_deckel = erstelle_stator_deckel()
wickel_basis, wickel_deckel = erstelle_wickel_tool()

# Explosions-Anordnung
back_oben.translate(App.Vector(0, 0, 45))
rotor_oben.translate(App.Vector(0, 0, 30))
stator_deckel.translate(App.Vector(0, 0, 15))
stator_basis.translate(App.Vector(0, 0, 0))
rotor_unten.translate(App.Vector(0, 0, -20))
back_unten.translate(App.Vector(0, 0, -40))

wickel_basis.translate(App.Vector(100, 0, 0))
wickel_deckel.translate(App.Vector(135, 0, 0))

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

show_obj(rotor_oben, "Rotor_Oben")
show_obj(rotor_unten, "Rotor_Unten")
show_obj(stator_basis, "Stator_Basis")
show_obj(stator_deckel, "Stator_Skelett_Deckel")
show_obj(back_oben, "Backplate_Oben")
show_obj(back_unten, "Backplate_Unten")
show_obj(wickel_basis, "Wickelhilfe_Basis")
show_obj(wickel_deckel, "Wickelhilfe_Deckel")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")
print("DIY Mini Generator - Alle Objekte benannt!")