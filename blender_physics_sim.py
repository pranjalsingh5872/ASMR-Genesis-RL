import os
import sys
import math
import bpy

# Ensure stdout handles UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def setup_physics_world(scene, gravity=(0.0, 0.0, -9.81)):
    """Sets up physical environment gravity."""
    scene.gravity = gravity
    print(f"[BlenderSim] Physics Environment Gravity set: g={gravity[2]} m/s^2")

def make_collision_obstacle(obj, thickness=0.005, damping=0.3, friction=0.15):
    """
    Configures an object as a physical obstacle for Cloth Pressure actors.
    Used for marble pedestals, pillars, and glass tubes.
    """
    col = obj.modifiers.get("Collision")
    if not col:
        col = obj.modifiers.new(name="Collision", type='COLLISION')
    col.settings.thickness_outer = thickness
    col.settings.damping = damping
    col.settings.cloth_friction = friction
    print(f"[BlenderSim] Collision Obstacle configured for '{obj.name}' (thickness={thickness}, friction={friction})")
    return col

def make_cloth_pressure_actor(
    obj,
    mass=0.25,
    pressure=2.8,
    target_volume=1.0,
    tension=12.0,
    compression=12.0,
    shear=6.0,
    bending=0.15,
    damping=2.0
):
    """
    Creates an ultra-realistic 3D soft-body jelly / silicone actor using Cloth Pressure.
    Unlike procedural scaling, this computes true vertex-level physics:
    - Internal hydrostatic pressure maintains inflation and organic shape.
    - Pressure volume conservation ensures physical volume is preserved.
    - Low bending stiffness allows squish, bulging, and jelly rebound.
    - Self-collision prevents mesh self-penetration.
    """
    bpy.context.view_layer.objects.active = obj
    
    # Ensure smooth shading
    bpy.ops.object.shade_smooth()
    
    cloth = obj.modifiers.get("ClothPressure")
    if not cloth:
        cloth = obj.modifiers.new(name="ClothPressure", type='CLOTH')
        
    cs = cloth.settings
    cs.quality = 6
    cs.mass = mass
    cs.air_damping = 0.4

    # Elasticity properties (Jelly / Silicone)
    cs.tension_stiffness = tension
    cs.compression_stiffness = compression
    cs.shear_stiffness = shear
    cs.bending_stiffness = bending  # Lower = softer and juicier jelly!

    # Damping properties
    cs.tension_damping = damping
    cs.compression_damping = damping
    cs.shear_damping = damping * 0.8
    cs.bending_damping = damping * 0.3

    # INTERNAL HYDROSTATIC PRESSURE & VOLUME CONSERVATION
    cs.use_pressure = True
    cs.uniform_pressure_force = pressure
    cs.use_pressure_volume = True
    cs.target_volume = target_volume
    cs.pressure_factor = 1.0

    # Collision & Self-Collision
    col = cloth.collision_settings
    col.use_collision = True
    col.distance_min = 0.008
    col.use_self_collision = True
    col.self_distance_min = 0.008

    print(f"[BlenderSim] Cloth Pressure Soft-Body configured for '{obj.name}': Pressure={pressure}, Mass={mass}kg, Bending={bending}")
    return cloth

def add_geometry_nodes_jiggle(obj, amplitude=0.012, frequency=8.0):
    """
    Adds a Geometry Nodes modifier to apply organic micro-jiggle surface resonance
    and dynamic contact relaxation on top of the physical cloth simulation.
    """
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.get("OrganicJellyGN")
    if not mod:
        mod = obj.modifiers.new(name="OrganicJellyGN", type='NODES')
    
    tree_name = f"GN_OrganicJelly_{obj.name}"
    tree = bpy.data.node_groups.get(tree_name)
    if not tree:
        tree = bpy.data.node_groups.new(tree_name, 'GeometryNodeTree')
        tree.interface.new_socket(name='Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
        tree.interface.new_socket(name='Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        
        in_node = tree.nodes.new('NodeGroupInput')
        in_node.location = (-300, 0)
        out_node = tree.nodes.new('NodeGroupOutput')
        out_node.location = (400, 0)
        
        # Set Position node for micro-displacement
        set_pos = tree.nodes.new('GeometryNodeSetPosition')
        set_pos.location = (100, 0)
        
        # Position input
        pos_node = tree.nodes.new('GeometryNodeInputPosition')
        pos_node.location = (-300, -200)
        
        # Normal input
        norm_node = tree.nodes.new('GeometryNodeInputNormal')
        norm_node.location = (-300, -350)
        
        # Noise Texture for subtle organic surface wave
        noise = tree.nodes.new('ShaderNodeTexNoise')
        noise.location = (-100, -200)
        noise.inputs['Scale'].default_value = frequency
        noise.inputs['Detail'].default_value = 2.0
        noise.inputs['Roughness'].default_value = 0.3
        tree.links.new(pos_node.outputs['Position'], noise.inputs['Vector'])
        
        # Math: Multiply noise by normal to get directional displacement
        scale_vec = tree.nodes.new('ShaderNodeVectorMath')
        scale_vec.operation = 'SCALE'
        scale_vec.location = (0, -300)
        scale_vec.inputs['Scale'].default_value = amplitude
        tree.links.new(norm_node.outputs['Normal'], scale_vec.inputs['Vector'])
        
        tree.links.new(in_node.outputs['Geometry'], set_pos.inputs['Geometry'])
        tree.links.new(scale_vec.outputs['Vector'], set_pos.inputs['Offset'])
        tree.links.new(set_pos.outputs['Geometry'], out_node.inputs['Geometry'])

    mod.node_group = tree
    print(f"[BlenderSim] Geometry Nodes Organic Resonance attached to '{obj.name}'")
    return mod

def add_smooth_subsurf(obj, levels=1):
    """Applies clean optical subdivision on top of physical simulation."""
    sub = obj.modifiers.get("Subsurf")
    if not sub:
        sub = obj.modifiers.new(name="Subsurf", type='SUBSURF')
    sub.levels = levels
    sub.render_levels = levels
    return sub

def evaluate_physics_range(scene, frame_start, frame_end, step_callback=None):
    """
    Deterministically evaluates physics frames step-by-step from start to end.
    Populates Blender point cache for headless rendering.
    """
    print(f"[*] Simulating physical frames {frame_start} to {frame_end}...")
    for f in range(frame_start, frame_end + 1):
        scene.frame_set(f)
        if step_callback:
            step_callback(f)
    print(f"[+] Physics simulation complete for all {frame_end - frame_start + 1} frames.")

# ==============================================================================
# STANDARDIZED 100% OPAQUE LUXURY PBR MATERIALS
# ==============================================================================
def create_opaque_verde_alpi():
    """100% Opaque Italian Verde Alpi Emerald Marble (Zero transmission/light bleed)."""
    mat = bpy.data.materials.new(name="Verde_Alpi_100Opaque")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['IOR'].default_value = 1.54
    bsdf.inputs['Transmission Weight'].default_value = 0.0

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = 2.4
    noise1.inputs['Detail'].default_value = 12.0
    noise1.inputs['Roughness'].default_value = 0.58
    noise1.inputs['Distortion'].default_value = 1.4
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])

    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.inputs['Scale'].default_value = 8.5
    noise2.inputs['Detail'].default_value = 8.0
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

def create_opaque_24k_gold():
    """100% Opaque 24K Bullion Gold (Zero transmission, rich solid metallic body)."""
    mat = bpy.data.materials.new('24K_Gold_100Opaque')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.76, 0.22, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.09
    bsdf.inputs['Transmission Weight'].default_value = 0.0
    return mat

def create_optical_glass():
    """Double-wall Optical Glass (Glass BSDF, IOR=1.492)."""
    mat = bpy.data.materials.new('Glass_Optical')
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
