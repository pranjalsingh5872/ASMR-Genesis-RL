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

# Cycles OptiX setup
cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.compute_device_type = 'OPTIX'
cycles_prefs.get_devices()
for dev in cycles_prefs.devices:
    if 'RTX 4060' in dev.name and dev.type == 'OPTIX':
        dev.use = True
    else:
        dev.use = False

scene.cycles.device = 'GPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'

out_dir = os.path.abspath("output/test_cloth_physics")
os.makedirs(out_dir, exist_ok=True)

# 1. MATERIALS
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

# 2. COLLISION OBSTACLE (Marble Pedestal)
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.8, location=(0, 0, -0.4))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal_Collision"
pedestal.data.materials.append(marble_mat)
bpy.ops.object.shade_smooth()

# Add Collision modifier to pedestal
col_mod = pedestal.modifiers.new(name="Collision", type='COLLISION')
col_mod.settings.thickness_outer = 0.005
col_mod.settings.damping = 0.3
col_mod.settings.cloth_friction = 0.1

# 3. SOFT JELLY CLOTH PRESSURE ACTOR
# Create high-res UV sphere / capsule
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0, 0, 1.8), segments=36, ring_count=24)
jelly = bpy.context.active_object
jelly.name = "Cloth_Pressure_Jelly"
jelly.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Add Cloth Modifier with Internal Pressure & Volume Conservation
cloth_mod = jelly.modifiers.new(name="ClothPressure", type='CLOTH')
cs = cloth_mod.settings
cs.quality = 6
cs.mass = 0.25 # Light responsive mass
cs.air_damping = 0.5

# Stiffness settings for jelly
cs.tension_stiffness = 18.0
cs.compression_stiffness = 18.0
cs.shear_stiffness = 8.0
cs.bending_stiffness = 0.4 # Low bending allows organic squish & bulging

# Damping settings
cs.tension_damping = 2.5
cs.compression_damping = 2.5
cs.shear_damping = 2.0
cs.bending_damping = 0.6

# INTERNAL PRESSURE (The key to 3D jelly/soft-body simulation!)
cs.use_pressure = True
cs.uniform_pressure_force = 3.2   # Internal gas/fluid pressure
cs.use_pressure_volume = True     # Conserves total 3D volume
cs.target_volume = 1.0
cs.pressure_factor = 1.0

# Cloth Collision settings (self-collision prevents self-intersection)
col_settings = cloth_mod.collision_settings
col_settings.use_collision = True
col_settings.distance_min = 0.008
col_settings.use_self_collision = True
col_settings.self_distance_min = 0.008

# Subsurf modifier on top of cloth for ultra-smooth surface
sub_mod = jelly.modifiers.new(name="Subsurf", type='SUBSURF')
sub_mod.levels = 1
sub_mod.render_levels = 1

# 4. CAMERA & STUDIO LIGHTING
bpy.ops.object.camera_add(location=(0, -4.5, 1.1), rotation=(math.radians(80), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 50

bpy.ops.object.light_add(type='AREA', location=(2.5, -2.5, 3.5), rotation=(math.radians(45), 0, math.radians(30)))
bpy.context.active_object.data.energy = 800
bpy.ops.object.light_add(type='AREA', location=(-2.5, -2.0, 2.5), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 400

world = bpy.data.worlds.new('World_ASMR')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.78, 0.81, 0.84, 1.0)

# 5. RUN SIMULATION & RENDER TEST FRAMES
# Sequentially evaluate physics frames 1 to 90
print("[*] Evaluating Cloth Pressure Physics frames 1 to 90...")
test_render_frames = [20, 35, 45, 60, 80]

for f in range(1, 91):
    scene.frame_set(f)
    if f in test_render_frames:
        scene.render.filepath = os.path.join(out_dir, f"cloth_jelly_frame_{f:03d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[+] Rendered Cloth Pressure test frame: {f}")

print("[*] Cloth Pressure Simulation test completed!")
