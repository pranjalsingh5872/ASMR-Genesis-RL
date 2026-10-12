import bpy
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from test_full_cloth_sim import scene, pedestal, jelly

for f in range(1, 100):
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    eval_jelly = jelly.evaluated_get(dg)
    mesh = eval_jelly.to_mesh()
    world_z = [(eval_jelly.matrix_world @ v.co).z for v in mesh.vertices]
    min_z = min(world_z)
    max_z = max(world_z)
    center_z = sum(world_z) / len(world_z)
    eval_jelly.to_mesh_clear()
    if f in [1, 10, 20, 30, 35, 40, 45, 50, 60, 70, 80, 90]:
        print(f"Frame {f:3d}: Z = [{min_z:6.3f}, {max_z:6.3f}], center={center_z:6.3f}")
