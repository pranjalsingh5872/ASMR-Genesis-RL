import bpy
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from blender_physics_sim import (
    make_collision_obstacle,
    make_cloth_pressure_actor,
    add_geometry_nodes_jiggle,
    add_smooth_subsurf,
    create_opaque_verde_alpi,
    create_opaque_24k_gold,
    create_optical_glass
)

# 1. Clean factory slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 720  # Exactly 12.0 seconds at 60 FPS

scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.engine = 'CYCLES'

# Cycles GPU OptiX Configuration
cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
cycles_prefs.compute_device_type = 'OPTIX'
cycles_prefs.get_devices()
for dev in cycles_prefs.devices:
    if 'RTX 4060' in dev.name and dev.type == 'OPTIX':
        dev.use = True
    else:
        dev.use = False

scene.cycles.device = 'GPU'
scene.cycles.samples = 20  # Fast, crystal-clear with OptiX Denoising
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 12

out_dir = os.path.abspath("output/cloth_jelly_12s_60fps_frames")
os.makedirs(out_dir, exist_ok=True)
scene.render.image_settings.file_format = 'PNG'

# ------------------------------------------------------------------------------
# 2. LUXURY 100% OPAQUE MATERIALS
# ------------------------------------------------------------------------------
marble_mat = create_opaque_verde_alpi()
gold_mat = create_opaque_24k_gold()
glass_mat = create_optical_glass()

# Studio Cyclorama Backdrop
bpy.ops.mesh.primitive_plane_add(size=18.0, location=(0, 2.5, -2.8))
cyclorama = bpy.context.active_object
cyclorama.name = "Studio_Cyclorama"
bg_mat = bpy.data.materials.new("Backdrop")
bg_mat.use_nodes = True
bg_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (0.76, 0.79, 0.83, 1.0)
bg_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.40
cyclorama.data.materials.append(bg_mat)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=24)
bpy.ops.object.mode_set(mode='OBJECT')
for v in cyclorama.data.vertices:
    if v.co.y > 0.5:
        dist = v.co.y - 0.5
        v.co.z += (dist ** 2) * 0.18
cyclorama.data.update()
bpy.ops.object.shade_smooth()

# Pedestal (Solid Verde Alpi Marble)
bpy.ops.mesh.primitive_cylinder_add(radius=1.95, depth=1.6, location=(0, 0, -0.8))
pedestal = bpy.context.active_object
pedestal.name = "Marble_Pedestal"
pedestal.data.materials.append(marble_mat)
bpy.ops.object.shade_smooth()

# Carve Spacious Basin in Pedestal (radius 1.25)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.25, location=(0, 0, 0.75))
cutter = bpy.context.active_object
b_mod = pedestal.modifiers.new('Carve', 'BOOLEAN')
b_mod.object = cutter
b_mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = pedestal
bpy.ops.object.modifier_apply(modifier='Carve')
bpy.data.objects.remove(cutter, do_unlink=True)

# 24K Gold Rim around Pedestal
bpy.ops.mesh.primitive_torus_add(major_radius=1.95, minor_radius=0.065, location=(0, 0, 0.0))
rim = bpy.context.active_object
rim.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Side Marble Pillars with Collision
for x in [-1.25, 1.25]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.8, location=(x, 0, 0.9))
    p = bpy.context.active_object
    p.data.materials.append(marble_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(x, 0, 1.8))
    d = bpy.context.active_object
    d.data.materials.append(marble_mat)
    bpy.context.view_layer.objects.active = p
    p.select_set(True)
    d.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()
    make_collision_obstacle(p, thickness=0.005, friction=0.15)

# Add Collision to Pedestal
make_collision_obstacle(pedestal, thickness=0.005, damping=0.25, friction=0.15)

# Top Gold Dispenser Nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.6, location=(0, 0, 2.7))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Optical Glass Guiding Ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.72, minor_radius=0.08, location=(0, 0, 1.35))
glass_ring = bpy.context.active_object
glass_ring.data.materials.append(glass_mat)
bpy.ops.object.shade_smooth()

# Gold Brackets holding Glass Ring
for x in [-0.72, 0.72]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.55, location=(x, 0, 1.35))
    bracket = bpy.context.active_object
    bracket.rotation_euler = (0, math.pi/2, 0)
    bracket.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()

# ------------------------------------------------------------------------------
# 3. 3-STAGE CLOTH PRESSURE SOFT-BODY JELLY ACTORS (12.0s / 720 FRAMES)
# ------------------------------------------------------------------------------
# Helper to create cloth jelly actor with staggered start frame
def create_staggered_jelly(name, loc, start_f, end_f=720):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.40, location=loc, segments=40, ring_count=28)
    actor = bpy.context.active_object
    actor.name = name
    actor.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()

    cloth = make_cloth_pressure_actor(
        actor,
        mass=0.42,
        pressure=2.5,
        target_volume=1.0,
        tension=8.0,
        compression=8.0,
        shear=4.0,
        bending=0.05,
        damping=1.2
    )
    cloth.point_cache.frame_start = start_f
    cloth.point_cache.frame_end = end_f

    # Add Geometry Nodes organic surface ripple
    add_geometry_nodes_jiggle(actor, amplitude=0.008, frequency=8.0)
    # Smooth Subsurf for high-end optical sheen
    add_smooth_subsurf(actor, levels=1)
    return actor

# Drop 1: Starts at Frame 1 (center-left)
jelly1 = create_staggered_jelly("Jelly_Actor_1", (0.0, 0.0, 2.25), start_f=1)

# Drop 2: Starts at Frame 210 (slight lateral offset to land beside Jelly 1)
jelly2 = create_staggered_jelly("Jelly_Actor_2", (0.32, 0.0, 2.25), start_f=210)

# Drop 3: Starts at Frame 420 (center drop settling into cluster)
jelly3 = create_staggered_jelly("Jelly_Actor_3", (-0.22, 0.0, 2.25), start_f=420)

# ------------------------------------------------------------------------------
# 4. CINEMATIC CAMERA CHOREOGRAPHY ACROSS 12 SECONDS (FRAMES 1 TO 720)
# ------------------------------------------------------------------------------
bpy.ops.object.camera_add(location=(0, -5.3, 0.95), rotation=(math.radians(82.5), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 54

# Camera Keyframes without jumping scene frame:
# Frame 1: Hero establishing angle
cam.location = (0, -5.3, 0.95)
cam.keyframe_insert("location", frame=1)

# Frame 100: Glide down slightly tracking Jelly 1 settling
cam.location = (0, -5.0, 0.75)
cam.keyframe_insert("location", frame=100)

# Frame 210: Reset angle slightly upward for Jelly 2 entry
cam.location = (0, -5.1, 0.85)
cam.keyframe_insert("location", frame=210)

# Frame 350: Focus on twin squish dynamic
cam.location = (0, -4.8, 0.70)
cam.keyframe_insert("location", frame=350)

# Frame 420: Track 3rd drop arrival
cam.location = (0, -4.9, 0.80)
cam.keyframe_insert("location", frame=420)

# Frame 560: Push into intimate cluster shot
cam.location = (0, -4.5, 0.65)
cam.keyframe_insert("location", frame=560)

# Frame 720: Macro close-up & seamless loop return
cam.location = (0, -5.3, 0.95)
cam.keyframe_insert("location", frame=720)

scene.frame_set(1)

# 3-Point Luxury Studio Area Lights
bpy.ops.object.light_add(type='AREA', location=(3.2, -3.2, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 950
bpy.ops.object.light_add(type='AREA', location=(-3.2, -2.6, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 500
bpy.ops.object.light_add(type='AREA', location=(0, 2.6, 3.8), rotation=(math.radians(-36), 0, 0))
bpy.context.active_object.data.energy = 700

world = bpy.data.worlds.new('W_12s_60fps')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.76, 0.79, 0.83, 1.0)

# ------------------------------------------------------------------------------
# 5. PRODUCTION RENDER LOOP (720 FRAMES / 12.0s AT 60 FPS)
# ------------------------------------------------------------------------------
print("[*] Starting 12.0s (720 Frames) 60 FPS Cycles OptiX Production Render...")
for f in range(1, 721):
    scene.frame_set(f)
    frame_path = os.path.join(out_dir, f"frame_{f:04d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    if f % 30 == 0 or f == 1:
        print(f"[+] Rendered Frame {f:3d}/720 ({(f/720.0)*100:.1f}%) -> {os.path.basename(frame_path)}")

print("[SUCCESS] All 720 frames (12.0s) rendered at 60 FPS with Multi-Cloth Pressure Physics!")
