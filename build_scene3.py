import bpy
import math
import os

# Clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 26 * 30  # 780 frames (26 seconds)

# 1080x1920 9:16 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.Scene, 'eevee_next') else 'BLENDER_EEVEE'

os.makedirs("output/scene3_frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/scene3_frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# Materials
def create_pbr_material(name, base_color, metallic=0.0, roughness=0.1, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = 1.48
    return mat

def create_green_marble_material():
    mat = bpy.data.materials.new(name="Green_Veined_Marble")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    color_ramp = nodes.new("ShaderNodeValToRGB")

    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 5.0
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[0].color = (0.75, 0.82, 0.77, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.75
    color_ramp.color_ramp.elements[1].color = (0.18, 0.32, 0.25, 1.0)

    links.new(noise.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.18
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

marble_mat = create_green_marble_material()
gold_mat = create_pbr_material("Reflective_Gold", (1.0, 0.76, 0.28, 1.0), metallic=0.98, roughness=0.1)
glass_mat = create_pbr_material("Clear_Glass", (0.95, 0.98, 1.0, 1.0), metallic=0.0, roughness=0.03, transmission=0.96)

# -------------------------------------------------------------
# Geometry: Descending Marble Stairs and Three Glass Tubes
# -------------------------------------------------------------
# Create 4 marble steps descending forward
for step_idx in range(4):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, -0.6 * step_idx, 1.2 - 0.5 * step_idx)
    )
    st = bpy.context.active_object
    st.scale = (2.4, 0.6, 0.45)
    st.data.materials.append(marble_mat)

# Three Curved Glass Tubes at bottom (left, center, right)
x_offsets = [-0.75, 0.0, 0.75]
for idx, x_off in enumerate(x_offsets):
    c_data = bpy.data.curves.new(f'TubeCurve_{idx}', type='CURVE')
    c_data.dimensions = '3D'
    poly = c_data.splines.new('BEZIER')
    poly.bezier_points.add(1)

    p0 = poly.bezier_points[0]
    p0.co = (x_off, -1.8, -0.3)
    p0.handle_left = (x_off, -1.5, -0.1)
    p0.handle_right = (x_off, -2.1, -0.5)

    p1 = poly.bezier_points[1]
    p1.co = (x_off, -2.5, -1.4)
    p1.handle_left = (x_off, -2.3, -1.0)
    p1.handle_right = (x_off, -2.7, -1.8)

    c_data.bevel_depth = 0.22
    t_obj = bpy.data.objects.new(f'TubeObj_{idx}', c_data)
    bpy.context.collection.objects.link(t_obj)
    t_obj.data.materials.append(glass_mat)

# -------------------------------------------------------------
# Three Gold Capsule Actors
# -------------------------------------------------------------
capsules = []
for idx, x_off in enumerate(x_offsets):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.55, location=(x_off, 0.2, 1.8))
    cap = bpy.context.active_object
    cap.name = f"GoldCap_{idx}"
    cap.data.materials.append(gold_mat)
    sub = cap.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    capsules.append(cap)

# Stages for Scene 3 (26 seconds total):
# 0%   (0s - 2s / f1   - f75) : Rigid capsules tumble & bounce erratically, scattering away
# 25%  (3s - 6s / f90  - f180): Slide down, slight flex, partially lodge at entrance lip
# 50%  (7s - 11s / f210 - f330): Deform & slide partially through tubes, jamming near bottom
# 75%  (12s - 18s / f360 - f540): Gelatin snaking smoothly through all 3 tubes and shooting out
# 100% (19s - 25s / f570 - f780): Liquid flow down steps, extruding & dripping out bottom

def animate_capsules_0(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        for i, cap in enumerate(capsules):
            x_off = x_offsets[i]
            if t < 0.5:
                cap.location = (x_off, 0.2 - 1.2 * (t / 0.5), 1.8 - 1.2 * (t / 0.5))
                cap.rotation_euler = (t * 4, t * 2, 0)
                cap.scale = (1, 1, 1)
            else: # erratic bounce away from entrance
                st = (t - 0.5) / 0.5
                cap.location = (x_off + (i - 1) * 1.5 * st, -1.0 - 0.8 * st, 0.6 + math.sin(st * math.pi) * 0.8 - 1.5 * st)
                cap.rotation_euler = (4 + st * 8, 2 + st * 6, st * 5)
                cap.scale = (1, 1, 1)
            cap.keyframe_insert("location", frame=f)
            cap.keyframe_insert("rotation_euler", frame=f)
            cap.keyframe_insert("scale", frame=f)

def animate_capsules_25(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        for i, cap in enumerate(capsules):
            x_off = x_offsets[i]
            if t < 0.6:
                st = t / 0.6
                cap.location = (x_off, 0.2 - 2.0 * st, 1.8 - 2.0 * st)
                cap.rotation_euler = (st * 0.6, 0, 0)
                cap.scale = (1.0, 1.0, 1.0)
            else: # lodge at entrance lip
                w = math.sin((t - 0.6) * 30) * 0.015
                cap.location = (x_off, -1.8 + w, -0.2)
                cap.rotation_euler = (0.6, 0, 0)
                cap.scale = (1.1, 1.1, 0.85)
            cap.keyframe_insert("location", frame=f)
            cap.keyframe_insert("rotation_euler", frame=f)
            cap.keyframe_insert("scale", frame=f)

def animate_capsules_50(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        for i, cap in enumerate(capsules):
            x_off = x_offsets[i]
            if t < 0.4:
                st = t / 0.4
                cap.location = (x_off, 0.2 - 2.0 * st, 1.8 - 2.0 * st)
                cap.scale = (1.0, 1.0, 1.0)
            elif t < 0.8:
                st = (t - 0.4) / 0.4
                cap.location = (x_off, -1.8 - 0.4 * st, -0.2 - 0.8 * st)
                cap.scale = (0.85, 0.85, 1.25) # elongated flex
            else: # jammed near bottom curve
                w = math.sin((t - 0.8) * 20) * 0.02
                cap.location = (x_off, -2.2, -1.0 + w)
                cap.scale = (1.1, 1.1, 0.85)
            cap.keyframe_insert("location", frame=f)
            cap.keyframe_insert("rotation_euler", frame=f)
            cap.keyframe_insert("scale", frame=f)

def animate_capsules_75(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        for i, cap in enumerate(capsules):
            x_off = x_offsets[i]
            if t < 0.4:
                st = t / 0.4
                cap.location = (x_off, 0.2 - 2.0 * st, 1.8 - 2.0 * st)
                cap.scale = (0.9, 0.9, 1.2)
            elif t < 0.7: # snaking smoothly through tubes
                st = (t - 0.4) / 0.3
                cap.location = (x_off, -1.8 - 0.7 * st, -0.2 - 1.2 * st)
                cap.scale = (0.65, 0.65, 1.7)
            else: # shoot out the ends
                st = (t - 0.7) / 0.3
                cap.location = (x_off, -2.5 - 1.2 * st, -1.4 - 1.0 * st)
                cap.scale = (1.0, 1.0, 1.0)
            cap.keyframe_insert("location", frame=f)
            cap.keyframe_insert("rotation_euler", frame=f)
            cap.keyframe_insert("scale", frame=f)

def animate_capsules_100(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        for i, cap in enumerate(capsules):
            x_off = x_offsets[i]
            if t < 0.4:
                st = t / 0.4
                cap.location = (x_off, 0.2 - 2.0 * st, 1.8 - 2.0 * st)
                cap.scale = (0.7, 0.7, 1.6)
            elif t < 0.7: # extruding viscous liquid stream
                st = (t - 0.4) / 0.3
                cap.location = (x_off, -1.8 - 0.7 * st, -0.2 - 1.2 * st)
                cap.scale = (0.5, 0.5, 2.2)
            else: # dripping out and pooling on floor
                st = (t - 0.7) / 0.3
                cap.location = (x_off, -2.5 - 0.4 * st, -1.4 - 1.2 * st)
                cap.scale = (1.4 + 1.2 * st, 1.4 + 1.2 * st, 0.3 - 0.25 * st)
            cap.keyframe_insert("location", frame=f)
            cap.keyframe_insert("rotation_euler", frame=f)
            cap.keyframe_insert("scale", frame=f)

animate_capsules_0(1, 75)
animate_capsules_25(90, 180)
animate_capsules_50(210, 330)
animate_capsules_75(360, 540)
animate_capsules_100(570, 780)

# Camera & Lighting
bpy.ops.object.camera_add(location=(0, -7.5, 1.2), rotation=(math.radians(82), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 50

bpy.ops.object.light_add(type='AREA', location=(3.5, -4.5, 5.0), rotation=(math.radians(45), 0, math.radians(30)))
key = bpy.context.active_object
key.data.energy = 950
key.data.size = 2.8

bpy.ops.object.light_add(type='AREA', location=(-3.5, -4.0, 3.5), rotation=(math.radians(45), 0, math.radians(-30)))
fill = bpy.context.active_object
fill.data.energy = 480
fill.data.size = 3.2

bpy.ops.object.light_add(type='POINT', location=(0, 2.8, 3.5))
rim = bpy.context.active_object
rim.data.energy = 650
rim.data.color = (1.0, 0.92, 0.8)

world = bpy.data.worlds.new("StudioWorld3")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.74, 0.78, 0.84, 1.0)

print("[*] Scene 3 configured.")
