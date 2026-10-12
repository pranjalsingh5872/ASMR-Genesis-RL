import bpy
import math
import os

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 1  # Single frame test for quality validation

# 1080x1920 9:16 Vertical HD
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100

# -------------------------------------------------------------
# 1. Enable Cycles with NVIDIA RTX 4060 OptiX Ray Tracing
# -------------------------------------------------------------
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
scene.cycles.samples = 128          # High sample count for glass caustics
scene.cycles.use_denoising = True   # OptiX AI Denoiser
scene.cycles.denoiser = 'OPTIX'
scene.cycles.max_bounces = 12       # Essential for multi-bounce optical glass refraction
scene.cycles.transmission_bounces = 12

os.makedirs("output/cycles_test", exist_ok=True)
scene.render.filepath = os.path.abspath("output/cycles_test/cycles_quality_benchmark.png")
scene.render.image_settings.file_format = 'PNG'

# -------------------------------------------------------------
# 2. Photorealistic Shading (Green Veined Marble, Optical Glass, Pure Gold)
# -------------------------------------------------------------
def create_photoreal_glass():
    mat = bpy.data.materials.new(name="Photoreal_Glass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfGlass")
    bsdf.inputs["Color"].default_value = (0.97, 0.99, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.005 # crystal polished
    bsdf.inputs["IOR"].default_value = 1.48        # realistic optical glass index

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def create_photoreal_gold():
    mat = bpy.data.materials.new(name="Photoreal_Gold")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.766, 0.336, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.08  # Mirror-like polished metal
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def create_photoreal_green_marble():
    mat = bpy.data.materials.new(name="Photoreal_Green_Marble")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    ramp = nodes.new("ShaderNodeValToRGB")

    noise.inputs["Scale"].default_value = 3.8
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.65

    # Sage marble body to deep dark green veins
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = (0.80, 0.86, 0.82, 1.0) # Polished sage marble
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.08, 0.22, 0.14, 1.0) # Deep vein mineral

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.12 # High gloss polish
    # Subsurface scattering gives marble physical depth
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.15
        bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.9, 0.8)
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.15

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

mat_glass = create_photoreal_glass()
mat_gold = create_photoreal_gold()
mat_marble = create_photoreal_green_marble()

# -------------------------------------------------------------
# 3. Geometry with Physical Wall Thickness & Bevels
# -------------------------------------------------------------
# Pedestal Base
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=2.0, location=(0, 0, -1.8))
pedestal = bpy.context.active_object
pedestal.data.materials.append(mat_marble)
ped_bevel = pedestal.modifiers.new("Bevel", 'BEVEL')
ped_bevel.width = 0.04
ped_bevel.segments = 4

# Gold Rim
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.06, location=(0, 0, -0.8))
rim = bpy.context.active_object
rim.data.materials.append(mat_gold)

# Dual Pillars with Beveled Caps
for x_pos in [-1.15, 1.15]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.6, location=(x_pos, 0, 0.0))
    p = bpy.context.active_object
    p.data.materials.append(mat_marble)
    p_b = p.modifiers.new("Bevel", 'BEVEL')
    p_b.width = 0.03
    p_b.segments = 3

# Top Gold Dropper
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.6, location=(0, 0, 2.7))
top_nozzle = bpy.context.active_object
top_nozzle.data.materials.append(mat_gold)

# Curved Glass Tube WITH PHYSICAL WALL THICKNESS
c_data = bpy.data.curves.new('GlassTube', type='CURVE')
c_data.dimensions = '3D'
poly = c_data.splines.new('BEZIER')
poly.bezier_points.add(2)

poly.bezier_points[0].co = (0.0, 0.0, 1.8)
poly.bezier_points[0].handle_left = (0.0, 0.0, 2.1)
poly.bezier_points[0].handle_right = (0.0, 0.0, 1.4)

poly.bezier_points[1].co = (-0.25, 0.0, 0.8)
poly.bezier_points[1].handle_left = (-0.1, 0.0, 1.1)
poly.bezier_points[1].handle_right = (-0.45, 0.0, 0.5)

poly.bezier_points[2].co = (-0.6, 0.0, 0.35)
poly.bezier_points[2].handle_left = (-0.5, 0.0, 0.45)
poly.bezier_points[2].handle_right = (-0.75, 0.0, 0.2)

c_data.bevel_depth = 0.32
c_data.bevel_resolution = 6
tube = bpy.data.objects.new('Curved_Glass_Tube', c_data)
bpy.context.collection.objects.link(tube)
tube.data.materials.append(mat_glass)

# Convert curve to mesh to apply Solidify modifier (giving it realistic glass wall thickness)
bpy.context.view_layer.objects.active = tube
tube.select_set(True)
bpy.ops.object.convert(target='MESH')
solid = tube.modifiers.new("GlassThickness", 'SOLIDIFY')
solid.thickness = 0.04  # 4cm physical glass wall thickness
sub_tube = tube.modifiers.new("Subsurf", 'SUBSURF')
sub_tube.levels = 1

# Gold Capsule falling midway into glass tube (showing real refraction through the glass)
bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.7, location=(-0.15, 0, 1.1))
capsule = bpy.context.active_object
capsule.rotation_euler = (0, 0, -0.4)
capsule.data.materials.append(mat_gold)
cap_sub = capsule.modifiers.new("Subsurf", 'SUBSURF')
cap_sub.levels = 2
cap_bev = capsule.modifiers.new("Bevel", 'BEVEL')
cap_bev.width = 0.05
cap_bev.segments = 4

# -------------------------------------------------------------
# 4. Studio Lighting & High-Dynamic-Range Environment
# -------------------------------------------------------------
bpy.ops.object.camera_add(location=(0, -6.8, 0.8), rotation=(math.radians(84), 0, 0))
cam = bpy.context.active_object
scene.camera = cam
cam.data.lens = 52

# Key Area Light (Diffused Studio Softbox)
bpy.ops.object.light_add(type='AREA', location=(3.5, -4.0, 4.5), rotation=(math.radians(45), 0, math.radians(30)))
key = bpy.context.active_object
key.data.energy = 850
key.data.size = 2.8

# Fill Light (Cool Cyan Bounce)
bpy.ops.object.light_add(type='AREA', location=(-3.5, -3.5, 3.0), rotation=(math.radians(45), 0, math.radians(-30)))
fill = bpy.context.active_object
fill.data.energy = 450
fill.data.size = 3.2

# Rim Light (Accent highlight on glass & gold edges)
bpy.ops.object.light_add(type='AREA', location=(0, 3.0, 3.2), rotation=(math.radians(-45), 0, 0))
rim = bpy.context.active_object
rim.data.energy = 550
rim.data.size = 2.0
rim.data.color = (1.0, 0.95, 0.85)

# Background Color
world = bpy.data.worlds.new("CyclesWorld")
world.use_nodes = True
scene.world = world
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.73, 0.77, 0.84, 1.0)
    bg.inputs["Strength"].default_value = 1.0

print("[*] Starting Cycles Raytraced GPU Render...")
bpy.ops.render.render(write_still=True)
print("[+] Cycles benchmark render complete: output/cycles_test/cycles_quality_benchmark.png")
