import bpy
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from blender_physics_sim import make_collision_obstacle, make_cloth_pressure_actor, add_geometry_nodes_jiggle, add_smooth_subsurf

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 120

scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.engine = 'CYCLES'

cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.compute_device_type = 'OPTIX'
cycles_prefs.get_devices()
for dev in cycles_prefs.devices:
    if 'RTX 4060' in dev.name and dev.type == 'OPTIX':
        dev.use = True
    else:
        dev.use = False

scene.cycles.device = 'GPU'
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'

out_dir = os.path.abspath("output/test_squish_physics")
os.makedirs(out_dir, exist_ok=True)

# Gold material
gold_mat = bpy.data.materials.new("Gold_24K")
gold_mat.use_nodes = True
bsdf = gold_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.28, 1.0)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.05

# Verde Alpi Marble
marble_mat = bpy.data.materials.new("Verde_Alpi")
marble_mat.use_nodes = True
m_bsdf = marble_mat.node_tree.nodes.get("Principled BSDF")
m_bsdf.inputs['Base Color'].default_value = (0.02, 0.12, 0.06, 1.0)
m_bsdf.inputs['Roughness'].default_value = 0.08

# Pedestal with a slight curved basin bowl
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.8, location=(0, 0, -0.4))
pedestal = bpy.context.active_object
pedestal.data.materials.append(marble_mat)
bpy.ops.object.shade_smooth()

# Carve gentle basin in center
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0, 0, 0.8))
bowl_cutter = bpy.context.active_object
b_mod = pedestal.modifiers.new('Carve', 'BOOLEAN')
b_mod.object = bowl_cutter
b_mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = pedestal
bpy.ops.object.modifier_apply(modifier='Carve')
bpy.data.objects.remove(bowl_cutter, do_unlink=True)

# Collision on pedestal
make_collision_obstacle(pedestal, thickness=0.005, damping=0.25, friction=0.15)

# Jelly sphere starting at z=2.0 (falls under pure physics)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(0, 0, 2.0), segments=40, ring_count=28)
jelly = bpy.context.active_object
jelly.name = "Jelly_Soft_Actor"
jelly.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Cloth Pressure with extra squishy settings
cloth = make_cloth_pressure_actor(
    jelly,
    mass=0.40,            # Good momentum
    pressure=2.4,         # Internal hydrostatic volume inflation
    target_volume=1.0,
    tension=8.0,          # Lower tension = juicy lateral stretching
    compression=8.0,
    shear=4.0,
    bending=0.06,         # Ultra soft bending = deep organic pancake squish!
    damping=1.2
)

# Geometry nodes surface ripple
add_geometry_nodes_jiggle(jelly, amplitude=0.008, frequency=8.0)

# Subsurf
add_smooth_subsurf(jelly, levels=1)

# Camera & lighting
bpy.ops.object.camera_add(location=(0, -5.2, 0.9), rotation=(math.radians(82), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 52

bpy.ops.object.light_add(type='AREA', location=(2.8, -3.0, 3.8), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 850
bpy.ops.object.light_add(type='AREA', location=(-2.8, -2.5, 2.5), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 450
bpy.ops.object.light_add(type='AREA', location=(0, 2.5, 3.5), rotation=(math.radians(-35), 0, 0))
bpy.context.active_object.data.energy = 600

world = bpy.data.worlds.new('W')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.78, 0.81, 0.84, 1.0)

# Sequential frame evaluation and target rendering
targets = [1, 35, 46, 60, 85]
print(f"[*] Running physical drop test across {scene.frame_end} frames...")

for f in range(1, 101):
    scene.frame_set(f)
    if f in targets:
        scene.render.filepath = os.path.join(out_dir, f"squish_frame_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[+] Rendered squish frame {f}")

print("[SUCCESS] Squish test complete!")
