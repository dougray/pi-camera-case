"""Printable parts for the Raspberry Pi A+ camera case (camera stands on the Pi).

Combines two CC BY-SA Thingiverse designs (credits in README.md):
  - Raspberry Pi A+ Case by adafruit (thing:546427): case base and lid
  - Raspberry Pi Camera Stand by atleberg (thing:274111): camera box, cover and the hinge idea

Parts written to stl/ (all in print orientation, no supports):
  lid.stl            adafruit lid with two extra M3 holes for the hinge mount
  hinge-mount.stl    NEW: plate with two hinge ears, nut pockets underneath; bolts to the lid
  camera-box.stl     atleberg camera box, unmodified (needs the real camera board to confirm the posts)
  camera-cover.stl   atleberg back cover, unmodified
  pi-case.stl        adafruit case base, with the USB opening widened for a WiFi dongle

Hardware: 1x M3 x 25 screw + nut (hinge pin), 2x M3 x 5 screws + 2x M3 nuts (hinge mount).

Run:  /Applications/Blender.app/Contents/MacOS/Blender --background --python build_case.py
"""
import math
import os
import shutil

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(HERE, "originals")
STL = os.path.join(HERE, "stl")
PREV = os.path.join(HERE, "preview")
os.makedirs(STL, exist_ok=True)
os.makedirs(PREV, exist_ok=True)

# ---- geometry (mm). Assembled frame: case base on z = 0, +x = ports wall, lens looks toward -x ----
CASE_H = 19.0
LID_PLATE = 1.5                      # adafruit lists 1.5 mm walls
LID_TOP = CASE_H + LID_PLATE         # outer lid surface when assembled
HINGE_X, HINGE_Y = 17.0, -6.0        # hinge position on the lid (keeps the camera ribbon clear)
MOUNT_W, MOUNT_D, MOUNT_T = 28.0, 22.0, 3.0
SCREW_DX = 10.0                      # mount screws sit this far from the hinge centre along x
SCREW_D, NUT_AF, NUT_T = 3.4, 5.7, 2.4
EAR_T, TAB_W = 3.0, 9.24
EAR_GAP = TAB_W + 0.6
EAR_R = 5.2                         # must stay under 5.76: the camera box shoulders start that far from the pin
PIN_H = 9.0                          # pin height above the mount plate
PIN_D = 3.2                          # tab hole measured at 3.1 mm
BOX_PIN = Vector((0.0, -46.0, 3.5))  # pin centre in the camera box frame, measured from the mesh
LEAN_BACK = 15.0                     # default tilt for the preview
# USB opening in the case's +y wall, widened for a WiFi dongle (Cable Matters, ~15.5 mm body, external antenna).
# adafruit's opening measures 17.5 x 10.1 mm, centred at x = -2.45, z 6.2..16.3.
USB_CX, USB_W, USB_Z0, USB_Z1 = -2.45, 22.0, 5.2, 17.0
CASE_YMAX, CASE_WALL = 35.5, 1.89


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def load(fn):
    before = set(bpy.data.objects)
    bpy.ops.wm.stl_import(filepath=os.path.join(ORIG, fn))
    return [o for o in bpy.data.objects if o not in before][0]


def apply(ob, m):
    ob.data.transform(m)
    ob.data.update()


def box(x0, y0, z0, x1, y1, z1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    ob = bpy.context.active_object
    ob.scale = (x1 - x0, y1 - y0, z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    return ob


def cyl_z(x, y, z0, z1, d, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=d / 2, depth=z1 - z0,
                                        location=(x, y, (z0 + z1) / 2))
    return bpy.context.active_object


def cyl_y(x, z, y0, y1, d):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=d / 2, depth=y1 - y0,
                                        location=(x, (y0 + y1) / 2, z), rotation=(math.pi / 2, 0, 0))
    return bpy.context.active_object


def boolean(target, other, op):
    mod = target.modifiers.new("b", "BOOLEAN")
    mod.operation, mod.object, mod.solver = op, other, "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(other, do_unlink=True)


def report(ob, label):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bad = sum(1 for e in bm.edges if not e.is_manifold)
    xs, ys, zs = ([getattr(v.co, a) for v in bm.verts] for a in "xyz")
    print(f"CHECK {label}: {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} x {max(zs)-min(zs):.1f} mm, "
          f"volume {bm.calc_volume()/1000:.1f} cm3, non-manifold edges {bad}")
    bm.free()
    return bad


def export(ob, name):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.wm.stl_export(filepath=os.path.join(STL, name), export_selected_objects=True)


# ---------------------------------------------------------------- parts
def make_lid():
    """adafruit lid in its own (outer-face-down) frame, plus two M3 holes for the hinge mount.

    Assembled, the lid is flipped 180 degrees about x, so an assembled y maps to lid y = -y."""
    lid = load("piaplus-top.stl")
    for sx in (-1, 1):
        boolean(lid, cyl_z(HINGE_X + sx * SCREW_DX, -HINGE_Y, -1, 6, SCREW_D), "DIFFERENCE")
    lid.name = "lid"
    return lid


def make_mount():
    """Mount plate + ears in print orientation: plate bottom on the bed (z = 0), ears up."""
    plate = box(HINGE_X - MOUNT_W / 2, HINGE_Y - MOUNT_D / 2, 0, HINGE_X + MOUNT_W / 2, HINGE_Y + MOUNT_D / 2, MOUNT_T)
    pin_z = MOUNT_T + PIN_H
    for side in (-1, 1):
        yc = HINGE_Y + side * (EAR_GAP / 2 + EAR_T / 2)
        blk = box(HINGE_X - EAR_R, yc - EAR_T / 2, MOUNT_T - 0.4, HINGE_X + EAR_R, yc + EAR_T / 2, pin_z)
        boolean(blk, cyl_y(HINGE_X, pin_z, yc - EAR_T / 2, yc + EAR_T / 2, EAR_R * 2), "UNION")
        boolean(plate, blk, "UNION")
    boolean(plate, cyl_y(HINGE_X, pin_z, HINGE_Y - 20, HINGE_Y + 20, PIN_D), "DIFFERENCE")
    for sx in (-1, 1):
        x = HINGE_X + sx * SCREW_DX
        boolean(plate, cyl_z(x, HINGE_Y, -1, MOUNT_T + 1, SCREW_D), "DIFFERENCE")
        boolean(plate, cyl_z(x, HINGE_Y, -0.01, NUT_T, NUT_AF / math.cos(math.radians(30)), verts=6), "DIFFERENCE")
    plate.name = "hinge-mount"
    return plate


def stand_matrix(lean_deg):
    """Camera-box frame -> assembled frame: arm along +Z, lens toward -X, leaning back by lean_deg."""
    pin_z = LID_TOP + MOUNT_T + PIN_H
    to_stand = Matrix(((0, 0, 1, -BOX_PIN.z), (1, 0, 0, 0), (0, 1, 0, -BOX_PIN.y), (0, 0, 0, 1)))
    return Matrix.Translation((HINGE_X, HINGE_Y, pin_z)) @ Matrix.Rotation(math.radians(lean_deg), 4, "Y") @ to_stand


def world_bvh(ob):
    """BVH in WORLD space. (BVHTree.FromObject uses local coordinates and ignores matrix_world.)"""
    mw = ob.matrix_world
    verts = [mw @ v.co for v in ob.data.vertices]
    polys = [tuple(p.vertices) for p in ob.data.polygons]
    return BVHTree.FromPolygons(verts, polys)


def sweep(box_ob, statics, lo=-90, hi=110, step=5):
    """Find the lean angles where the camera box is free of everything else."""
    trees = [world_bvh(o) for o in statics]
    free = []
    for a in range(lo, hi + 1, step):
        box_ob.matrix_world = stand_matrix(a)
        bt = world_bvh(box_ob)
        hit = any(bt.overlap(t) for t in trees)
        free.append((a, not hit))
    return free


def ranges(free):
    out, start, prev = [], None, None
    for a, ok in free:
        if ok and start is None:
            start = a
        if not ok and start is not None:
            out.append((start, prev))
            start = None
        prev = a
    if start is not None:
        out.append((start, prev))
    return out


def main():
    clear()
    case = load("piaplus-case.stl")
    boolean(case, box(USB_CX - USB_W / 2, CASE_YMAX - CASE_WALL - 0.05, USB_Z0,
                      USB_CX + USB_W / 2, CASE_YMAX + 1, USB_Z1), "DIFFERENCE")
    case.name = "case"
    lid = make_lid()
    mount = make_mount()
    cam = load("camera_front_box_v003.stl")
    cover = load("camera_back_cover_v002.stl")

    bad = 0
    for ob, label in ((lid, "lid"), (mount, "hinge mount"), (case, "case"), (cam, "camera box"), (cover, "cover")):
        bad += report(ob, label)
    export(lid, "lid.stl")
    export(mount, "hinge-mount.stl")
    export(case, "pi-case.stl")
    export(cam, "camera-box.stl")
    export(cover, "camera-cover.stl")
    print("CHECK total non-manifold edges:", bad)

    # ---- assemble (design frame) for the swing check and renders
    asm_lid = lid.copy()
    asm_lid.data = lid.data.copy()
    bpy.context.collection.objects.link(asm_lid)
    apply(asm_lid, Matrix.Translation((0, 0, LID_TOP)) @ Matrix.Rotation(math.pi, 4, "X"))
    asm_mount = mount.copy()
    asm_mount.data = mount.data.copy()
    bpy.context.collection.objects.link(asm_mount)
    apply(asm_mount, Matrix.Translation((0, 0, LID_TOP)))
    asm_cover = cover.copy()
    asm_cover.data = cover.data.copy()
    bpy.context.collection.objects.link(asm_cover)

    # hide the print-frame originals of lid/mount from the assembled scene
    for o in (lid, mount):
        bpy.data.objects.remove(o, do_unlink=True)

    apply(asm_cover, Matrix.Translation((0, 0, 10.0)))      # cover on the pocket's open side, box frame
    cam.matrix_world = stand_matrix(LEAN_BACK)
    asm_cover.matrix_world = stand_matrix(LEAN_BACK)

    # free-swing range of the camera box (cover moves with it, so test the box alone)
    free = sweep(cam, [case, asm_lid, asm_mount])
    for a in (15, 0, 45, -25, 70):
        cam.matrix_world = stand_matrix(a)
        bt = world_bvh(cam)
        hits = {nm: len(bt.overlap(world_bvh(o))) for nm, o in (("case", case), ("lid", asm_lid), ("mount", asm_mount))}
        print(f"DEBUG lean {a:>4}: overlapping triangle pairs {hits}")
    rng = ranges(free)
    print("SWING free lean-angle ranges (deg, + = leaning back, lens looks down):", rng)
    print("SWING lens look angle relative to horizontal = lean angle downward")

    colors = {case: (0.30, 0.55, 0.85, 1), asm_lid: (0.55, 0.75, 0.95, 1), asm_mount: (0.95, 0.60, 0.15, 1),
              cam: (0.35, 0.80, 0.50, 1), asm_cover: (0.95, 0.85, 0.30, 1)}
    for ob, c in colors.items():
        ob.color = c

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "OBJECT"
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    target = bpy.data.objects.new("t", None)
    target.location = (0, 0, 46)
    scene.collection.objects.link(target)
    shots = {"iso-front": (-1.0, -1.1, 0.6, LEAN_BACK), "side": (0, -1, 0.05, LEAN_BACK),
             "side-down": (0, -1, 0.05, 45), "side-up": (0, -1, 0.05, -25)}
    for name, (dx, dy, dz, lean) in shots.items():
        cam.matrix_world = stand_matrix(lean)
        asm_cover.matrix_world = stand_matrix(lean) @ Matrix.Translation((0, 0, 0))
        bpy.context.view_layer.update()
        c = bpy.data.cameras.new("c")
        c.type, c.ortho_scale = "ORTHO", 180
        co = bpy.data.objects.new("c", c)
        scene.collection.objects.link(co)
        co.location = Vector((dx, dy, dz)).normalized() * 400 + Vector((0, 0, 46))
        tr = co.constraints.new("TRACK_TO")
        tr.target, tr.track_axis, tr.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
        scene.camera = co
        scene.render.filepath = os.path.join(PREV, f"case-{name}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(co, do_unlink=True)


main()
