import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station")

# ==========================================
# ⚙️ PARAMETER FÜR DIE BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Maße für das Kegelrollenlager (32005)
lager_innen_d = 25.0      
lager_aussen_d = 47.0     
lager_dicke = 15.0        

# Schlitten & Generator
schlitten_breite = 95.0 
fuss_radius = 60.0 
gehaeuse_h = 110.0 

# Turm Daten & Hex-System (Modifiziert für Flachdruck)
blatt_radius = 66.0       
dicke = 2.4               
versatz = 12.0            
kappen_dicke = 8.0        # Leicht erhöht auf 8mm für stabilen Hex-Halt
hex_radius = 10.0         # REDUZIERT & GEDREHT für perfekten Freiraum!
hex_h = kappen_dicke

einschmelzmutter_d = 4.2 
einschmelzmutter_t = 5.0  
# ==========================================

def make_hex_prism(radius, height):
    points = []
    for j in range(7):
        # +30 Grad Drehung, damit die FLACHE Seite des Sechskants zu den Flügeln zeigt!
        angle = math.radians(60 * j + 30) 
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    polygon = Part.makePolygon(points)
    face = Part.Face(Part.Wire(polygon))
    return face.extrude(App.Vector(0, 0, height))

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DER MASCHINEN-FUSS (Mit gerundetem Heck-Einschub!)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# 1. Der Lagersitz ganz oben
lager_sitz = Part.makeCylinder((lager_aussen_d + 0.2) / 2.0, lager_dicke)
lager_sitz.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke))
gehaeuse = gehaeuse.cut(lager_sitz)

# 2. Die dicke Schulter, die das Lager stützt
schulter_durchlass = Part.makeCylinder(14.0, 10.0)
schulter_durchlass.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke - 10.0))
gehaeuse = gehaeuse.cut(schulter_durchlass)

# --- DIE 3 EINSCHUB-ETAGEN (Jetzt mit perfekt gerundetem Rücken!) ---
# Etage A: Der Keller für den unteren Rotor
k_cyl = Part.makeCylinder(40.0, 30.0)
k_box = Part.makeBox(80.0, 80.0, 30.0).translate(App.Vector(-40.0, -80.0, 0))
gehaeuse = gehaeuse.cut(k_cyl).cut(k_box)

# Etage B: Die Schlitten-Führungsschienen (Gerundetes Ende)
s_cyl = Part.makeCylinder(47.5, 5.2).translate(App.Vector(0,0,30.0))
s_box = Part.makeBox(95.0, 80.0, 5.2).translate(App.Vector(-47.5, -80.0, 30.0))
gehaeuse = gehaeuse.cut(s_cyl).cut(s_box)

# Etage C: Der Generator-Raum für Stator & oberen Rotor
g_cyl = Part.makeCylinder(46.0, 49.8).translate(App.Vector(0, 0, 35.2))
g_box = Part.makeBox(92.0, 80.0, 49.8).translate(App.Vector(-46.0, -80.0, 35.2))
gehaeuse = gehaeuse.cut(g_cyl).cut(g_box)

# --- Baumhalterung ---
baum_rohr = Part.makeCylinder(20.0, 30.0)
baum_rohr.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
baum_rohr.translate(App.Vector(fuss_radius - 5.0, 0, 50.0))

baum_platte = Part.makeBox(10.0, 60.0, 60.0)
baum_platte.translate(App.Vector(fuss_radius + 20.0, -30.0, 20.0))

for y in [-20, 20]:
    for z in [30, 70]:
        loch = Part.makeCylinder(3.0, 10.0)
        loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
        loch.translate(App.Vector(fuss_radius + 20.0, y, z))
        baum_platte = baum_platte.cut(loch)

gehaeuse = gehaeuse.fuse(baum_rohr).fuse(baum_platte).removeSplitter()
show_obj(gehaeuse, "Basis_Gehaeuse")


# ==========================================
# BAUTEIL 2: DER SCHLITTEN (Mit rundem Heck!)
# ==========================================
schlitten_radius = 47.0 # Leicht unter 47.5 für minimales Spiel beim Einschieben
schlitten_back = Part.makeCylinder(schlitten_radius, 5.0)
schlitten_front = Part.makeBox(schlitten_radius * 2, 70.0, 5.0)
schlitten_front.translate(App.Vector(-schlitten_radius, -70.0, 0))

schlitten = schlitten_back.fuse(schlitten_front)

# Griff-Lasche vorne zum leichten Herausziehen
griff = Part.makeBox(30.0, 10.0, 5.0).translate(App.Vector(-15.0, -80.0, 0))
schlitten = schlitten.fuse(griff)

# Zentrales Durchlass-Loch für die Achse
schlitten = schlitten.cut(Part.makeCylinder(20.0, 5.0))

# 4 Befestigungslöcher für den Stator (Exakt auf Radius 41.5mm)
for i in range(4):
    angle = math.radians(i * 90 + 45)
    x = 41.5 * math.cos(angle)
    y = 41.5 * math.sin(angle)
    loch = Part.makeCylinder(1.7, 5.0).translate(App.Vector(x, y, 0))
    schlitten = schlitten.cut(loch)

schlitten = schlitten.removeSplitter()
schlitten.translate(App.Vector(0, -fuss_radius * 2.0, 0)) # Layout Position
show_obj(schlitten, "Schiebe_Schlitten")


# ==========================================
# BAUTEIL 3: FLACHE START-SCHEIBE (Easy Print)
# ==========================================
kappen_radius = blatt_radius - versatz + blatt_radius + 5.0 
scheibe = Part.makeCylinder(kappen_radius, kappen_dicke)

# Hexagon-Loch für den Adapter (+0.2mm Toleranz für leichten Steck-Sitz)
hex_cut = make_hex_prism(hex_radius + 0.2, kappen_dicke)
scheibe = scheibe.cut(hex_cut)

# S-Schlitze für die Flügel
cx = blatt_radius - versatz
po_s = App.Vector(-versatz, 0, 0)
po_m = App.Vector(cx, blatt_radius, 0)
po_e = App.Vector(cx + blatt_radius, 0, 0)
pi_s = App.Vector(-versatz + dicke + toleranz, 0, 0)
pi_m = App.Vector(cx, blatt_radius - dicke - toleranz, 0)
pi_e = App.Vector(cx + blatt_radius - dicke - toleranz, 0, 0)

blade_wire = Part.Wire([
    Part.Arc(po_s, po_m, po_e).toShape(), 
    Part.makeLine(po_e, pi_e), 
    Part.Arc(pi_e, pi_m, pi_s).toShape(), 
    Part.makeLine(pi_s, po_s)
])

# Rille ist 5mm tief, damit 3mm stabil als Boden bleiben
blade_cut = Part.Face(blade_wire).extrude(App.Vector(0,0,5.0))
blade_cut.translate(App.Vector(0,0, kappen_dicke - 5.0))

scheibe = scheibe.cut(blade_cut)
blade_cut2 = blade_cut.copy()
blade_cut2.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
scheibe = scheibe.cut(blade_cut2)

scheibe = scheibe.removeSplitter()
scheibe.translate(App.Vector(0, fuss_radius * 2.8, 0)) 
show_obj(scheibe, "Start_Scheibe_FLACH")


# ==========================================
# BAUTEIL 4: MODULARER VERBINDER-ADAPTER (Hex-Plug)
# ==========================================
# 1. Hex-Teil in der Mitte (Drehung um 30 Grad ist jetzt direkt in make_hex_prism!)
plug = make_hex_prism(hex_radius, hex_h)

# 2. Lagerschaft (unten, in das Kegelrollenlager passend)
lager_schaft = Part.makeCylinder((lager_innen_d - 0.2) / 2.0, lager_dicke + 2.0)
lager_schaft.translate(App.Vector(0,0, -lager_dicke - 2.0))
plug = plug.fuse(lager_schaft)

# 3. Kragen (oben) für Madenschrauben (17.5mm Durchmesser für genügend Abstand zu Flügeln)
kragen_h = 15.0
kragen_d = 17.5 
kragen = Part.makeCylinder(kragen_d / 2.0, kragen_h)
kragen.translate(App.Vector(0,0, hex_h))
plug = plug.fuse(kragen)

# 4. 10x10 Achse durch alles
achse_cut = make_square_prism(achse_kantenlaenge + toleranz, hex_h + lager_dicke + kragen_h + 5.0)
achse_cut.translate(App.Vector(0,0, -lager_dicke - 3.0))
plug = plug.cut(achse_cut)

# 5. NEU: 4x M3 Gewindeeinsatz und Löcher im Kragen für absolut ausbalancierten Grip (0 Unwucht!)
einschmelzmutter_t_kragen = 4.0 
for i in range(4):
    angle = i * 90
    
    # Durchgangsloch
    m3_loch = Part.makeCylinder(3.4 / 2.0, 30.0)
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_loch.translate(App.Vector(-15, 0, hex_h + (kragen_h / 2.0)))
    m3_loch.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    # Tasche für die Heat-Set Mutter
    m3_insert = Part.makeCylinder(einschmelzmutter_d / 2.0, einschmelzmutter_t_kragen)
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
    m3_insert.translate(App.Vector((kragen_d / 2.0) - einschmelzmutter_t_kragen, 0, hex_h + (kragen_h / 2.0)))
    m3_insert.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
    
    plug = plug.cut(m3_loch).cut(m3_insert)

plug = plug.removeSplitter()
plug.translate(App.Vector(fuss_radius * 2.5, 0, 0)) 
show_obj(plug, "Adapter_Hex_Verbinder")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")