import bpy
import math
import os

# Clean slate
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

out_dir = os.path.abspath("output/test_cloth_pure_physics")
os.makedirs(out_dir, exist_ok=True)

# Gold material
gold_mat = bpy.data.materials.new("Gold_24K")
gold_mat.use_nodes = True
bsdf = gold_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.28, 1.0)
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.05

# Marble material
marble_mat = bpy.data.materials.new("Verde_Alpi")
marble_mat.use_nodes = True
m_bsdf = marble_mat.node_tree.nodes.get("Principled BSDF")
m_bsdf.inputs['Base Color'].default_value = (0.02, 0.12, 0.06, 1.0)
m_bsdf.inputs['Metallic'].default_value = 0.0
m_bsdf.inputs['Roughness'].default_value = 0.08

# Pedestal with collision
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.8, location=(0, 0, -0.4))
pedestal = bpy.context.active_object
pedestal.data.materials.append(marble_mat)
bpy.ops.object.shade_smooth()

col = pedestal.modifiers.new(name="Collision", type='COLLISION')
col.settings.thickness_outer = 0.005
col.settings.damping = 0.3
col.settings.cloth_friction = 0.2

# Jelly ball starting above pedestal at (0, 0, 1.2)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0, 0, 1.2), segments=36, ring_count=24)
jelly = bpy.context.active_object
jelly.name = "Jelly_Actor"
jelly.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Cloth Pressure
cloth = jelly.modifiers.new(name="ClothPressure", type='CLOTH')
cs = cloth.settings
cs.quality = 6
cs.mass = 0.35
cs.air_damping = 0.3
cs.tension_stiffness = 12.0
cs.compression_stiffness = 12.0
cs.shear_stiffness = 5.0
cs.bending_stiffness = 0.15 # Soft jelly

cs.tension_damping = 2.0
cs.compression_damping = 2.0
cs.shear_damping = 1.5
cs.bending_damping = 0.4

cs.use_pressure = True
cs.uniform_pressure_force = 2.8
cs.use_pressure_volume = True
cs.target_volume = 1.0
cs.pressure_factor = 1.0

cloth.collision_settings.use_collision = True
cloth.collision_settings.distance_min = 0.008
cloth.collision_settings.use_self_collision = True
cloth.collision_settings.self_distance_min = 0.008

# Subsurf modifier
sub = jelly.modifiers.new(name="Subsurf", type='SUBSURF')
sub.levels = 1

# Camera & lighting
bpy.ops.object.camera_add(location=(0, -4.5, 0.8), rotation=(math.radians(82), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 50

bpy.ops.object.light_add(type='AREA', location=(2.5, -2.5, 3.5), rotation=(math.radians(45), 0, math.radians(30)))
bpy.context.active_object.data.energy = 800
bpy.ops.object.light_add(type='AREA', location=(-2.5, -2.0, 2.5), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 400

world = bpy.data.worlds.new('W')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.78, 0.81, 0.84, 1.0)

# Simulate sequentially from frame 1 to 90 and render frames 1, 20, 32, 45, 60
render_targets = [1, 20, 32, 45, 60]
print("[*] Simulating physical cloth drop...")
for f in range(1, 91):
    scene.frame_set(f)
    if f in render_targets:
        scene.render.filepath = os.path.join(out_dir, f"frame_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[+] Rendered frame {f}")

print("[SUCCESS] Pure physical cloth simulation rendered!")
