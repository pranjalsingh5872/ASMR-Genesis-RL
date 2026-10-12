import bpy
import math
import os

# Clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
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
scene.cycles.samples = 28
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12
scene.cycles.transparent_max_bounces = 12

out_dir = os.path.abspath("output/test_stage4_realistic")
os.makedirs(out_dir, exist_ok=True)

# 1. MATERIALS
def create_luxury_verde_alpi():
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
    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 2.4
    noise1.inputs['Detail'].default_value = 14.0
    noise1.inputs['Roughness'].default_value = 0.58
    noise1.inputs['Distortion'].default_value = 1.2
    links.new(tex_coord.outputs['Object'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 8.5
    noise2.inputs['Detail'].default_value = 8.0
    noise2.inputs['Roughness'].default_value = 0.70
    links.new(tex_coord.outputs['Object'], noise2.inputs['Vector'])

    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'FLOAT'
    mix.inputs['Factor'].default_value = 0.40
    links.new(noise1.outputs['Fac'], mix.inputs[2])
    links.new(noise2.outputs['Fac'], mix.inputs[3])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'EASE'
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.008, 0.045, 0.022, 1.0)
    ramp.color_ramp.elements.new(0.50)
    ramp.color_ramp.elements[1].color = (0.022, 0.125, 0.065, 1.0)
    ramp.color_ramp.elements.new(0.74)
    ramp.color_ramp.elements[2].color = (0.055, 0.245, 0.145, 1.0)
    ramp.color_ramp.elements[3].position = 0.95
    ramp.color_ramp.elements[3].color = (0.75, 0.88, 0.80, 1.0)
    links.new(mix.outputs[0], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.015
    links.new(mix.outputs[0], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_24k_gold():
    mat = bpy.data.materials.new('24K_Gold')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.78, 0.28, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.04
    return mat

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

marble_mat = create_luxury_verde_alpi()
gold_mat = create_24k_gold()
glass_mat = create_optical_glass()

# 2. STUDIO CYCLORAMA & PEDESTAL
bpy.ops.mesh.primitive_plane_add(size=16.0, location=(0, 2.5, -2.8))
cyclorama = bpy.context.active_object
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

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.4, location=(0, 0, -1.9))
base = bpy.context.active_object
base.data.materials.append(marble_mat)
bev = base.modifiers.new('Bevel', 'BEVEL')
bev.width = 0.04
bev.segments = 4
bpy.ops.object.shade_smooth()

# Basin funnel
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

# Pillars
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

# Top Gold Nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.23, depth=0.8, location=(0, 0, 2.5))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Glass Tube
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

# 100% Flow Guide Curve (Continuous smooth flow from top nozzle down into basin center)
flow_data = bpy.data.curves.new('Flow100Curve', type='CURVE')
flow_data.dimensions = '3D'
fpoly = flow_data.splines.new('BEZIER')
fpoly.bezier_points.add(4)  # 5 control points (0 to 4)

fpoly.bezier_points[0].co = (0.0, 0.0, 1.62)
fpoly.bezier_points[0].handle_left = (0.0, 0.0, 1.85)
fpoly.bezier_points[0].handle_right = (0.0, 0.0, 1.30)

fpoly.bezier_points[1].co = (-0.19, 0.0, 0.95)
fpoly.bezier_points[1].handle_left = (-0.06, 0.0, 1.20)
fpoly.bezier_points[1].handle_right = (-0.38, 0.0, 0.70)

fpoly.bezier_points[2].co = (-0.48, 0.0, 0.52)
fpoly.bezier_points[2].handle_left = (-0.38, 0.0, 0.62)
fpoly.bezier_points[2].handle_right = (-0.48, 0.0, 0.25)

fpoly.bezier_points[3].co = (-0.28, 0.0, -0.15)
fpoly.bezier_points[3].handle_left = (-0.40, 0.0, 0.05)
fpoly.bezier_points[3].handle_right = (-0.14, 0.0, -0.42)

fpoly.bezier_points[4].co = (0.0, 0.0, -0.67)
fpoly.bezier_points[4].handle_left = (-0.08, 0.0, -0.62)
fpoly.bezier_points[4].handle_right = (0.0, 0.0, -0.67)

c_flow = bpy.data.objects.new('CurveFlow100', flow_data)
bpy.context.collection.objects.link(c_flow)

# Create Subdivided Actor
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

# Stream Actor
cap100_stream = create_subdivided_actor("Cap100_Stream", r=0.13, h=1.4)
c_mod100 = cap100_stream.modifiers.new('Curve', 'CURVE')
c_mod100.object = c_flow
c_mod100.deform_axis = 'POS_Z'

# Pool Actor: A smooth fluid dome inside the basin
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 50.0))
pool = bpy.context.active_object
pool.name = "Liquid_Pool_Actor"
pool.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()
sub_pool = pool.modifiers.new('Subsurf', 'SUBSURF')
sub_pool.levels = 1

# Camera & Cinematic Studio Lighting
bpy.ops.object.camera_add(location=(0, -6.1, 0.72), rotation=(math.radians(84.5), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 56

bpy.ops.object.light_add(type='AREA', location=(3.2, -3.6, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 900
bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.0, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 450
bpy.ops.object.light_add(type='AREA', location=(0, 2.8, 3.8), rotation=(math.radians(-38), 0, 0))
bpy.context.active_object.data.energy = 650

world = bpy.data.worlds.new('W')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.76, 0.79, 0.83, 1.0)

# ANIMATION
scene.frame_set(660)
cap100_stream.location = (0, 0, 50.0)
cap100_stream.keyframe_insert("location", frame=660)
pool.location = (0, 0, 50.0)
pool.keyframe_insert("location", frame=660)

# Stream flow from 661 to 745
for f in range(661, 746):
    scene.frame_set(f)
    t = (f - 661) / 80.0
    cap100_stream.location = (0, 0, -0.60 + 3.10 * t)
    if f < 715:
        cap100_stream.scale = (0.88, 0.88, 1.25)
    else:
        drain = (f - 715) / 29.0
        cap100_stream.scale = (0.88 * (1.0 - drain * 0.4), 0.88 * (1.0 - drain * 0.4), 1.25 * (1.0 - drain * 0.85))
    cap100_stream.keyframe_insert("location", frame=f)
    cap100_stream.keyframe_insert("scale", frame=f)

scene.frame_set(746)
cap100_stream.location = (0, 0, 50.0)
cap100_stream.keyframe_insert("location", frame=746)

# Pool expansion & ripple resonance from frame 714 to 780
scene.frame_set(713)
pool.location = (0, 0, 50.0)
pool.keyframe_insert("location", frame=713)

for f in range(714, 781):
    scene.frame_set(f)
    if f < 742:
        t = (f - 714) / 28.0
        sx = 0.08 + 0.95 * (t ** 0.82)
        sy = sx
        sz = 0.10 + 0.14 * math.sin(t * math.pi * 0.9)
        pool.location = (0, 0, -0.69)
        pool.scale = (sx, sy, sz)
    else:
        t = (f - 742) / 38.0
        decay = math.exp(-t * 2.8)
        ripple = decay * math.sin(t * 15.0) * 0.025
        pool.location = (0, 0, -0.69)
        pool.scale = (1.02 + ripple, 1.02 + ripple, 0.12 - ripple * 0.5)
    pool.keyframe_insert("location", frame=f)
    pool.keyframe_insert("scale", frame=f)

# Render verification frames: 675, 700, 718, 735, 765
test_frames = [675, 700, 718, 735, 765]
for tf in test_frames:
    scene.frame_set(tf)
    scene.render.filepath = os.path.join(out_dir, f"realistic_frame_{tf}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[+] Rendered realistic test frame: {tf}")
