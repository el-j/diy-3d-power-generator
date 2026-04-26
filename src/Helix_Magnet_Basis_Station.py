import FreeCAD as App
import Part
import math

doc = App.newDocument("Savonius_Base_Station")

# ==========================================
# ⚙️ PARAMETER FÜR DIE BASIS-STATION
# ==========================================
achse_kantenlaenge = 10.0 
toleranz = 0.5 

# Maße für das Kegelrollenlager (32005) aus deinen Fotos!
lager_innen_d = 25.0      
lager_aussen_d = 47.0     
lager_dicke = 15.0        

# Schlitten & Generator (Passend zum neuen 90mm Generator)
schlitten_breite = 95.0 
schlitten_tiefe = 90.0
fuss_radius = 60.0 
gehaeuse_h = 110.0 # Massiv aufgestockt für den großen Generator!

# Turm Daten für die S-Kappe
blatt_radius = 66.0       
dicke = 2.4               
versatz = 12.0            
kappen_dicke = 6.0        
rillen_tiefe = 3.0        
# ==========================================

def make_square_prism(size, height):
    box = Part.makeBox(size, size, height)
    box.translate(App.Vector(-size / 2.0, -size / 2.0, 0))
    return box

def show_obj(shape, name):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj

# ==========================================
# BAUTEIL 1: DER MASCHINEN-FUSS (C-Profil für Front-Einschub)
# ==========================================
gehaeuse = Part.makeCylinder(fuss_radius, gehaeuse_h)

# 1. Der Lagersitz ganz oben (Z=95 bis 110)
lager_sitz = Part.makeCylinder((lager_aussen_d + 0.2) / 2.0, lager_dicke)
lager_sitz.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke))
gehaeuse = gehaeuse.cut(lager_sitz)

# 2. Die dicke Schulter, die das Lager stützt (Z=85 bis 95)
schulter_durchlass = Part.makeCylinder(14.0, 10.0)
schulter_durchlass.translate(App.Vector(0, 0, gehaeuse_h - lager_dicke - 10.0))
gehaeuse = gehaeuse.cut(schulter_durchlass)

# --- DIE 3 EINSCHUB-ETAGEN (Von vorne Y=-80 bis in die Mitte Y=20) ---
# Etage A: Der Keller für den unteren Rotor (Z=0 bis 30)
k_cyl = Part.makeCylinder(40.0, 30.0)
k_box = Part.makeBox(80.0, 100.0, 30.0).translate(App.Vector(-40.0, -80.0, 0))
gehaeuse = gehaeuse.cut(k_cyl).cut(k_box)

# Etage B: Die Schlitten-Führungsschienen (Z=30 bis 35.2)
s_box = Part.makeBox(96.0, 100.0, 5.2).translate(App.Vector(-48.0, -80.0, 30.0))
gehaeuse = gehaeuse.cut(s_box)

# Etage C: Der Generator-Raum für Stator & oberen Rotor (Z=35.2 bis 85)
g_cyl = Part.makeCylinder(46.0, 49.8).translate(App.Vector(0, 0, 35.2))
g_box = Part.makeBox(92.0, 100.0, 49.8).translate(App.Vector(-46.0, -80.0, 35.2))
gehaeuse = gehaeuse.cut(g_cyl).cut(g_box)

# --- Baumhalterung (Seitlich rechts am Gehäuse) ---
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
# BAUTEIL 2: DER SCHLITTEN (Repariert & Verstärkt)
# ==========================================
schlitten = Part.makeBox(schlitten_breite, schlitten_tiefe, 5.0)
# Sitzt exakt im Slot: X von -47.5 bis 47.5, Y von -70 bis 20 (Mitte ist 0,0)
schlitten.translate(App.Vector(-schlitten_breite / 2.0, 20.0 - schlitten_tiefe, 0))

# Griff-Lasche vorne zum leichten Herausziehen
griff = Part.makeBox(30.0, 10.0, 5.0).translate(App.Vector(-15.0, 20.0 - schlitten_tiefe - 10.0, 0))
schlitten = schlitten.fuse(griff)

# Zentrales Durchlass-Loch für die Achse (Sichere 40mm Durchmesser)
schlitten = schlitten.cut(Part.makeCylinder(20.0, 5.0))

# 4 Befestigungslöcher für den Stator (Exakt auf Radius 41.5mm)
for i in range(4):
    angle = math.radians(i * 90 + 45)
    x = 41.5 * math.cos(angle)
    y = 41.5 * math.sin(angle)
    loch = Part.makeCylinder(1.7, 5.0).translate(App.Vector(x, y, 0))
    schlitten = schlitten.cut(loch)

schlitten = schlitten.removeSplitter()
schlitten.translate(App.Vector(0, -fuss_radius * 2.0, 0)) # Nur fürs Layout verschoben
show_obj(schlitten, "Schiebe_Schlitten")


# ==========================================
# BAUTEIL 3: TURM-START-KAPPE (Jetzt mit integriertem Lager-Adapter!)
# ==========================================
kappen_radius = blatt_radius - versatz + blatt_radius + 5.0 
start_kappe = Part.makeCylinder(kappen_radius, kappen_dicke)

# Der Schaft, der von Oben ins Kegelrollenlager rutscht!
lager_schaft = Part.makeCylinder((lager_innen_d - 0.2) / 2.0, lager_dicke + 2.0)
lager_schaft.translate(App.Vector(0,0, -lager_dicke - 2.0))
start_kappe = start_kappe.fuse(lager_schaft)

# Die Achse geht komplett durch
achse_cut = make_square_prism(achse_kantenlaenge + toleranz, kappen_dicke + lager_dicke + 5.0)
achse_cut.translate(App.Vector(0,0, -lager_dicke - 3.0))
start_kappe = start_kappe.cut(achse_cut)

# S-Schlitze für die Flügel einschneiden
cx = blatt_radius - versatz
po_s = App.Vector(-versatz, 0, 0); po_m = App.Vector(cx, blatt_radius, 0); po_e = App.Vector(cx + blatt_radius, 0, 0)
pi_s = App.Vector(-versatz + dicke + toleranz, 0, 0); pi_m = App.Vector(cx, blatt_radius - dicke - toleranz, 0); pi_e = App.Vector(cx + blatt_radius - dicke - toleranz, 0, 0)

blade_wire = Part.Wire([Part.Arc(po_s, po_m, po_e).toShape(), Part.makeLine(po_e, pi_e), Part.Arc(pi_e, pi_m, pi_s).toShape(), Part.makeLine(pi_s, po_s)])

rille_oben_1 = Part.Face(blade_wire).extrude(App.Vector(0,0,rillen_tiefe))
rille_oben_1.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))

blade_wire_180 = blade_wire.copy()
blade_wire_180.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
rille_oben_2 = Part.Face(blade_wire_180).extrude(App.Vector(0,0,rillen_tiefe))
rille_oben_2.translate(App.Vector(0,0, kappen_dicke - rillen_tiefe))

start_kappe = start_kappe.cut(rille_oben_1).cut(rille_oben_2)
start_kappe = start_kappe.removeSplitter()

start_kappe.translate(App.Vector(0, fuss_radius * 2.5, 0)) # Layout Position
show_obj(start_kappe, "Turm_Start_Kappe")

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")

print("Maschinenbasis mit C-Einschub und integriertem Lager-Schaft generiert!")