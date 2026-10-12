import bpy
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from blender_physics_sim import make_collision_obstacle, make_cloth_pressure_actor, add_geometry_nodes_jiggle, add_smooth_subsurf

# 1. Clean factory slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 300  # 5.0 seconds at 60 FPS

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
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 12

out_dir = os.path.abspath("output/cloth_jelly_60fps_frames")
os.makedirs(out_dir, exist_ok=True)
scene.render.image_settings.file_format = 'PNG'

# ------------------------------------------------------------------------------
# 2. LUXURY PBR MATERIALS
# ------------------------------------------------------------------------------
# Italian Verde Alpi Emerald Marble
def create_verde_alpi():
    mat = bpy.data.materials.new(name="Verde_Alpi_Organic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['IOR'].default_value = 1.54

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 2.4
    noise1.inputs['Detail'].default_value = 14.0
    noise1.inputs['Roughness'].default_value = 0.58
    noise1.inputs['Distortion'].default_value = 1.4
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 8.5
    noise2.inputs['Detail'].default_value = 10.0
    noise2.inputs['Roughness'].default_value = 0.5
    noise2.inputs['Distortion'].default_value = 1.8
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])

    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.65
    links.new(noise1.outputs['Fac'], mix.inputs[2])
    links.new(noise2.outputs['Fac'], mix.inputs[3])

    cr = nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.interpolation = 'EASE'
    cr.color_ramp.elements[0].position = 0.20
    cr.color_ramp.elements[0].color = (0.015, 0.07, 0.035, 1.0)
    cr.color_ramp.elements[1].position = 0.58
    cr.color_ramp.elements[1].color = (0.06, 0.20, 0.11, 1.0)
    e3 = cr.color_ramp.elements.new(0.80)
    e3.color = (0.10, 0.35, 0.18, 1.0)
    e4 = cr.color_ramp.elements.new(0.96)
    e4.color = (0.75, 0.88, 0.80, 1.0)
    links.new(mix.outputs[0], cr.inputs['Fac'])
    links.new(cr.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.015
    links.new(mix.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# 100% Opaque 24K Heavy Bullion Gold (Zero Transmission, Solid Opaque Core)
def create_24k_gold():
    mat = bpy.data.materials.new('24K_Gold_Opaque')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.76, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.09
    bsdf.inputs['Transmission Weight'].default_value = 0.0
    return mat

# Double-wall Optical Glass
def create_optical_glass():
    mat = bpy.data.materials.new('Glass')
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfGlass')
    bsdf.inputs['Color'].default_value = (0.99, 1.0, 0.99, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.001
    bsdf.inputs['IOR'].default_value = 1.492
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

marble_mat = create_verde_alpi()
gold_mat = create_24k_gold()
glass_mat = create_optical_glass()

# ------------------------------------------------------------------------------
# 3. ARCHITECTURAL PEDESTAL & STUDIO ENVIRONMENT
# ------------------------------------------------------------------------------
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

# Pedestal (Solid Marble with Carved Basin)
bpy.ops.mesh.primitive_cylinder_add(radius=1.85, depth=1.6, location=(0, 0, -0.8))
pedestal = bpy.context.active_object
pedestal.name = "Marble_Pedestal"
pedestal.data.materials.append(marble_mat)
bpy.ops.object.shade_smooth()

# Carve Basin in Pedestal
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.05, location=(0, 0, 0.65))
cutter = bpy.context.active_object
b_mod = pedestal.modifiers.new('Carve', 'BOOLEAN')
b_mod.object = cutter
b_mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = pedestal
bpy.ops.object.modifier_apply(modifier='Carve')
bpy.data.objects.remove(cutter, do_unlink=True)

# Gold Rim around Pedestal
bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.065, location=(0, 0, 0.0))
rim = bpy.context.active_object
rim.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Side Marble Pillars
for x in [-1.15, 1.15]:
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
bpy.ops.mesh.primitive_cylinder_add(radius=0.26, depth=0.6, location=(0, 0, 2.7))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Optical Glass Guiding Ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.65, minor_radius=0.08, location=(0, 0, 1.35))
glass_ring = bpy.context.active_object
glass_ring.data.materials.append(glass_mat)
bpy.ops.object.shade_smooth()

# Gold Brackets holding Glass Ring
for x in [-0.65, 0.65]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.5, location=(x, 0, 1.35))
    bracket = bpy.context.active_object
    bracket.rotation_euler = (0, math.pi/2, 0)
    bracket.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()

# ------------------------------------------------------------------------------
# 4. 100% PURE CLOTH PRESSURE SOFT-BODY JELLY ACTOR
# ------------------------------------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(0, 0, 2.25), segments=42, ring_count=30)
jelly = bpy.context.active_object
jelly.name = "Jelly_Soft_Actor"
jelly.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Cloth Pressure with viral squishy ASMR settings
cloth = make_cloth_pressure_actor(
    jelly,
    mass=0.42,            # Organic momentum
    pressure=2.5,         # Hydrostatic internal pressure
    target_volume=1.0,
    tension=8.0,          # Allows organic elastic stretching
    compression=8.0,
    shear=4.0,
    bending=0.05,         # Ultra soft bending for juicy folds and pancake bulging
    damping=1.2
)

# Geometry nodes micro-surface jiggle resonance
add_geometry_nodes_jiggle(jelly, amplitude=0.008, frequency=8.0)

# Subsurf for mirror-smooth OptiX reflections
add_smooth_subsurf(jelly, levels=1)

# ------------------------------------------------------------------------------
# 5. CAMERA & CINEMATIC LIGHTING
# ------------------------------------------------------------------------------
bpy.ops.object.camera_add(location=(0, -5.3, 0.95), rotation=(math.radians(82.5), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 54

# Camera keyframing WITHOUT jumping scene frame:
cam.location = (0, -5.3, 0.95)
cam.keyframe_insert("location", frame=1)
cam.location = (0, -5.0, 0.75)
cam.keyframe_insert("location", frame=85)
cam.location = (0, -4.6, 0.65)
cam.keyframe_insert("location", frame=300)

# Ensure scene is at frame 1 before simulation
scene.frame_set(1)

# 3-Point Luxury Studio Area Lights
bpy.ops.object.light_add(type='AREA', location=(3.2, -3.2, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 950
bpy.ops.object.light_add(type='AREA', location=(-3.2, -2.6, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 500
bpy.ops.object.light_add(type='AREA', location=(0, 2.6, 3.8), rotation=(math.radians(-36), 0, 0))
bpy.context.active_object.data.energy = 700

world = bpy.data.worlds.new('W_Cinematic_60fps')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.76, 0.79, 0.83, 1.0)

# ------------------------------------------------------------------------------
# 6. SEQUENTIAL RENDER LOOP (FRAMES 1 TO 300)
# ------------------------------------------------------------------------------
print("[*] Starting Full 60 FPS Cycles OptiX Production Render (300 frames)...")
for f in range(1, 301):
    scene.frame_set(f)
    frame_path = os.path.join(out_dir, f"frame_{f:04d}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    if f % 15 == 0 or f == 1:
        print(f"[+] Rendered Frame {f:3d}/300 ({(f/300.0)*100:.1f}%) -> {os.path.basename(frame_path)}")

print("[SUCCESS] All 300 frames rendered at 60 FPS with Cloth Pressure Physics!")
