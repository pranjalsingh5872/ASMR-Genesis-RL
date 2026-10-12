import bpy
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from blender_physics_sim import make_collision_obstacle, make_cloth_pressure_actor

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 60
scene.frame_start = 1
scene.frame_end = 300

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.8, location=(0, 0, -0.4))
pedestal = bpy.context.active_object
make_collision_obstacle(pedestal, thickness=0.005, friction=0.15)

# Jelly 1: drops at frame 1
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(-0.4, 0, 2.0))
jelly1 = bpy.context.active_object
jelly1.name = "Jelly_1"
cloth1 = make_cloth_pressure_actor(jelly1, mass=0.4, pressure=2.5, bending=0.05)
cloth1.point_cache.frame_start = 1
cloth1.point_cache.frame_end = 300

# Jelly 2: drops at frame 120
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0.4, 0, 2.0))
jelly2 = bpy.context.active_object
jelly2.name = "Jelly_2"
cloth2 = make_cloth_pressure_actor(jelly2, mass=0.4, pressure=2.5, bending=0.05)
cloth2.point_cache.frame_start = 120
cloth2.point_cache.frame_end = 300

# Track positions across key frames
for f in [1, 35, 60, 119, 120, 155, 180]:
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    
    eval_1 = jelly1.evaluated_get(dg)
    m1 = eval_1.to_mesh()
    z1 = [v.co.z for v in m1.vertices]
    eval_1.to_mesh_clear()
    
    eval_2 = jelly2.evaluated_get(dg)
    m2 = eval_2.to_mesh()
    z2 = [v.co.z for v in m2.vertices]
    eval_2.to_mesh_clear()
    
    print(f"Frame {f:3d}: Jelly1 center_z={sum(z1)/len(z1):.3f} | Jelly2 center_z={sum(z2)/len(z2):.3f}")

print("[SUCCESS] Multi-cloth test executed cleanly!")
