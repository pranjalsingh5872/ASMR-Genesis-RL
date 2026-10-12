import bpy

import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
import test_squish_physics

for f in [1, 20, 35, 46, 60, 85]:
    test_squish_physics.scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    eval_j = test_squish_physics.jelly.evaluated_get(dg)
    mesh = eval_j.to_mesh()
    world_z = [(eval_j.matrix_world @ v.co).z for v in mesh.vertices]
    print(f"Squish Test Frame {f:3d}: Z = [{min(world_z):6.3f}, {max(world_z):6.3f}], center = {sum(world_z)/len(world_z):6.3f}")
    eval_j.to_mesh_clear()
