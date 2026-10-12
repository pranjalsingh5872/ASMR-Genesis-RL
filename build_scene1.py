import bpy
import math
import os

# Clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 26 * 30  # 780 frames for Scene 1 (26 seconds)

# 1080x1920 9:16 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# EEVEE Next Engine for ultra-fast, clean shading
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.Scene, 'eevee_next') else 'BLENDER_EEVEE'

os.makedirs("output/scene1_frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/scene1_frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# -------------------------------------------------------------
# Materials Setup
# -------------------------------------------------------------
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

# Procedural Green Veined Marble
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

    noise.inputs["Scale"].default_value = 4.5
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.55

    # Color Ramp for green veined marble (pale sage green to deep forest marble vein)
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[0].color = (0.75, 0.82, 0.77, 1.0) # pale sage marble
    color_ramp.color_ramp.elements[1].position = 0.75
    color_ramp.color_ramp.elements[1].color = (0.18, 0.32, 0.25, 1.0) # deep green vein

    links.new(noise.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.18
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return mat

marble_mat = create_green_marble_material()
gold_mat = create_pbr_material("Reflective_Gold", (1.0, 0.76, 0.28, 1.0), metallic=0.98, roughness=0.1)
glass_mat = create_pbr_material("Clear_Glass", (0.95, 0.98, 1.0, 1.0), metallic=0.0, roughness=0.03, transmission=0.96)

# -------------------------------------------------------------
# Geometry: Scene 1 Setup
# -------------------------------------------------------------
# 1. Marble Base with Central Funnel Depression
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.0, location=(0, 0, -1.8))
base = bpy.context.active_object
base.name = "Marble_Base"
base.data.materials.append(marble_mat)

# Gold Rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.06, location=(0, 0, -0.8))
gold_rim = bpy.context.active_object
gold_rim.data.materials.append(gold_mat)

# Two Vertical Marble Pillars (Left and Right)
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, location=(-1.15, 0, 0.0))
pillar_l = bpy.context.active_object
pillar_l.name = "Pillar_Left"
pillar_l.data.materials.append(marble_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, location=(1.15, 0, 0.0))
pillar_r = bpy.context.active_object
pillar_r.name = "Pillar_Right"
pillar_r.data.materials.append(marble_mat)

# Top Dropper Nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.6, location=(0, 0, 2.7))
top_nozzle = bpy.context.active_object
top_nozzle.data.materials.append(gold_mat)

# 2. Curved Glass Tube (Elevated between nozzle and base)
# Create a curved path/mesh representing the J-bend / curved funnel tube
curve_data = bpy.data.curves.new('GlassTubeCurve', type='CURVE')
curve_data.dimensions = '3D'
polyline = curve_data.splines.new('BEZIER')
polyline.bezier_points.add(2)

# Point 0: Top entrance
p0 = polyline.bezier_points[0]
p0.co = (0.0, 0.0, 1.8)
p0.handle_left = (0.0, 0.0, 2.1)
p0.handle_right = (0.0, 0.0, 1.4)

# Point 1: Curve mid
p1 = polyline.bezier_points[1]
p1.co = (-0.25, 0.0, 0.8)
p1.handle_left = (-0.1, 0.0, 1.1)
p1.handle_right = (-0.45, 0.0, 0.5)

# Point 2: Bottom exit pointing towards left pillar
p2 = polyline.bezier_points[2]
p2.co = (-0.6, 0.0, 0.35)
p2.handle_left = (-0.5, 0.0, 0.45)
p2.handle_right = (-0.75, 0.0, 0.2)

curve_data.bevel_depth = 0.32
curve_data.bevel_resolution = 4
curve_obj = bpy.data.objects.new('Curved_Glass_Tube', curve_data)
bpy.context.collection.objects.link(curve_obj)
curve_obj.data.materials.append(glass_mat)

# 3. Gold Capsule Actor
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.7, location=(0, 0, 2.5))
capsule = bpy.context.active_object
capsule.name = "Gold_Capsule"
capsule.data.materials.append(gold_mat)
sub = capsule.modifiers.new("Subsurf", 'SUBSURF')
sub.levels = 2

# -------------------------------------------------------------
# Stage 1: Animation Trajectories for 5 Softness Stages
# -------------------------------------------------------------
# Stages:
# 0%   (0s  - 2s  / f1   - f60) : Rigid ricochet off glass and left pillar
# 25%  (3s  - 5s  / f90  - f150): Compresses, enters, jams inside the curve
# 50%  (6s  - 12s / f180 - f360): Flexes, exits bottom curve, hits pillar, drops in funnel
# 75%  (13s - 22s / f390 - f660): Smooth gelatin stretch, bends around pillar, drops on basin
# 100% (23s - 26s / f690 - f780): Liquid slumping, pools into golden blob

def animate_stage_0(start_f, end_f):
    # Rigid: drops, strikes tube lip at f25, ricochets off left pillar at f40, flies off
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.35: # falling
            capsule.location = (0, 0, 2.5 - 2.8 * (t / 0.35))
            capsule.rotation_euler = (0, 0, 0)
            capsule.scale = (1, 1, 1)
        elif t < 0.65: # ricochet towards left pillar
            sub_t = (t - 0.35) / 0.3
            capsule.location = (-0.1 - 1.05 * sub_t, 0, 1.5 - 1.2 * sub_t)
            capsule.rotation_euler = (sub_t * 3.0, 0, sub_t * 4.0)
            capsule.scale = (1, 1, 1)
        else: # bounce off pillar and fly away
            sub_t = (t - 0.65) / 0.35
            capsule.location = (-1.15 - 1.8 * sub_t, 0, 0.3 + 0.8 * math.sin(sub_t * math.pi) - 1.5 * sub_t)
            capsule.rotation_euler = (3.0 + sub_t * 6.0, 0, 4.0 + sub_t * 5.0)
            capsule.scale = (1, 1, 1)
        capsule.keyframe_insert("location", frame=f)
        capsule.keyframe_insert("rotation_euler", frame=f)
        capsule.keyframe_insert("scale", frame=f)

def animate_stage_25(start_f, end_f):
    # 25% Soft: Slight compress, gets stuck/jammed in curve
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.5:
            capsule.location = (-0.12 * (t / 0.5), 0, 2.5 - 1.5 * (t / 0.5))
            capsule.rotation_euler = (0, 0, -0.3 * (t / 0.5))
            capsule.scale = (1, 1, 1)
        else: # jams in tube, vibrating slightly
            wobble = math.sin((t - 0.5) * 40) * 0.02
            capsule.location = (-0.12 + wobble, 0, 1.0)
            capsule.rotation_euler = (0, 0, -0.35)
            capsule.scale = (1.1, 1.1, 0.85) # slight compression
        capsule.keyframe_insert("location", frame=f)
        capsule.keyframe_insert("rotation_euler", frame=f)
        capsule.keyframe_insert("scale", frame=f)

def animate_stage_50(start_f, end_f):
    # 50% Soft: Flexes through tube, hits left pillar, falls into funnel
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.4: # sliding through bend
            st = t / 0.4
            capsule.location = (-0.45 * st, 0, 2.5 - 2.1 * st)
            capsule.rotation_euler = (0, 0, -1.1 * st)
            capsule.scale = (0.85, 0.85, 1.25) # stretches through tube
        elif t < 0.65: # exits and hits left pillar
            st = (t - 0.4) / 0.25
            capsule.location = (-0.45 - 0.7 * st, 0, 0.4 - 0.3 * st)
            capsule.rotation_euler = (0, 0, -1.1 - 0.5 * st)
            capsule.scale = (1.2, 1.2, 0.8) # impact squish
        else: # bounces down into funnel
            st = (t - 0.65) / 0.35
            capsule.location = (-1.15 + 1.15 * st, 0, 0.1 - 0.9 * st)
            capsule.rotation_euler = (0, 0, -1.6 + 1.6 * st)
            capsule.scale = (1.1, 1.1, 0.9)
        capsule.keyframe_insert("location", frame=f)
        capsule.keyframe_insert("rotation_euler", frame=f)
        capsule.keyframe_insert("scale", frame=f)

def animate_stage_75(start_f, end_f):
    # 75% Soft: Smooth gelatin elongation, bends effortlessly around pillar, lands on basin
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.5:
            st = t / 0.5
            capsule.location = (-0.6 * st, 0, 2.5 - 2.2 * st)
            capsule.rotation_euler = (0, 0, -1.3 * st)
            capsule.scale = (0.7, 0.7, 1.6) # strong gelatin elongation
        else:
            st = (t - 0.5) / 0.5
            capsule.location = (-0.6 - 0.4 * math.sin(st * math.pi) + 0.6 * st, 0, 0.3 - 1.1 * st)
            capsule.rotation_euler = (0, 0, -1.3 + 1.3 * st)
            # wobble settle
            w = math.exp(-st * 3) * math.sin(st * 15) * 0.2
            capsule.scale = (1.3 + w, 1.3 + w, 0.7 - w)
        capsule.keyframe_insert("location", frame=f)
        capsule.keyframe_insert("rotation_euler", frame=f)
        capsule.keyframe_insert("scale", frame=f)

def animate_stage_100(start_f, end_f):
    # 100% Soft: Liquid slump, completely pools and flattens into golden puddle
    for f in range(start_f, end_f + 1):
        scene.frame_set(f)
        t = (f - start_f) / float(end_f - start_f)
        if t < 0.5:
            st = t / 0.5
            capsule.location = (-0.6 * st, 0, 2.5 - 2.4 * st)
            capsule.rotation_euler = (0, 0, -1.4 * st)
            capsule.scale = (0.5, 0.5, 2.0) # oozing liquid stream
        else: # pooling into flat puddle in funnel
            st = (t - 0.5) / 0.5
            capsule.location = (-0.6 + 0.6 * st, 0, 0.1 - 0.9 * st)
            capsule.rotation_euler = (0, 0, 0)
            # puddle expansion
            capsule.scale = (1.0 + 1.8 * st, 1.0 + 1.8 * st, 0.5 - 0.45 * st)
        capsule.keyframe_insert("location", frame=f)
        capsule.keyframe_insert("rotation_euler", frame=f)
        capsule.keyframe_insert("scale", frame=f)

print("[*] Keyframing all 5 softness stages for Scene 1...")
animate_stage_0(1, 60)      # 00:00 - 00:02
animate_stage_25(90, 150)   # 00:03 - 00:05
animate_stage_50(180, 360)  # 00:06 - 00:12
animate_stage_75(390, 660)  # 00:13 - 00:22
animate_stage_100(690, 780) # 00:23 - 00:26

# Camera Setup
bpy.ops.object.camera_add(location=(0, -6.8, 0.8), rotation=(math.radians(84), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 52

# Lighting
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

# Minimalist Pastel Background
world = bpy.data.worlds.new("StudioWorld")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.74, 0.78, 0.84, 1.0)

print("[*] Scene 1 script configured. Ready to render!")
