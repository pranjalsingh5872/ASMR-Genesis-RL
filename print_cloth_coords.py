import bpy

scene = bpy.context.scene
jelly = bpy.data.objects.get("Jelly_Soft_Actor")

for f in [1, 20, 40, 60, 80, 100, 150, 200, 250, 300]:
    scene.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    eval_jelly = jelly.evaluated_get(dg)
    mesh = eval_jelly.to_mesh()
    z_coords = [v.co.z for v in mesh.vertices]
    avg_z = sum(z_coords) / len(z_coords)
    min_z = min(z_coords)
    max_z = max(z_coords)
    print(f"Frame {f:3d}: Jelly bounds Z = [{min_z:.3f}, {max_z:.3f}], center_z = {avg_z:.3f}")
    eval_jelly.to_mesh_clear()
