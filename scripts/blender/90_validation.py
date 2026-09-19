from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"validation"/"renders"
OUT.mkdir(parents=True,exist_ok=True)

scene=bpy.context.scene
scene.render.resolution_x=1600
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"

cams=[o for o in bpy.data.objects if o.type=="CAMERA" and o.name.startswith("VAL_")]
if not cams:
    raise RuntimeError("No validation cameras named VAL_* exist. Solve/create cameras before rendering.")

for cam in sorted(cams,key=lambda o:o.name):
    scene.camera=cam
    scene.render.filepath=str(OUT/f"{cam.name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered",cam.name)
