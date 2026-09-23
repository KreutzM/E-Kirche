"""Render fixed diagnostic cameras; these are not photo-calibrated VAL views."""
from pathlib import Path
import json
import os

import bpy

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
settings=json.loads(os.environ["EKIRCHE_INSPECTION_JSON"])
scene.render.resolution_x,scene.render.resolution_y=settings["resolution"]
scene.render.resolution_percentage=100
scene.render.film_transparent=False
out = ROOT / "validation/renders" / scene.get("iteration", "unversioned")
out.mkdir(parents=True, exist_ok=True)
cameras = sorted((o for o in scene.objects if o.type == "CAMERA" and o.name.startswith("INSPECT_")), key=lambda o: o.name)
if not cameras:
    raise RuntimeError("No INSPECT_* cameras in this scene")
scene.render.use_stamp = True
scene.render.use_stamp_note = True
scene.render.stamp_note_text = "PHASE A / PROVISIONAL ENVELOPE / SYNTHETIC VIEW - NOT PHOTO CALIBRATED"
scene.render.use_stamp_date = False
scene.render.use_stamp_time = False
scene.render.use_stamp_frame = False
scene.render.use_stamp_filename = False
scene.render.use_stamp_camera = True
scene.render.stamp_font_size = 14
for camera in cameras:
    scene.camera = camera
    scene.render.filepath = str(out / f"{camera.name}.png")
    bpy.ops.render.render(write_still=True)
    print("INSPECTION RENDER", scene.render.filepath, flush=True)
