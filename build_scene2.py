import bpy
import math
import os

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 22 * 30  # 660 frames (22 seconds)

# 1080x1920 9:16 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.Scene, 'eevee_next') else 'BLENDER_EEVEE'

os.makedirs("output/scene2_frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/scene2_frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# Materials
def create_pbr_material(name, base_color, metallic=0.0, roughness=0.1):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
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

# -------------------------------------------------------------
# Geometry: Square Pedestal & Green Marble Snowman Figurine
# -------------------------------------------------------------
# Square pedestal base
bpy.ops.mesh.primitive_cube_add(size=2.4, location=(0, 0, -1.5))
pedestal = bpy.context.active_object
pedestal.scale = (1.0, 1.0, 0.5)
pedestal.data.materials.append(marble_mat)

# Gold rim trim on pedestal
bpy.ops.mesh.primitive_torus_add(major_radius=1.3, minor_radius=0.05, location=(0, 0, -0.9))
rim = bpy.context.active_object
rim.data.materials.append(gold_mat)

# Snowman Bottom sphere (base torso)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0, 0, 0.0))
sm_bottom = bpy.context.active_object
sm_bottom.data.materials.append(marble_mat)

# Snowman Middle sphere (chest)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, 1.1))
sm_mid = bpy.context.active_object
sm_mid.data.materials.append(marble_mat)

# Snowman Top sphere (head)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0, 0, 1.95))
sm_head = bpy.context.active_object
sm_head.data.materials.append(marble_mat)

# -------------------------------------------------------------
# Golden Torus (Ring) Actor
# -------------------------------------------------------------
bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.12, location=(0, 0, 3.4))
ring = bpy.context.active_object
ring.name = "Gold_Ring"
ring.data.materials.append(gold_mat)

# Stages for Scene 2 (22 seconds total):
# 0%   (0s - 2s / f1   - f60) : Rigid torus strikes head, bounces off shoulder, deflects off-screen
# 25%  (3s - 6s / f90  - f180): Slightly deforms upon impact, rests briefly atop head, slides off
# 50%  (7s - 9s / f210 - f270): Flexes elastically around neck/torso, hugs contour without sliding down
# 75%  (10s - 17s / f300 - f510): Stretches and drapes loosely over middle section like rubber band
# 100% (18s - 21s / f540 - f660): Behaves like molten liquid/fabric, melting over snowman and dripping

def animate_ring_0(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.4:
            ring.location = (0, 0, 3.4 - 1.0 * (t / 0.4))
            ring.rotation_euler = (0, 0, 0)
            ring.scale = (1, 1, 1)
        elif t < 0.7:
            st = (t - 0.4) / 0.3
            ring.location = (0.4 * st, 0, 2.4 - 0.6 * st)
            ring.rotation_euler = (st * 1.8, 0, st * 1.2)
            ring.scale = (1, 1, 1)
        else:
            st = (t - 0.7) / 0.3
            ring.location = (0.4 + 2.0 * st, 0, 1.8 + 0.5 * math.sin(st * math.pi) - 2.2 * st)
            ring.rotation_euler = (1.8 + st * 4.0, 0, 1.2 + st * 3.0)
            ring.scale = (1, 1, 1)
        ring.keyframe_insert("location", frame=f)
        ring.keyframe_insert("rotation_euler", frame=f)
        ring.keyframe_insert("scale", frame=f)

def animate_ring_25(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.35:
            ring.location = (0, 0, 3.4 - 1.1 * (t / 0.35))
            ring.rotation_euler = (0, 0, 0)
            ring.scale = (1, 1, 1)
        elif t < 0.7: # slight deformation, resting briefly on head
            st = (t - 0.35) / 0.35
            w = math.sin(st * math.pi * 3) * 0.03
            ring.location = (w, 0, 2.3)
            ring.rotation_euler = (0.1, 0, 0.1)
            ring.scale = (1.08, 1.08, 0.88)
        else: # slides off shoulder
            st = (t - 0.7) / 0.3
            ring.location = (-0.8 * st, 0, 2.3 - 2.2 * st)
            ring.rotation_euler = (-0.6 * st, 0, -0.4 * st)
            ring.scale = (1.0, 1.0, 1.0)
        ring.keyframe_insert("location", frame=f)
        ring.keyframe_insert("rotation_euler", frame=f)
        ring.keyframe_insert("scale", frame=f)

def animate_ring_50(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.4:
            st = t / 0.4
            ring.location = (0, 0, 3.4 - 1.8 * st)
            ring.rotation_euler = (0, 0, 0)
            ring.scale = (1.0, 1.0, 1.0)
        else: # hugs around neck / torso area with elastic flex
            st = (t - 0.4) / 0.6
            wobble = math.exp(-st * 4) * math.sin(st * 16) * 0.15
            ring.location = (0, 0, 1.6 - 0.1 * st)
            ring.rotation_euler = (0.2 * math.sin(st * 6), 0, 0)
            ring.scale = (1.25 + wobble, 1.25 + wobble, 0.75 - wobble)
        ring.keyframe_insert("location", frame=f)
        ring.keyframe_insert("rotation_euler", frame=f)
        ring.keyframe_insert("scale", frame=f)

def animate_ring_75(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.3:
            st = t / 0.3
            ring.location = (0, 0, 3.4 - 2.3 * st)
            ring.scale = (1.0, 1.0, 1.0)
        else: # stretches and drapes loosely over middle section like rubber band
            st = (t - 0.3) / 0.7
            wobble = math.exp(-st * 2.5) * math.sin(st * 12) * 0.1
            ring.location = (0, 0, 1.1 - 0.2 * st)
            ring.rotation_euler = (0.35, 0, 0.2)
            ring.scale = (1.55 + wobble, 1.55 + wobble, 0.55 - wobble)
        ring.keyframe_insert("location", frame=f)
        ring.keyframe_insert("rotation_euler", frame=f)
        ring.keyframe_insert("scale", frame=f)

def animate_ring_100(start_f, end_f):
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.25:
            st = t / 0.25
            ring.location = (0, 0, 3.4 - 2.5 * st)
            ring.scale = (1.0, 1.0, 1.0)
        else: # molten liquid melting over snowman body down to base
            st = (t - 0.25) / 0.75
            ring.location = (0, 0, 0.9 - 1.8 * st)
            ring.rotation_euler = (0, 0, 0)
            ring.scale = (1.2 + 1.6 * st, 1.2 + 1.6 * st, 0.35 - 0.3 * st)
        ring.keyframe_insert("location", frame=f)
        ring.keyframe_insert("rotation_euler", frame=f)
        ring.keyframe_insert("scale", frame=f)

animate_ring_0(1, 60)
animate_ring_25(90, 180)
animate_ring_50(210, 270)
animate_ring_75(300, 510)
animate_ring_100(540, 660)

# Camera & Lighting
bpy.ops.object.camera_add(location=(0, -6.5, 1.0), rotation=(math.radians(82), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 52

bpy.ops.object.light_add(type='AREA', location=(3.2, -4.0, 4.5), rotation=(math.radians(45), 0, math.radians(30)))
key = bpy.context.active_object
key.data.energy = 900
key.data.size = 2.5

bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.5, 3.0), rotation=(math.radians(45), 0, math.radians(-30)))
fill = bpy.context.active_object
fill.data.energy = 450
fill.data.size = 3.0

bpy.ops.object.light_add(type='POINT', location=(0, 2.8, 3.2))
rim = bpy.context.active_object
rim.data.energy = 600
rim.data.color = (1.0, 0.92, 0.8)

world = bpy.data.worlds.new("StudioWorld2")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.74, 0.78, 0.84, 1.0)

print("[*] Scene 2 configured.")
