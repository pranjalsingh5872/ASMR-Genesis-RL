import bpy
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 300  # 5.0 seconds at 60 FPS

# 1080x1920 9:16 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# Setup Cycles GPU OptiX
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
scene.cycles.samples = 28
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 12

out_dir = os.path.abspath("output/cloth_jelly_60fps_frames")
os.makedirs(out_dir, exist_ok=True)
scene.render.filepath = os.path.join(out_dir, "frame_")
scene.render.image_settings.file_format = 'PNG'

# ==============================================================================
# 1. LUXURY PBR MATERIALS
# ==============================================================================
# 100% Opaque Italian Verde Alpi Emerald Marble
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
    bsdf.inputs['Transmission Weight'].default_value = 0.0

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
    cr.color_ramp.elements[0].position = 0.22
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

# Pure 24K Mirror Gold
def create_24k_gold():
    mat = bpy.data.materials.new('24K_Gold')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.28, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.04
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

# ==============================================================================
# 2. STUDIO CYCLORAMA & ARCHITECTURAL PEDESTAL WITH COLLISION
# ==============================================================================
from blender_physics_sim import make_collision_obstacle, make_cloth_pressure_actor, add_geometry_nodes_jiggle, add_smooth_subsurf

# Studio Floor / Cyclorama Backdrop
bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 2.5, -2.8))
cyclorama = bpy.context.active_object
cyclorama.name = "Studio_Cyclorama"
bg_mat = bpy.data.materials.new("Backdrop")
bg_mat.use_nodes = True
bg_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (0.76, 0.79, 0.83, 1.0)
bg_mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.40
cyclorama.data.materials.append(bg_mat)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')
for v in cyclorama.data.vertices:
    if v.co.y > 0.5:
        dist = v.co.y - 0.5
        v.co.z += (dist ** 2) * 0.18
cyclorama.data.update()
bpy.ops.object.shade_smooth()

# Pedestal (Solid Marble)
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.4, location=(0, 0, -1.9))
base = bpy.context.active_object
base.name = "Marble_Pedestal"
base.data.materials.append(marble_mat)
bev = base.modifiers.new('Bevel', 'BEVEL')
bev.width = 0.04
bev.segments = 4
bpy.ops.object.shade_smooth()

# Carved Basin Funnel
bpy.ops.mesh.primitive_cone_add(radius1=0.72, radius2=0.04, depth=0.55, location=(0, 0, -0.65))
cutter = bpy.context.active_object
cutter.rotation_euler = (math.pi, 0, 0)
b_mod = base.modifiers.new('Carve', 'BOOLEAN')
b_mod.object = cutter
b_mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier='Carve')
bpy.data.objects.remove(cutter, do_unlink=True)

# Gold rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.065, location=(0, 0, -0.7))
rim = bpy.context.active_object
rim.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Marble Pillars with Collision
for x in [-1.05, 1.05]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=1.35, location=(x, 0, 0.08))
    p = bpy.context.active_object
    p.data.materials.append(marble_mat)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(x, 0, 0.75))
    d = bpy.context.active_object
    d.data.materials.append(marble_mat)
    bpy.context.view_layer.objects.active = p
    p.select_set(True)
    d.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()
    make_collision_obstacle(p, thickness=0.005, friction=0.15)

# Add Collision to Pedestal
make_collision_obstacle(base, thickness=0.005, friction=0.15)

# Top Gold Nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.23, depth=0.8, location=(0, 0, 2.5))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Curved Optical Glass Funnel Tube
c_data = bpy.data.curves.new('FunnelCurve', type='CURVE')
c_data.dimensions = '3D'
poly = c_data.splines.new('BEZIER')
poly.bezier_points.add(2)
poly.bezier_points[0].co = (0.0, 0.0, 1.62)
poly.bezier_points[0].handle_left = (0.0, 0.0, 1.85)
poly.bezier_points[0].handle_right = (0.0, 0.0, 1.30)
poly.bezier_points[1].co = (-0.19, 0.0, 0.95)
poly.bezier_points[1].handle_left = (-0.06, 0.0, 1.20)
poly.bezier_points[1].handle_right = (-0.38, 0.0, 0.70)
poly.bezier_points[2].co = (-0.48, 0.0, 0.52)
poly.bezier_points[2].handle_left = (-0.38, 0.0, 0.62)
poly.bezier_points[2].handle_right = (-0.58, 0.0, 0.42)

c_guide = bpy.data.objects.new('CurveGuide', c_data)
bpy.context.collection.objects.link(c_guide)

tube_data = c_data.copy()
tube_data.bevel_depth = 0.28
tube_data.bevel_resolution = 12
tube = bpy.data.objects.new('Tube', tube_data)
bpy.context.collection.objects.link(tube)
tube.data.materials.append(glass_mat)
bpy.context.view_layer.objects.active = tube
tube.select_set(True)
bpy.ops.object.convert(target='MESH')
bpy.ops.object.shade_smooth()
sol = tube.modifiers.new('Solidify', 'SOLIDIFY')
sol.thickness = 0.038
sol.offset = 1.0

# Add collision to tube
make_collision_obstacle(tube, thickness=0.005, friction=0.08)

# ==============================================================================
# 3. 60 FPS CLOTH PRESSURE SOFT-BODY JELLY SIMULATION
# ==============================================================================
# In-Tube Elastic Jelly Glide (Frames 1 to 140)
# Subdivided capsule
def create_subdivided_actor(name, r=0.175, h=0.45):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(0, 0, 50.0))
    body = bpy.context.active_object
    body.name = name

    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, 50.0 + h/2))
    top_cap = bpy.context.active_object

    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, 50.0 - h/2))
    bot_cap = bpy.context.active_object

    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    top_cap.select_set(True)
    bot_cap.select_set(True)
    bpy.ops.object.join()
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=12)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    body.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()
    return body

jelly_tube = create_subdivided_actor("Jelly_Tube_Actor", r=0.165, h=0.70)
c_mod = jelly_tube.modifiers.new('Curve', 'CURVE')
c_mod.object = c_guide
c_mod.deform_axis = 'POS_Z'

# Frame 0: Offscreen
scene.frame_set(0)
jelly_tube.location = (0, 0, 50.0)
jelly_tube.keyframe_insert("location", frame=0)

# Frames 1 to 140: Glides through glass tube with elastic stretching
for f in range(1, 141):
    scene.frame_set(f)
    t = (f - 1) / 139.0
    jelly_tube.location = (0, 0, -0.45 + 1.50 * t)
    stretch = 1.0 + 0.35 * math.sin(t * math.pi)
    jelly_tube.scale = (1.0 / math.sqrt(stretch), 1.0 / math.sqrt(stretch), stretch)
    jelly_tube.keyframe_insert("location", frame=f)
    jelly_tube.keyframe_insert("scale", frame=f)

scene.frame_set(141)
jelly_tube.location = (0, 0, 50.0)
jelly_tube.keyframe_insert("location", frame=141)

# --- CLOTH PRESSURE IMPACT & REBOUND ACTOR (Frames 138 to 300) ---
# High-density UV sphere for vertex-level organic squish
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(0, 0, 50.0), segments=40, ring_count=28)
jelly_impact = bpy.context.active_object
jelly_impact.name = "Jelly_Cloth_Pressure"
jelly_impact.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Cloth Pressure Modifier
cloth = make_cloth_pressure_actor(
    jelly_impact,
    mass=0.20,
    pressure=2.6,
    target_volume=1.0,
    tension=10.0,
    compression=10.0,
    bending=0.12,  # Ultra-soft jiggly silicone
    damping=1.8
)

# Geometry Nodes Organic Jiggle Resonance
add_geometry_nodes_jiggle(jelly_impact, amplitude=0.010, frequency=7.5)

# Subsurf for high-end optical sheen
add_smooth_subsurf(jelly_impact, levels=1)

# Initial Keyframe: inactive
scene.frame_set(137)
jelly_impact.location = (0, 0, 50.0)
jelly_impact.keyframe_insert("location", frame=137)

# Frames 138 to 300: Emerge from spout, free fall, collision impact with physical squish & harmonic rebound
# Dropping from tube exit mouth (-0.48, 0, 0.52) towards central basin (0, 0, -0.67)
for f in range(138, 301):
    scene.frame_set(f)
    if f < 175:
        # Freefall parabolic trajectory towards basin center
        t = (f - 138) / 36.0
        # Smooth arc: x moves from -0.48 to 0.0, z falls from 0.52 to -0.65
        x = -0.48 * (1.0 - t)
        z = 0.52 - 1.17 * (t ** 1.6)
        jelly_impact.location = (x, 0, z)
        # Slight aerodynamic elongation during fall
        jelly_impact.scale = (0.92, 0.92, 1.18)
    elif f < 192:
        # Physical Impact & Maximum Hydrostatic Squish (Compresses Z, bulges XY)
        t = (f - 175) / 16.0
        squish_depth = math.sin(t * math.pi) * 0.48
        jelly_impact.location = (0, 0, -0.65 - squish_depth * 0.12)
        # Volume-preserving hydrostatic bulging: S_xy * S_xy * S_z = 1.0
        sz = 1.0 - squish_depth
        sxy = math.sqrt(1.0 / max(0.1, sz))
        jelly_impact.scale = (sxy, sxy, sz)
    elif f < 225:
        # Elastic Rebound & Airborne Jiggle Oscillation
        t = (f - 192) / 32.0
        bounce_height = math.sin(t * math.pi) * 0.28
        jelly_impact.location = (0, 0, -0.65 + bounce_height)
        # Jelly wobble oscillation
        wobble = math.sin(t * 12.0) * 0.22 * math.exp(-t * 2.2)
        jelly_impact.scale = (1.0 - wobble, 1.0 - wobble, 1.0 + wobble * 1.8)
    else:
        # Settling Harmonic Ripples in Basin Cavity
        t = (f - 225) / 75.0
        decay = math.exp(-t * 3.5)
        ripple = decay * math.sin(t * 16.0) * 0.14
        jelly_impact.location = (0, 0, -0.67)
        jelly_impact.scale = (1.18 + ripple, 1.18 + ripple, 0.72 - ripple * 1.5)

    jelly_impact.keyframe_insert("location", frame=f)
    jelly_impact.keyframe_insert("scale", frame=f)

# ==============================================================================
# 4. CAMERA & CINEMATIC STUDIO LIGHTING
# ==============================================================================
bpy.ops.object.camera_add(location=(0, -6.1, 0.72), rotation=(math.radians(84.5), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 56

bpy.ops.object.light_add(type='AREA', location=(3.2, -3.6, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 900
bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.0, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 450
bpy.ops.object.light_add(type='AREA', location=(0, 2.8, 3.8), rotation=(math.radians(-38), 0, 0))
bpy.context.active_object.data.energy = 650

world = bpy.data.worlds.new('W_60fps')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.76, 0.79, 0.83, 1.0)

print("[*] 60 FPS Cloth Pressure & Geometry Nodes ASMR Scene Built Successfully!")
