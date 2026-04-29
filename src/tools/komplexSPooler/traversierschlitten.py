import FreeCAD as App
import Part

doc = App.newDocument("Wickelmaschine_Schlitten_Modular")

def make_centered_box(l, w, h, cx, cy, cz):
    box = Part.makeBox(l, w, h)
    box.translate(App.Vector(cx - l/2.0, cy - w/2.0, cz - h/2.0))
    return box

# ==========================================
# 1. ZENTRAL-SCHLITTEN (Die Basis auf der T-Schiene)
# ==========================================
base = make_centered_box(30, 20, 22, 0, 0, 11.0)
cut_stem = make_centered_box(6.6, 22.0, 5.0, 0, 0, 2.5)   
cut_top = make_centered_box(12.6, 22.0, 6.0, 0, 0, 8.0) 
square_hole = make_centered_box(7.4, 22.0, 7.4, 0, 0, 16.0)

m3_clearance_l = Part.makeCylinder(1.7, 10.0).translate(App.Vector(-7, 0, 16))
m3_clearance_r = Part.makeCylinder(1.7, 10.0).translate(App.Vector(7, 0, 16))

hook = Part.makeCylinder(2.5, 10).translate(App.Vector(0, 0, 0))
hook.rotate(App.Vector(0,0,0), App.Vector(1,0,0), -90)
hook.translate(App.Vector(0, -10, 16))

sled = base.cut(cut_stem).cut(cut_top).cut(square_hole).cut(m3_clearance_l).cut(m3_clearance_r).fuse(hook).removeSplitter()
sled.translate(App.Vector(0, 30, 0)) 

obj_sled = doc.addObject("Part::Feature", "Schlitten_Basis")
obj_sled.Shape = sled

# ==========================================
# 2. LINKER ARM (Abtaster - Angepasst auf neue Achshöhe 75mm!)
# ==========================================
peg_l = make_centered_box(14, 7, 7, -7, 0, 3.5) 
shoulder_l = make_centered_box(8, 10, 10, -18, 0, 5.0)

# Arm wurde exakt 25mm verlängert! (alt: 26, neu: 51)
vertical_l = make_centered_box(10, 10, 51, -18, 0, 35.5)
pin = Part.makeSphere(4.0).translate(App.Vector(-18, 0, 61.0)) 

lock_hole_l = Part.makeCylinder(1.4, 10).translate(App.Vector(-7, 0, 0))

arm_l = peg_l.fuse(shoulder_l).fuse(vertical_l).fuse(pin).cut(lock_hole_l).removeSplitter()
arm_l.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
arm_l.translate(App.Vector(-30, 0, 5)) 

obj_arm_l = doc.addObject("Part::Feature", "Arm_Links_Abtaster")
obj_arm_l.Shape = arm_l

# ==========================================
# 3. RECHTER ARM (Drahtführung - Angepasst auf neue Achshöhe 75mm!)
# ==========================================
peg_r = make_centered_box(14, 7, 7, 7, 0, 3.5) 
shoulder_r = make_centered_box(71, 10, 10, 49.5, 0, 5.0) 

# Arm wurde exakt 25mm verlängert! (alt: 26, neu: 51)
vertical_r = make_centered_box(10, 10, 51, 85, 0, 35.5) 

wire_hole = Part.makeCylinder(1.0, 20)
wire_hole.rotate(App.Vector(0,0,0), App.Vector(0,1,0), 90)
wire_hole.translate(App.Vector(75, 0, 59.0)) # Loch zielt jetzt genau auf 75mm absolute Höhe!

lock_hole_r = Part.makeCylinder(1.4, 10).translate(App.Vector(7, 0, 0))

arm_r = peg_r.fuse(shoulder_r).fuse(vertical_r).cut(wire_hole).cut(lock_hole_r).removeSplitter()
arm_r.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
arm_r.translate(App.Vector(0, -30, 5))

obj_arm_r = doc.addObject("Part::Feature", "Arm_Rechts_Drahtfuehrung")
obj_arm_r.Shape = arm_r

doc.recompute()
if App.GuiUp:
    App.Gui.activeDocument().activeView().viewAxometric()
    App.Gui.SendMsgToActiveView("ViewFit")