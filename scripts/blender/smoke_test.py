"""Exercise mesh creation, CPU rendering and .blend round trip in ignored tmp/."""
from pathlib import Path
import json
import os
import runpy
import tempfile

import bpy

root = Path(__file__).resolve().parents[2]
(root / "tmp").mkdir(exist_ok=True)
out = Path(tempfile.mkdtemp(prefix="blender-smoke-", dir=root / "tmp"))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add()
bpy.context.object.name = "SMOKE_cube"
bpy.ops.object.camera_add(location=(5, -5, 4))
cam = bpy.context.object
cam.rotation_euler = (-cam.location).to_track_quat("-Z", "Y").to_euler()
scene = bpy.context.scene
scene.camera = cam
bpy.ops.object.light_add(type="AREA", location=(2, -3, 5))
bpy.context.object.data.energy = 1000
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 4
scene.render.resolution_x = 128
scene.render.resolution_y = 128
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(out / "smoke.png")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out / "smoke.blend"))
scene.collection.children.link(bpy.data.collections.new("REFERENCE"))
runpy.run_path(str(root / "scripts/blender/10_massing.py"), run_name="__main__")
bpy.ops.wm.open_mainfile(filepath=str(out / "smoke.blend"))
assert "SMOKE_cube" in bpy.data.objects
expected_width = json.loads(os.environ["EKIRCHE_DIMENSIONS_JSON"])["hall_total_width"]["value"]
assert abs(bpy.data.objects["REF_hall_width"].dimensions.y - expected_width) < 1e-4
assert bpy.data.objects["REF_hall_width"].hide_render
assert (out / "smoke.png").stat().st_size > 0
print("BLENDER SMOKE OK:", out)
