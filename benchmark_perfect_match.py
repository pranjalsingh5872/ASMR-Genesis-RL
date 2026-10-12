import bpy
import math
import os

bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# Cycles OptiX GPU Setup
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
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12
scene.cycles.transmission_bounces = 12

os.makedirs("output/cycles_test", exist_ok=True)
scene.render.filepath = os.path.abspath("output/cycles_test/perfect_match_benchmark.png")
scene.render.image_settings.file_format = 'PNG'

# -------------------------------------------------------------
# 1. Procedural Fine-Veined Green Marble (Exact Match)
# -------------------------------------------------------------
def create_veined_marble():
    mat = bpy.data.materials.new(name="Green_Veined_Marble_Exact")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    # Texture coordinate & mapping
    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.5, 2.5, 4.0)
    links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # Wave + Voronoi + Noise for realistic cracked marble veins
    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.feature = 'F1'
    voronoi.distance = 'EUCLIDEAN'
    voronoi.inputs["Scale"].default_value = 4.2

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 10.0
    noise.inputs["Distortion"].default_value = 1.8

    mix = nodes.new("ShaderNodeMix")
    mix.data_type = 'FLOAT'
    mix.inputs["Factor"].default_value = 0.5
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])
    links.new(voronoi.outputs["Distance"], mix.inputs[2])
    links.new(noise.outputs["Fac"], mix.inputs[3])

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.28
    color_ramp.color_ramp.elements[0].color = (0.78, 0.82, 0.79, 1.0) # Light sage marble base
    color_ramp.color_ramp.elements[1].position = 0.55
    color_ramp.color_ramp.elements[1].color = (0.22, 0.35, 0.28, 1.0) # Distinct green mineral vein

    links.new(mix.outputs[0], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.15 # High gloss polish

    # Subsurface depth
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.12
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.12

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def create_pure_gold():
    mat = bpy.data.materials.new(name="Pure_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.72, 0.24, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.06
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def create_crystal_glass():
    mat = bpy.data.materials.new(name="Crystal_Glass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfGlass")
    bsdf.inputs["Color"].default_value = (0.98, 0.99, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.002
    bsdf.inputs["IOR"].default_value = 1.50 # Real optical soda-lime glass
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

marble = create_veined_marble()
gold = create_pure_gold()
glass = create_crystal_glass()

# -------------------------------------------------------------
# 2. Geometry: Pedestal with Central Funnel Basin & Rounded Pillars
# -------------------------------------------------------------
# Pedestal base
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.4, location=(0, 0, -1.9))
base = bpy.context.active_object
base.data.materials.append(marble)

# Funnel depression cut in pedestal top
bpy.ops.mesh.primitive_cone_add(radius1=0.75, radius2=0.05, depth=0.6, location=(0, 0, -0.6))
cone_cutter = bpy.context.active_object
cone_cutter.rotation_euler = (math.pi, 0, 0)
bpy.ops.object.modifier_add(type='BOOLEAN')
bool_mod = base.modifiers.new("FunnelCut", 'BOOLEAN')
bool_mod.object = cone_cutter
bool_mod.operation = 'DIFFERENCE'
bpy.context.view_layer.objects.active = base
bpy.ops.object.modifier_apply(modifier="FunnelCut")
bpy.data.objects.remove(cone_cutter, do_unlink=True)

# Gold rim trim along the top edge of the pedestal
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.06, location=(0, 0, -0.7))
rim = bpy.context.active_object
rim.data.materials.append(gold)

# Fully rounded marble pillars (capsule tops matching reference image)
for x_pos in [-1.05, 1.05]:
    # Cylinder pillar base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=1.3, location=(x_pos, 0, 0.1))
    p_body = bpy.context.active_object
    p_body.data.materials.append(marble)
    # Dome cap
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.19, location=(x_pos, 0, 0.75))
    p_dome = bpy.context.active_object
    p_dome.data.materials.append(marble)

# Golden Dropper Nozzle at the very top (framed exactly as reference)
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.8, location=(0, 0, 2.5))
nozzle = bpy.context.active_object
nozzle.data.materials.append(gold)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 2.1))
nozzle_tip = bpy.context.active_object
nozzle_tip.data.materials.append(gold)

# -------------------------------------------------------------
# 3. Elevated Curved Glass Tube with Physical Wall Thickness
# -------------------------------------------------------------
c_data = bpy.data.curves.new('Ref_Tube', type='CURVE')
c_data.dimensions = '3D'
poly = c_data.splines.new('BEZIER')
poly.bezier_points.add(2)

# Point 0: Top entrance
poly.bezier_points[0].co = (0.0, 0.0, 1.55)
poly.bezier_points[0].handle_left = (0.0, 0.0, 1.8)
poly.bezier_points[0].handle_right = (0.0, 0.0, 1.25)

# Point 1: Curve mid
poly.bezier_points[1].co = (-0.18, 0.0, 0.85)
poly.bezier_points[1].handle_left = (-0.05, 0.0, 1.1)
poly.bezier_points[1].handle_right = (-0.35, 0.0, 0.6)

# Point 2: Bottom exit angled towards left pillar
poly.bezier_points[2].co = (-0.45, 0.0, 0.45)
poly.bezier_points[2].handle_left = (-0.35, 0.0, 0.55)
poly.bezier_points[2].handle_right = (-0.55, 0.0, 0.35)

c_data.bevel_depth = 0.28
c_data.bevel_resolution = 6
tube = bpy.data.objects.new('Curved_Glass_Funnel', c_data)
bpy.context.collection.objects.link(tube)
tube.data.materials.append(glass)

# Convert to mesh & apply Solidify for true physical glass refraction
bpy.context.view_layer.objects.active = tube
tube.select_set(True)
bpy.ops.object.convert(target='MESH')
solid = tube.modifiers.new("GlassThickness", 'SOLIDIFY')
solid.thickness = 0.035
sub = tube.modifiers.new("Subsurf", 'SUBSURF')
sub.levels = 1

# -------------------------------------------------------------
# 4. Camera & Vignetted Studio Lighting Setup
# -------------------------------------------------------------
# Camera framed to match sample thumbnail perspective
bpy.ops.object.camera_add(location=(0, -6.6, 0.65), rotation=(math.radians(85), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 54

# Soft Key Light (Studio Softbox from upper right)
bpy.ops.object.light_add(type='AREA', location=(3.2, -3.8, 4.2), rotation=(math.radians(45), 0, math.radians(28)))
key = bpy.context.active_object
key.data.energy = 750
key.data.size = 2.6

# Fill Light (Cool ambient soft light from left)
bpy.ops.object.light_add(type='AREA', location=(-3.2, -3.2, 2.8), rotation=(math.radians(45), 0, math.radians(-30)))
fill = bpy.context.active_object
fill.data.energy = 380
fill.data.size = 3.0

# Warm Rim Light (Glints on gold trim & glass wall highlights)
bpy.ops.object.light_add(type='AREA', location=(0, 2.5, 3.5), rotation=(math.radians(-40), 0, 0))
rim = bpy.context.active_object
rim.data.energy = 500
rim.data.size = 2.2
rim.data.color = (1.0, 0.94, 0.85)

# Studio Background Gradient
world = bpy.data.worlds.new("VignetteStudio")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.68, 0.73, 0.82, 1.0)
    bg.inputs["Strength"].default_value = 0.95

print("[*] Rendering exact matched benchmark frame...")
bpy.ops.render.render(write_still=True)
print("[+] Perfect match render complete!")
