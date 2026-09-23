"""Self-contained procedural textures. No downloaded/AI bitmap assets required.

Per-face metric UV projection avoids stretched courses on merged facade meshes.
All geometry/coordinates already use world metres with identity transforms.
"""
from mathutils import Vector

for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    uv=obj.data.uv_layers.new(name="MetricCourses")
    for face in obj.data.polygons:
        normal=face.normal
        # Horizontal course direction lies in each face. Up follows the slope.
        horizontal=Vector((0,0,1)).cross(normal)
        if horizontal.length < .001:
            horizontal=Vector((1,0,0))
        horizontal.normalize()
        vertical=normal.cross(horizontal).normalized()
        for loop_id in face.loop_indices:
            point=obj.data.vertices[obj.data.loops[loop_id].vertex_index].co
            uv.data[loop_id].uv=(point.dot(horizontal),point.dot(vertical))


def textured(mat,name,colors,width,height,joint,bump_distance,roughness):
    mat.name=name
    tree=mat.node_tree
    nodes,links=tree.nodes,tree.links
    nodes.clear()
    def node(kind,label):
        n=nodes.new(kind); n.label=label
        return n
    out=node("ShaderNodeOutputMaterial","Output")
    bsdf=node("ShaderNodeBsdfPrincipled","Opaque exterior surface")
    bsdf.inputs["Roughness"].default_value=roughness
    uv=node("ShaderNodeUVMap","Metric surface coordinates")
    uv.uv_map="MetricCourses"
    brick=node("ShaderNodeTexBrick","Staggered courses (visual approximation)")
    brick.inputs["Scale"].default_value=1
    brick.inputs["Brick Width"].default_value=width
    brick.inputs["Row Height"].default_value=height
    brick.inputs["Mortar Size"].default_value=joint
    brick.inputs["Mortar Smooth"].default_value=joint*.4
    brick.inputs["Color1"].default_value=(*colors[0],1)
    brick.inputs["Color2"].default_value=(*colors[1],1)
    brick.inputs["Mortar"].default_value=(*colors[2],1)
    links.new(uv.outputs["UV"],brick.inputs["Vector"])
    coord=node("ShaderNodeTexCoord","Object-space weathering")
    noise=node("ShaderNodeTexNoise","Broad subtle mineral variation")
    noise.inputs["Scale"].default_value=.7
    noise.inputs["Detail"].default_value=3
    links.new(coord.outputs["Object"],noise.inputs["Vector"])
    mix=node("ShaderNodeMixRGB","Weathering multiplied over courses")
    mix.blend_type="MULTIPLY"; mix.inputs[0].default_value=.24
    links.new(brick.outputs["Color"],mix.inputs[1]); links.new(noise.outputs["Color"],mix.inputs[2])
    links.new(mix.outputs[0],bsdf.inputs["Base Color"])
    bump=node("ShaderNodeBump","Recessed joints; shader only, not tactile")
    bump.invert=True; bump.inputs["Strength"].default_value=.35
    bump.inputs["Distance"].default_value=bump_distance
    links.new(brick.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    links.new(bsdf.outputs[0],out.inputs["Surface"])
    mat["provenance"]="Original procedural node recipe in scripts/blender/50_materials.py; visual approximation, no photographic pixels"
    mat["external_files_required"]=False

textured(stone,"Sandstone | warm ashlar + mineral variation",
         ((.40,.265,.175),(.245,.18,.135),(.22,.19,.155)),p("stone_block_width"),p("stone_course_height"),p("stone_joint_width"),.025,.84)
textured(slate,"Slate | staggered courses",
         ((.075,.105,.125),(.13,.16,.17),(.025,.032,.04)),p("slate_tile_width"),p("slate_course_height"),.006,.018,.64)
textured(glass,"Glazing | muted blue leaded panes (opaque exterior)",
         ((.07,.12,.15),(.12,.19,.22),(.025,.03,.035)),.35,.55,.008,.006,.28)
textured(door,"West doors | red painted timber",
         ((.23,.035,.018),(.34,.06,.025),(.055,.025,.016)),.28,8,.008,.012,.6)
scene=bpy.context.scene
scene["material_status"]="Procedural textured visual model; textures are shader detail, not tactile geometry"
scene["texture_provenance"]="Original node recipes; M12/M16/M17/M18/M19 used only as visual references. No external bitmap dependencies."
print("MATERIALS: metric UVs and four embedded procedural texture recipes",flush=True)
