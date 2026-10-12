import bpy
import math
import os

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Create scene and engine
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for d in prefs.devices:
    d.use = True
scene.cycles.samples = 16
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920

# Create material
def create_24k_gold():
    mat = bpy.data.materials.new("PureGold_24K")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (1.00, 0.76, 0.18, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.08
    return mat

gold_mat = create_24k_gold()

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.4, location=(0, 0, -1.9))
base = bpy.context.active_object

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

# Pillars
for x in [-1.05, 1.05]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=1.35, location=(x, 0, 0.08))
    p = bpy.context.active_object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(x, 0, 0.75))
    d = bpy.context.active_object
    bpy.context.view_layer.objects.active = p
    d.select_set(True)
    bpy.ops.object.join()

# Glass tube curve
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
bpy.context.view_layer.objects.active = tube
tube.select_set(True)
bpy.ops.object.convert(target='MESH')
sol = tube.modifiers.new('Solidify', 'SOLIDIFY')
sol.thickness = 0.038
sol.offset = 1.0

# 100% Flow Curve (Smooth continuous curve from nozzle to basin)
flow_data = bpy.data.curves.new('Flow100Curve', type='CURVE')
flow_data.dimensions = '3D'
fpoly = flow_data.splines.new('BEZIER')
fpoly.bezier_points.add(4) # 5 points total (indices 0, 1, 2, 3, 4)

# Pt 0: Top entrance
fpoly.bezier_points[0].co = (0.0, 0.0, 1.62)
fpoly.bezier_points[0].handle_left = (0.0, 0.0, 1.85)
fpoly.bezier_points[0].handle_right = (0.0, 0.0, 1.30)

# Pt 1: Inside tube bend
fpoly.bezier_points[1].co = (-0.19, 0.0, 0.95)
fpoly.bezier_points[1].handle_left = (-0.06, 0.0, 1.20)
fpoly.bezier_points[1].handle_right = (-0.38, 0.0, 0.70)

# Pt 2: Tube exit mouth
fpoly.bezier_points[2].co = (-0.48, 0.0, 0.52)
fpoly.bezier_points[2].handle_left = (-0.38, 0.0, 0.62)
fpoly.bezier_points[2].handle_right = (-0.48, 0.0, 0.25)

# Pt 3: Parabolic pouring waterfall arc
fpoly.bezier_points[3].co = (-0.28, 0.0, -0.15)
fpoly.bezier_points[3].handle_left = (-0.40, 0.0, 0.05)
fpoly.bezier_points[3].handle_right = (-0.14, 0.0, -0.42)

# Pt 4: Basin landing
fpoly.bezier_points[4].co = (0.0, 0.0, -0.67)
fpoly.bezier_points[4].handle_left = (-0.08, 0.0, -0.62)
fpoly.bezier_points[4].handle_right = (0.0, 0.0, -0.67)

c_flow = bpy.data.objects.new('CurveFlow100', flow_data)
bpy.context.collection.objects.link(c_flow)

# Create stream actor
def create_stream_actor(name, r=0.13, h=1.4):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = name
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, h/2))
    top_cap = bpy.context.active_object
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(0, 0, -h/2))
    bot_cap = bpy.context.active_object
    bpy.context.view_layer.objects.active = body
    top_cap.select_set(True)
    bot_cap.select_set(True)
    bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=14)
    bpy.ops.object.mode_set(mode='OBJECT')
    body.data.materials.append(gold_mat)
    bpy.ops.object.shade_smooth()
    return body

stream = create_stream_actor("GoldStream", r=0.13, h=1.4)
mod = stream.modifiers.new('FlowCurve', 'CURVE')
mod.object = c_flow
mod.deform_axis = 'POS_Z'

# Pool actor in basin
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.72, location=(0, 0, -0.67))
pool = bpy.context.active_object
pool.name = "GoldPool"
pool.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()
sub_pool = pool.modifiers.new('Subsurf', 'SUBSURF')
sub_pool.levels = 1

# Camera & lighting
bpy.ops.object.camera_add(location=(0, -6.1, 0.72), rotation=(math.radians(84.5), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 56
bpy.ops.object.light_add(type='AREA', location=(3.2, -3.6, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
bpy.context.active_object.data.energy = 900
bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.0, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
bpy.context.active_object.data.energy = 450

# Animation keyframing for Stage 4 (frames 661 - 780)
# Frame 660: inactive
scene.frame_set(660)
stream.location = (0, 0, 50.0)
stream.keyframe_insert("location", frame=660)
pool.location = (0, 0, 50.0)
pool.keyframe_insert("location", frame=660)

# Frames 661 - 740: stream flow along the full curve
for f in range(661, 745):
    scene.frame_set(f)
    t = (f - 661) / 80.0
    # Stream moves along Z from -0.6 to 2.4 along the curve
    stream.location = (0, 0, -0.6 + 3.0 * t)
    if f < 715:
        # Before landing in basin, full stream
        stream.scale = (0.9, 0.9, 1.2)
    else:
        # After frame 715, stream drains down into pool
        drain = (f - 715) / 29.0
        stream.scale = (0.9 * (1.0 - drain*0.5), 0.9 * (1.0 - drain*0.5), 1.2 * (1.0 - drain*0.8))
    stream.keyframe_insert("location", frame=f)
    stream.keyframe_insert("scale", frame=f)

scene.frame_set(745)
stream.location = (0, 0, 50.0)
stream.keyframe_insert("location", frame=745)

# Pool keyframing: starts at frame 712, expands and settles
scene.frame_set(712)
pool.location = (0, 0, 50.0)
pool.keyframe_insert("location", frame=712)

for f in range(713, 781):
    scene.frame_set(f)
    if f < 738:
        t = (f - 713) / 25.0
        # Smoothly expands in XY from 0.1 to 0.72 (fits basin perfectly)
        sx = 0.1 + 0.62 * (t ** 0.8)
        sy = sx
        sz = 0.08 + 0.08 * math.sin(t * math.pi)
        pool.location = (0, 0, -0.68 + 0.02 * t)
        pool.scale = (sx, sy, sz)
    else:
        t = (f - 738) / 42.0
        decay = math.exp(-t * 3.0)
        ripple = decay * math.sin(t * 16.0) * 0.03
        pool.location = (0, 0, -0.66)
        pool.scale = (0.72 + ripple, 0.72 + ripple, 0.06 - ripple * 0.4)
    pool.keyframe_insert("location", frame=f)
    pool.keyframe_insert("scale", frame=f)

# Render test frames to verify: 675, 700, 715, 730, 760
test_frames = [675, 700, 715, 730, 760]
for tf in test_frames:
    scene.frame_set(tf)
    scene.render.filepath = f"output/test_stage4/test_frame_{tf}.jpg"
    bpy.ops.render.render(write_still=True)
    print(f"Rendered test frame {tf}")
