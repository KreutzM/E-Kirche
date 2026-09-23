"""Bake shared procedural material swatches and export the exterior as a self-contained GLB.

This script changes only Blender's in-memory copy of the scene. The source .blend
and its procedural shaders remain the authoritative working artifact.
"""
import os
from pathlib import Path
import tempfile

import bpy


output = Path(os.environ["EKIRCHE_OUTPUT"])
if output.suffix.lower() != ".glb":
    raise ValueError("Web export destination must end in .glb")
if output.resolve() == Path(bpy.data.filepath).resolve():
    raise ValueError("Refusing to overwrite the Blender scene")

mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not mesh_objects:
    raise RuntimeError("No building meshes in the scene")
materials = {mat for obj in mesh_objects for mat in obj.data.materials if mat}
procedural = sorted((mat for mat in materials if mat.get("external_files_required") is False), key=lambda mat: mat.name)
if len(procedural) != 4:
    raise RuntimeError(f"Expected four procedural exterior materials, found {len(procedural)}")

tile_size_m = 4.0
resolution = 1024
bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.device = "CPU"
bpy.context.scene.cycles.samples = 8
bpy.context.scene.render.bake.use_selected_to_active = False
bpy.context.scene.render.bake.use_pass_direct = False
bpy.context.scene.render.bake.use_pass_indirect = False
bpy.context.scene.render.bake.use_pass_color = True
bpy.context.scene.render.bake.margin = 8

# A shared four-metre swatch keeps the GLB small. Existing MetricCourses UVs are
# expressed in metres and can repeat this image across every building surface.
quad = bpy.data.meshes.new("WEB_EXPORT_swatch")
quad.from_pydata([(0, 0, 0), (tile_size_m, 0, 0),
                  (tile_size_m, tile_size_m, 0), (0, tile_size_m, 0)], [], [(0, 1, 2, 3)])
quad.update()
uv = quad.uv_layers.new(name="MetricCourses")
for loop in quad.polygons[0].loop_indices:
    vert = quad.vertices[quad.loops[loop].vertex_index].co
    uv.data[loop].uv = (vert.x, vert.y)
bake_uv = quad.uv_layers.new(name="BakeUV")
for loop in quad.polygons[0].loop_indices:
    vert = quad.vertices[quad.loops[loop].vertex_index].co
    bake_uv.data[loop].uv = (vert.x / tile_size_m, vert.y / tile_size_m)
bake_uv.active = True
bake_uv.active_render = True
swatch = bpy.data.objects.new("WEB_EXPORT_swatch", quad)
bpy.context.scene.collection.objects.link(swatch)

with tempfile.TemporaryDirectory(prefix="ekirche_web_") as temp:
    baked = {}
    for index, mat in enumerate(procedural):
        swatch.data.materials.clear()
        swatch.data.materials.append(mat)
        image = bpy.data.images.new(f"web_{index}_color", width=resolution, height=resolution, alpha=False)
        image.filepath_raw = str(Path(temp) / f"web_{index}_color.png")
        image.file_format = "PNG"
        target = mat.node_tree.nodes.new("ShaderNodeTexImage")
        target.image = image
        mat.node_tree.nodes.active = target
        bpy.ops.object.select_all(action="DESELECT")
        swatch.select_set(True)
        bpy.context.view_layer.objects.active = swatch
        bpy.ops.object.bake(type="DIFFUSE")
        image.save()
        baked[mat] = image
        mat.node_tree.nodes.remove(target)
        print(f"WEB BAKE: {mat.name} -> {image.filepath_raw}", flush=True)

    bpy.data.objects.remove(swatch, do_unlink=True)
    for obj in mesh_objects:
        uv = obj.data.uv_layers.get("MetricCourses")
        if uv is None:
            raise RuntimeError(f"Missing MetricCourses UV on {obj.name}")
        uv.active = True
        uv.active_render = True
        for loop in uv.data:
            loop.uv /= tile_size_m

    for mat, image in baked.items():
        tree = mat.node_tree
        tree.nodes.clear()
        texture = tree.nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Linear"
        shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Roughness"].default_value = 0.82 if "Sandstone" in mat.name else 0.65
        output_node = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        tree.links.new(shader.outputs["BSDF"], output_node.inputs["Surface"])

    # The working scene has many small, independently named architectural parts.
    # Joining pieces with the same material reduces browser draw calls sharply.
    for mat in sorted(materials, key=lambda item: item.name):
        group = [obj for obj in bpy.context.scene.objects
                 if obj.type == "MESH" and len(obj.data.materials) == 1 and obj.data.materials[0] == mat]
        if len(group) < 2:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for obj in group:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = group[0]
        bpy.ops.object.join()
        group[0].name = f"WEB_{mat.name.split(' | ')[0]}"

    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(output), export_format="GLB", use_selection=True,
                              export_yup=True, export_texcoords=True, export_materials="EXPORT")

print(f"WEB EXPORT OK: {output} ({output.stat().st_size:,} bytes, {len(mesh_objects)} meshes)", flush=True)
