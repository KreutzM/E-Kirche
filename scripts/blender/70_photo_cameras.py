"""Import explicit camera hypotheses and verify projection against solver pixels."""
import json
import math
import os
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

report = json.loads(Path(os.environ["EKIRCHE_CAMERAS"]).read_text(encoding="utf-8"))
out = Path(os.environ["EKIRCHE_OUTPUT"])
if out.exists():
    raise RuntimeError(f"Refusing to overwrite {out}")
scene = bpy.context.scene
scene["iteration"] = os.environ.get("EKIRCHE_ITERATION", "phase_a_002")
scene["camera_calibration_status"] = report["projection"]
for name, spec in report["views"].items():
    c = spec["camera"]
    yaw,pitch,roll = c[3:6]
    forward = Vector((math.cos(pitch)*math.cos(yaw), math.cos(pitch)*math.sin(yaw), math.sin(pitch)))
    right = Vector((math.sin(yaw),-math.cos(yaw),0))
    up = right.cross(forward)
    r = math.cos(roll)*right+math.sin(roll)*up
    u = -math.sin(roll)*right+math.cos(roll)*up
    rotation = Matrix((r,u,-forward)).transposed()
    data = bpy.data.cameras.new("VAL_"+name)
    data.type = "PERSP"
    data.sensor_fit = "HORIZONTAL"
    data.sensor_width = 36  # arbitrary parameterization; not a claimed sensor measurement
    w,h = spec["image_size"]
    data.lens = c[6]*36/w
    data.shift_x = -c[7]/w
    data.shift_y = c[8]/w
    data.clip_end = 1000
    obj = bpy.data.objects.new("VAL_"+name,data)
    bpy.data.collections["CAMERAS"].objects.link(obj)
    obj.location = c[:3]
    obj.rotation_euler = rotation.to_euler()
    obj["image_width"], obj["image_height"] = w,h
    obj["evidence_id"] = name
    obj["calibration_status"] = spec["status"]
    obj["fit_rmse_px"], obj["check_rmse_px"] = spec["fit_rmse_px"], spec["check_rmse_px"]
    scene.render.resolution_x, scene.render.resolution_y = w,h
    scene.render.resolution_percentage = 100
    bpy.context.view_layer.update()
    for point in spec["points"]:
        projected = world_to_camera_view(scene,obj,Vector(point["xyz"]))
        actual = Vector((projected.x*w,(1-projected.y)*h))
        expected = Vector(point["projected_uv"])
        assert (actual-expected).length < 0.05, (name,point["name"],actual,expected)
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
scene["camera_solution_json"] = json.dumps(report)
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print("CAMERA PROJECTION VERIFIED",out)
