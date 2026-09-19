"""Coarse massing scaffold.

Creates only documented scale guides. Astra should add architectural massing only after reading
AGENTS.md and recording inferred dimensions in data/assumptions.yaml.
"""
import bpy
import json
import os

dimensions = json.loads(os.environ["EKIRCHE_DIMENSIONS_JSON"])

def metres(name):
    record = dimensions[name]
    if record["unit"] != "m":
        raise ValueError(f"Expected metres: {name}")
    return record["value"]

def collection(name):
    return bpy.data.collections[name]

def guide_cube(name, size_xyz, location=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj=bpy.context.object
    obj.name=name
    obj.dimensions=size_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection("REFERENCE").objects.link(obj)
    obj.display_type="WIRE"
    obj.hide_render=True
    obj["evidence_status"]="documented scale guide; not architectural surface"
    return obj

crossing = metres("crossing_square_side")
width = metres("hall_total_width")
height = metres("tower_height")
# Guide line thickness/offsets are display settings, not building dimensions.
guide_cube("REF_crossing",(crossing,crossing,0.10),(0,0,0.05))
guide_cube("REF_hall_width",(0.10,width,0.10),(0,0,0.15))
guide_cube("REF_tower_height",(0.10,0.10,height),(0,0,height/2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print("Created documented scale guides only.")
