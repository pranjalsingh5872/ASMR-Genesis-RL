import bpy
import math
import os
import sys

# Factory reset clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 90  # 3-second seamless loop

# 1080 x 1920 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# EEVEE Next Engine for ultra-soft Subsurface Scattering & Refraction
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.Scene, 'eevee_next') else 'BLENDER_EEVEE'

os.makedirs("output/embryo_soft_frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/embryo_soft_frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# -------------------------------------------------------------
# 1. ULTRA-SOFT TRANSLUCENT JELLY / GUMMY SHADERS
# -------------------------------------------------------------
# Outer Amniotic Sac (Extremely soft, viscous liquid membrane)
pod_mat = bpy.data.materials.new(name="Amniotic_Membrane")
pod_mat.use_nodes = True
bsdf_pod = pod_mat.node_tree.nodes.get("Principled BSDF")
if bsdf_pod:
    # Soft warm pearl/cyan iridescent mist
    bsdf_pod.inputs["Base Color"].default_value = (0.78, 0.92, 0.96, 1.0)
    bsdf_pod.inputs["Roughness"].default_value = 0.22 # Frosted/Soft, not sharp hard glass!
    if "Transmission Weight" in bsdf_pod.inputs:
        bsdf_pod.inputs["Transmission Weight"].default_value = 0.88
    elif "Transmission" in bsdf_pod.inputs:
        bsdf_pod.inputs["Transmission"].default_value = 0.88
    if "IOR" in bsdf_pod.inputs:
        bsdf_pod.inputs["IOR"].default_value = 1.25

# The Embryo Body: 100% Super-Soft Organic Translucent Gummy Flesh
jelly_mat = bpy.data.materials.new(name="Ultra_Soft_Jelly_Organism")
jelly_mat.use_nodes = True
nodes = jelly_mat.node_tree.nodes
links = jelly_mat.node_tree.links
bsdf_jelly = nodes.get("Principled BSDF")
if bsdf_jelly:
    # Soft pastel peach/pale sage organic tissue tone
    bsdf_jelly.inputs["Base Color"].default_value = (0.92, 0.85, 0.82, 1.0)
    bsdf_jelly.inputs["Roughness"].default_value = 0.35 # Velvety soft finish
    
    # Subsurface Scattering (SSS) gives the deep fleshy translucent glow
    if "Subsurface Weight" in bsdf_jelly.inputs:
        bsdf_jelly.inputs["Subsurface Weight"].default_value = 0.95
        bsdf_jelly.inputs["Subsurface Radius"].default_value = (1.2, 0.5, 0.3)
        bsdf_jelly.inputs["Subsurface Scale"].default_value = 0.15
    elif "Subsurface" in bsdf_jelly.inputs:
        bsdf_jelly.inputs["Subsurface"].default_value = 0.95

# Bioluminescent Warm Heart Core (Soft breathing light, not harsh neon)
core_mat = bpy.data.materials.new(name="Warm_Soul_Core")
core_mat.use_nodes = True
bsdf_core = core_mat.node_tree.nodes.get("Principled BSDF")
if bsdf_core:
    bsdf_core.inputs["Base Color"].default_value = (0.2, 0.95, 0.85, 1.0)
    if "Emission Color" in bsdf_core.inputs:
        bsdf_core.inputs["Emission Color"].default_value = (0.2, 0.95, 0.85, 1.0)
        bsdf_core.inputs["Emission Strength"].default_value = 2.8 # gentle warm glow
    elif "Emission" in bsdf_core.inputs:
        bsdf_core.inputs["Emission"].default_value = (0.2, 0.95, 0.85, 1.0)

# -------------------------------------------------------------
# 2. ULTRA-SOFT CURVED ORGANIC GEOMETRY (No rigid primitives)
# -------------------------------------------------------------
# A. Soft Amniotic Pod
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.35, location=(0, 0, 0), segments=48, ring_count=32)
pod = bpy.context.active_object
pod.name = "Soft_Amniotic_Sac"
pod.scale = (0.95, 0.95, 1.35)
bpy.ops.object.transform_apply(scale=True)
pod.data.materials.append(pod_mat)

# B. Soft Fetal Body (Smooth, Curled Head and Back)
# Head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(-0.05, 0, 0.55), segments=48, ring_count=32)
head = bpy.context.active_object
head.name = "Embryo_Head"
head.scale = (0.9, 0.85, 1.05)
bpy.ops.object.transform_apply(scale=True)
head.data.materials.append(jelly_mat)

# Torso / Curled Body
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48, location=(-0.25, 0, 0.05), segments=48, ring_count=32)
body = bpy.context.active_object
body.name = "Embryo_Body"
body.scale = (0.85, 0.8, 1.25)
body.rotation_euler = (0, math.radians(-18), 0)
bpy.ops.object.transform_apply(scale=True, rotation=True)
body.data.materials.append(jelly_mat)

# Tail / Lower tuck
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(-0.08, 0, -0.45), segments=48, ring_count=32)
tail = bpy.context.active_object
tail.name = "Embryo_Tail"
tail.scale = (0.9, 0.85, 0.95)
bpy.ops.object.transform_apply(scale=True)
tail.data.materials.append(jelly_mat)

# Join head, body, tail into ONE single seamless soft organism mesh
bpy.ops.object.select_all(action='DESELECT')
head.select_set(True)
body.select_set(True)
tail.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
embryo_mesh = bpy.context.active_object
embryo_mesh.name = "Soft_Embryo_Organism"

# Add Remesh / Subdivision for 100% seamless, smooth, squishy edges
subsurf = embryo_mesh.modifiers.new("Smooth_Jelly", 'SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

# C. Floating Heart Core (Suspended inside the soft body)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(-0.16, 0, 0.12))
core = bpy.context.active_object
core.name = "Heart_Core"
core.data.materials.append(core_mat)

# -------------------------------------------------------------
# 3. HIGH-ELASTICITY HARMONIC SQUISH & WOBBLE PHYSICS
# -------------------------------------------------------------
total_f = 90
for f in range(1, total_f + 1):
    scene.frame_set(f)
    t = (2 * math.pi * f) / float(total_f)
    
    # 1. Gentle Amniotic Liquid Floating Drift
    drift_z = math.sin(t) * 0.08
    drift_rot = math.sin(t * 0.5) * 0.04
    embryo_mesh.location = (0, 0, drift_z)
    embryo_mesh.rotation_euler = (0, drift_rot, 0)
    embryo_mesh.keyframe_insert("location", frame=f)
    embryo_mesh.keyframe_insert("rotation_euler", frame=f)

    # 2. Ultra-Soft Gelatin Squeeze & Stretch (Hooke's Law Volume-Preserving Squish)
    # When stretching in Z (breath in), X and Y contract to keep natural volume:
    # Scale_X * Scale_Y * Scale_Z ~= 1.0 (Real jelly physics!)
    squish_z = 1.0 + math.sin(t) * 0.07
    squish_xy = 1.0 / math.sqrt(squish_z) # Physical volume conservation
    embryo_mesh.scale = (squish_xy, squish_xy, squish_z)
    embryo_mesh.keyframe_insert("scale", frame=f)

    # 3. Soft Subsurface Core Pulse (Double heartbeat wave)
    pulse = 1.0 + (math.sin(t * 2) ** 4) * 0.35
    core.location = (-0.16, 0, 0.12 + drift_z)
    core.scale = (pulse, pulse, pulse)
    core.keyframe_insert("location", frame=f)
    core.keyframe_insert("scale", frame=f)

# -------------------------------------------------------------
# 4. SOFT WARM VOLUMETRIC STUDIO LIGHTING
# -------------------------------------------------------------
cam_data = bpy.data.cameras.new("Soft_Macro_Cam")
cam_data.lens = 70.0 # Intimate macro focal length
cam_obj = bpy.data.objects.new("Soft_Macro_Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0, -4.0, 0.05)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

# Soft Warm Key Light (Skin/Jelly illuminator)
l1 = bpy.data.lights.new("Soft_Key", type='AREA')
l1.energy = 160.0
l1.color = (0.95, 0.85, 0.75) # Warm candle/biological tone
l1.size = 3.5 # Huge light area = ultra-soft shadows
o1 = bpy.data.objects.new("Soft_Key", l1)
bpy.context.collection.objects.link(o1)
o1.location = (1.8, -2.2, 1.8)

# Subtle Cyan Fill
l2 = bpy.data.lights.new("Cyan_Fill", type='AREA')
l2.energy = 80.0
l2.color = (0.2, 0.85, 0.95)
l2.size = 3.0
o2 = bpy.data.objects.new("Cyan_Fill", l2)
bpy.context.collection.objects.link(o2)
o2.location = (-1.8, -1.8, -1.0)

print("[*] Rendering 90 Frames of ULTRA-SOFT Gelatin Organism...")
bpy.ops.render.render(animation=True)
print("[+] Soft Organism render completed successfully!")
