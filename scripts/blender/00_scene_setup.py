from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT/"blender"/"scene"/"elisabethkirche.blend"
if SCENE.exists():
    raise RuntimeError("Refusing to overwrite an existing working scene")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene=bpy.context.scene
scene.unit_settings.system="METRIC"
scene.unit_settings.length_unit="METERS"
scene.unit_settings.scale_length=1.0

for name in ["MASSING","TOWERS","ROOFS","BUTTRESSES","OPENINGS","TRACERY","DETAIL","CAMERAS","REFERENCE"]:
    if name not in bpy.data.collections:
        col=bpy.data.collections.new(name)
        scene.collection.children.link(col)

scene["project"]="Elisabethkirche Marburg exterior reconstruction"
scene["axis_convention"]="X east, Y north, Z up"
scene["origin_definition"]="centre of crossing at nominal floor level"

SCENE.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SCENE))
print("Saved",SCENE)
