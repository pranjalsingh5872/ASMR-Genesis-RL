import bpy
import math
import os

# Clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 780  # 26 seconds

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

os.makedirs("output/physics_scene1_frames", exist_ok=True)
scene.render.filepath = os.path.abspath("output/physics_scene1_frames/frame_")
scene.render.image_settings.file_format = 'PNG'

# ==============================================================================
# 1. 100% OPAQUE NATURAL VERDE ALPI MARBLE (Zero stripes, pure fractal stone)
# ==============================================================================
def create_luxury_verde_alpi():
    mat = bpy.data.materials.new(name="Verde_Alpi_Organic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    tc = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.4, 1.4, 1.4)
    links.new(tc.outputs['Object'], mapping.inputs['Vector'])

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 2.4
    noise1.inputs['Detail'].default_value = 14.0
    noise1.inputs['Roughness'].default_value = 0.58
    noise1.inputs['Distortion'].default_value = 2.5
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 6.8
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
    cr.color_ramp.elements[0].color = (0.015, 0.07, 0.035, 1.0) # Deep jade
    cr.color_ramp.elements[1].position = 0.58
    cr.color_ramp.elements[1].color = (0.06, 0.20, 0.11, 1.0)  # Polished emerald
    e3 = cr.color_ramp.elements.new(0.80)
    e3.color = (0.18, 0.42, 0.28, 1.0)                          # Sage mineral
    e4 = cr.color_ramp.elements.new(0.92)
    e4.color = (0.86, 0.90, 0.85, 1.0)                          # Calcite white vein
    links.new(mix.outputs[0], cr.inputs['Fac'])
    links.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    
    bsdf.inputs['Roughness'].default_value = 0.06
    bsdf.inputs['Metallic'].default_value = 0.0
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.0
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.0

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

# ==============================================================================
# 2. STUDIO CYCLORAMA & ARCHITECTURAL PEDESTAL WITH BEVELS
# ==============================================================================
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
    d.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.shade_smooth()

# Top Gold Nozzle
bpy.ops.mesh.primitive_cylinder_add(radius=0.23, depth=0.8, location=(0, 0, 2.5))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# ==============================================================================
# 3. CURVED GLASS TUBE & SPINE GUIDE
# ==============================================================================
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

# ==============================================================================
# 4. PHYSICAL ACTORS WITH ORGANIC CURVE DEFORMATION
# ==============================================================================
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
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    body.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()
    return body

# --- STAGE 0: 0% SOFT (Rigid Ricochet, Frames 1 - 60) ---
cap0 = create_subdivided_actor("Cap0", r=0.19, h=0.48)
for f in range(1, 61):
    scene.frame_set(f)
    if f < 22:
        t = (f - 1) / 21.0
        cap0.location = (0, 0, 2.45 - 1.15 * (t ** 1.8))
        cap0.rotation_euler = (0, 0, 0)
    elif f < 35:
        t = (f - 22) / 13.0
        cap0.location = (-1.05 * t, 0, 1.30 - 0.55 * t + 0.15 * math.sin(t * math.pi))
        cap0.rotation_euler = (t * 2.5, 0, t * 1.8)
    else:
        t = (f - 35) / 25.0
        cap0.location = (-1.05 - 2.4 * t, 0, 0.75 + 0.85 * math.sin(t * math.pi * 0.8) - 2.4 * t)
        cap0.rotation_euler = (2.5 + t * 6.0, 0, 1.8 + t * 4.5)
    cap0.scale = (1.0, 1.0, 1.0)
    cap0.keyframe_insert("location", frame=f)
    cap0.keyframe_insert("rotation_euler", frame=f)
    cap0.keyframe_insert("scale", frame=f)

scene.frame_set(61)
cap0.location = (0, 0, 50.0)
cap0.keyframe_insert("location", frame=61)

# --- STAGE 1: 25% SOFT (Stiff Rubber / Wedged Jam, Frames 61 - 150) ---
cap25 = create_subdivided_actor("Cap25", r=0.18, h=0.45)
c_mod25 = cap25.modifiers.new('Curve', 'CURVE')
c_mod25.object = c_guide
c_mod25.deform_axis = 'POS_Z'

scene.frame_set(60)
cap25.location = (0, 0, 50.0)
cap25.keyframe_insert("location", frame=60)

for f in range(61, 151):
    scene.frame_set(f)
    if f < 105:
        # Bends through the curve down to the wedging point
        t = (f - 61) / 44.0
        z_pos = -0.35 + 0.65 * (t ** 1.4)
        cap25.location = (0, 0, z_pos)
        cap25.scale = (1.0, 1.0, 1.0)
    elif f < 112:
        # Elastic compression on jam
        t = (f - 105) / 7.0
        sz = 1.0 - 0.18 * t
        sxy = math.sqrt(1.0 / sz)
        cap25.location = (0, 0, 0.30 + 0.03 * t)
        cap25.scale = (sxy, sxy, sz)
    else:
        # Decaying elastic vibration
        dt = (f - 112)
        decay = math.exp(-dt * 0.08)
        wobble = decay * math.sin(dt * 0.9) * 0.015
        cap25.location = (0, 0, 0.33 + wobble)
        cap25.scale = (1.10 + wobble*2, 1.10 + wobble*2, 0.82 - wobble*3)
    cap25.keyframe_insert("location", frame=f)
    cap25.keyframe_insert("scale", frame=f)

scene.frame_set(151)
cap25.location = (0, 0, 50.0)
cap25.keyframe_insert("location", frame=151)

# --- STAGE 2: 50% SOFT (Silicone Flex & Pillar Squish, Frames 151 - 360) ---
cap50_tube = create_subdivided_actor("Cap50_Tube", r=0.175, h=0.50)
c_mod50 = cap50_tube.modifiers.new('Curve', 'CURVE')
c_mod50.object = c_guide
c_mod50.deform_axis = 'POS_Z'

scene.frame_set(150)
cap50_tube.location = (0, 0, 50.0)
cap50_tube.keyframe_insert("location", frame=150)

for f in range(151, 231):
    scene.frame_set(f)
    t = (f - 151) / 80.0
    cap50_tube.location = (0, 0, -0.35 + 1.25 * t)
    cap50_tube.scale = (0.92, 0.92, 1.18)
    cap50_tube.keyframe_insert("location", frame=f)
    cap50_tube.keyframe_insert("scale", frame=f)

scene.frame_set(231)
cap50_tube.location = (0, 0, 50.0)
cap50_tube.keyframe_insert("location", frame=231)

# Exit actor
cap50_exit = create_subdivided_actor("Cap50_Exit", r=0.18, h=0.45)
scene.frame_set(229)
cap50_exit.location = (0, 0, 50.0)
cap50_exit.keyframe_insert("location", frame=229)

for f in range(230, 361):
    scene.frame_set(f)
    if f < 250:
        # Shoots to left pillar
        t = (f - 230) / 20.0
        cap50_exit.location = (-0.48 - 0.57 * t, 0, 0.48 - 0.18 * t)
        cap50_exit.rotation_euler = (0, -1.25 - 0.35 * t, 0)
        cap50_exit.scale = (1.0, 1.0, 1.0)
    elif f < 260:
        # Pancake squish against pillar at x=-1.05
        t = (f - 250) / 10.0
        squish = math.sin(t * math.pi) * 0.40
        cap50_exit.location = (-1.05 + 0.04 * t, 0, 0.30 - 0.05 * t)
        cap50_exit.rotation_euler = (0, -1.60, 0)
        cap50_exit.scale = (1.0 - squish, 1.0 + squish * 0.7, 1.0 + squish * 0.7)
    elif f < 290:
        # Rebound arc into central basin
        t = (f - 260) / 30.0
        cap50_exit.location = (-1.01 + 1.01 * t, 0, 0.25 + 0.30 * math.sin(t * math.pi) - 0.92 * t)
        cap50_exit.rotation_euler = (0, -1.60 * (1.0 - t), 0)
        cap50_exit.scale = (1.0, 1.0, 1.0)
    else:
        # Basin harmonic wobble
        t = (f - 290) / 70.0
        decay = math.exp(-t * 4.5)
        wobble = decay * math.sin(t * 18.0) * 0.24
        cap50_exit.location = (0, 0, -0.67)
        cap50_exit.rotation_euler = (0, 0, 0)
        cap50_exit.scale = (1.14 + wobble, 1.14 + wobble, 0.86 - wobble)
    cap50_exit.keyframe_insert("location", frame=f)
    cap50_exit.keyframe_insert("rotation_euler", frame=f)
    cap50_exit.keyframe_insert("scale", frame=f)

scene.frame_set(361)
cap50_exit.location = (0, 0, 50.0)
cap50_exit.keyframe_insert("location", frame=361)

# --- STAGE 3: 75% SOFT (Ultra-Stretchy Jelly Snake, Frames 361 - 660) ---
cap75_tube = create_subdivided_actor("Cap75_Tube", r=0.16, h=0.90)
c_mod75 = cap75_tube.modifiers.new('Curve', 'CURVE')
c_mod75.object = c_guide
c_mod75.deform_axis = 'POS_Z'

scene.frame_set(360)
cap75_tube.location = (0, 0, 50.0)
cap75_tube.keyframe_insert("location", frame=360)

for f in range(361, 481):
    scene.frame_set(f)
    t = (f - 361) / 120.0
    cap75_tube.location = (0, 0, -0.40 + 1.45 * t)
    stretch = 1.0 + 0.75 * math.sin(t * math.pi)
    cap75_tube.scale = (1.0 / math.sqrt(stretch), 1.0 / math.sqrt(stretch), stretch)
    cap75_tube.keyframe_insert("location", frame=f)
    cap75_tube.keyframe_insert("scale", frame=f)

scene.frame_set(481)
cap75_tube.location = (0, 0, 50.0)
cap75_tube.keyframe_insert("location", frame=481)

# Exit actor
cap75_exit = create_subdivided_actor("Cap75_Exit", r=0.18, h=0.65)
scene.frame_set(479)
cap75_exit.location = (0, 0, 50.0)
cap75_exit.keyframe_insert("location", frame=479)

for f in range(480, 661):
    scene.frame_set(f)
    if f < 525:
        t = (f - 480) / 45.0
        cap75_exit.location = (-0.48 + 0.48 * t - 0.22 * math.sin(t * math.pi), 0, 0.42 - 1.09 * t)
        cap75_exit.rotation_euler = (0, -1.25 * (1.0 - t), 0)
        cap75_exit.scale = (0.75 + 0.45 * t, 0.75 + 0.45 * t, 1.60 - 0.85 * t)
    else:
        t = (f - 525) / 135.0
        decay = math.exp(-t * 3.2)
        ripple = decay * math.sin(t * 14.0) * 0.28
        cap75_exit.location = (0, 0, -0.67)
        cap75_exit.rotation_euler = (0, 0, 0)
        cap75_exit.scale = (1.30 + ripple, 1.30 + ripple, 0.70 - ripple)
    cap75_exit.keyframe_insert("location", frame=f)
    cap75_exit.keyframe_insert("rotation_euler", frame=f)
    cap75_exit.keyframe_insert("scale", frame=f)

scene.frame_set(661)
cap75_exit.location = (0, 0, 50.0)
cap75_exit.keyframe_insert("location", frame=661)

# --- STAGE 4: 100% SOFT (Molten Liquid Gold Stream & Puddle, Frames 661 - 780) ---
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

cap100_stream = create_subdivided_actor("Cap100_Stream", r=0.13, h=1.4)
c_mod100 = cap100_stream.modifiers.new('Curve', 'CURVE')
c_mod100.object = c_flow
c_mod100.deform_axis = 'POS_Z'

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, 0, 50.0))
pool = bpy.context.active_object
pool.name = "Liquid_Pool_Actor"
pool.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()
sub_pool = pool.modifiers.new('Subsurf', 'SUBSURF')
sub_pool.levels = 1

scene.frame_set(660)
cap100_stream.location = (0, 0, 50.0)
cap100_stream.keyframe_insert("location", frame=660)
pool.location = (0, 0, 50.0)
pool.keyframe_insert("location", frame=660)

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
        pool.location = (0, 0, -0.71)
        pool.scale = (sx, sy, sz)
    else:
        t = (f - 742) / 38.0
        decay = math.exp(-t * 2.8)
        ripple = decay * math.sin(t * 15.0) * 0.025
        pool.location = (0, 0, -0.71)
        pool.scale = (1.02 + ripple, 1.02 + ripple, 0.12 - ripple * 0.5)
    pool.keyframe_insert("location", frame=f)
    pool.keyframe_insert("scale", frame=f)

# ==============================================================================
# 5. CAMERA & CINEMATIC STUDIO LIGHTING
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

world = bpy.data.worlds.new('W')
world.use_nodes = True
scene.world = world
world.node_tree.nodes.get('Background').inputs['Color'].default_value = (0.76, 0.79, 0.83, 1.0)

print("[*] Master Scene 1 ready to render all 780 frames.")
