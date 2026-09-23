"""Presentation only: temporary studio floor/lights/cameras, never save over model."""
import math
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
out=ROOT/"validation/renders"/scene["iteration"]
out.mkdir(parents=True,exist_ok=True)
scene.render.use_stamp=False
scene.render.film_transparent=False
scene.render.resolution_x=1600
scene.render.resolution_y=1400
scene.render.resolution_percentage=100
scene.cycles.samples=64
scene.cycles.use_denoising=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.48,.53,.60,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.7
sun=bpy.data.objects["Inspection_sun"]
sun.rotation_euler=(math.radians(30),math.radians(-20),math.radians(-40))
sun.data.energy=3
sun.data.angle=math.radians(12)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.08))
floor=bpy.context.object
floor.name="PRESENTATION_ONLY_floor"
mat=bpy.data.materials.new("PRESENTATION_ONLY_ground")
mat.diffuse_color=(.27,.29,.31,1)
mat.use_nodes=True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=(.27,.29,.31,1)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value=.95
floor.data.materials.append(mat)
views={"PRESENT_SE":((85,-120,78),(-12,0,37),120),
       "PRESENT_W":((-120,-75,62),(-15,0,37),113),
       "DETAIL_CHOIR":((38,-65,28),(0,-17,13),28),
       "DETAIL_PORTAL":((-82,-5,18),(-46,0,16),37)}
for name,(position,target,scale) in views.items():
    data=bpy.data.cameras.new(name); data.type="ORTHO"; data.ortho_scale=scale
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    scene.camera=obj
    scene.render.filepath=str(out/f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("PRESENTATION",name,flush=True)
