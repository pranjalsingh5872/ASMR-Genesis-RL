import bpy
import math
import os

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 90

# 1080 x 1920 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# EEVEE Next Engine
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.Scene, 'eevee_next') else 'BLENDER_EEVEE'

# Output directory
os.makedirs("output/frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# Materials
def get_pbr_mat(name, color, roughness=0.1, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
    return mat

marble = get_pbr_mat("Marble", (0.85, 0.85, 0.83, 1.0), roughness=0.3)
gold = get_pbr_mat("Gold", (0.95, 0.75, 0.25, 1.0), roughness=0.1, metallic=0.95)
glass = get_pbr_mat("Glass", (0.9, 0.95, 1.0, 1.0), roughness=0.05, transmission=0.95)

# 1. Marble Pedestal (Lower down, centered)
bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=2.0, location=(0, 0, -1.8))
pedestal = bpy.context.active_object
pedestal.data.materials.append(marble)

# Gold trim on pedestal rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.06, location=(0, 0, -0.8))
gold_rim = bpy.context.active_object
gold_rim.data.materials.append(gold)

# Left & Right Marble Pillars
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, location=(-1.1, 0, 0.0))
p_l = bpy.context.active_object
p_l.data.materials.append(marble)

bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, location=(1.1, 0, 0.0))
p_r = bpy.context.active_object
p_r.data.materials.append(marble)

# 2. Golden Dropper Nozzle at the Top
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.8, location=(0, 0, 2.5))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold)

# 3. Soft-Body / Elastic Glass Capsule Dropping Through Frame
# Animate its descent and deformation from frame 1 to 90
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.0, location=(0, 0, 2.3))
capsule = bpy.context.active_object
capsule.name = "Glass_Capsule"
capsule.data.materials.append(glass)

# Add subdivision surface for organic look
sub = capsule.modifiers.new("Subsurf", 'SUBSURF')
sub.levels = 2

# Keyframe falling motion & bending (like the reference 0% SOFT)
for f in range(1, 91):
    scene.frame_set(f)
    t = (f - 1) / 89.0  # 0.0 to 1.0
    
    # Position: drops from top nozzle (z=2.3) down towards the pedestal (z=-0.7)
    z_pos = 2.3 - 2.8 * t
    capsule.location = (0, 0, z_pos)
    capsule.keyframe_insert(data_path="location", frame=f)

    # Elastic wiggle / tilt rotation
    tilt = math.sin(t * math.pi * 3) * 0.25
    capsule.rotation_euler = (tilt, 0, tilt * 0.5)
    capsule.keyframe_insert(data_path="rotation_euler", frame=f)

    # Squash and stretch (elastic soft physics)
    if z_pos < -0.3:
        squash = 1.0 + ((-0.3 - z_pos) * 0.6)
        stretch = 1.0 / math.sqrt(squash)
        capsule.scale = (squash, squash, stretch)
    else:
        capsule.scale = (1.0, 1.0, 1.0)
    capsule.keyframe_insert(data_path="scale", frame=f)

# 4. Camera (Positioned to frame the entire composition perfectly)
bpy.ops.object.camera_add(location=(0, -6.5, 0.6), rotation=(math.radians(85), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 55

# 5. Studio Lighting
bpy.ops.object.light_add(type='AREA', location=(3.0, -3.5, 4.0), rotation=(math.radians(45), 0, math.radians(30)))
key = bpy.context.active_object
key.data.energy = 800
key.data.size = 2.5

bpy.ops.object.light_add(type='AREA', location=(-3.0, -3.0, 2.5), rotation=(math.radians(45), 0, math.radians(-30)))
fill = bpy.context.active_object
fill.data.energy = 400
fill.data.size = 3.0

bpy.ops.object.light_add(type='POINT', location=(0, 2.5, 3.0))
rim = bpy.context.active_object
rim.data.energy = 500
rim.data.color = (1.0, 0.9, 0.75)

# Studio Background
world = bpy.data.worlds.new("Studio")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.70, 0.75, 0.84, 1.0)

print("[*] Rendering corrected 1080x1920 composition...")
bpy.ops.render.render(animation=True)
print("[+] Render complete!")
