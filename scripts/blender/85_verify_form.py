"""Read-only regression checks on the PR-1 working scene."""
import json
import math
import bpy
import bmesh

scene=bpy.context.scene
a=json.loads(scene["model_inputs"])["assumptions"]["assumptions"]
objects=bpy.data.objects
assert scene.unit_settings.scale_length == 1
assert scene["axis_convention"] == "X east, Y north, Z up"
assert a["tower_buttress_width_base"]["value"] > a["buttress_width_base"]["value"]
assert len([o for o in objects if o.name.startswith("Sacristy_") and o.name.endswith(("_lower","_upper"))]) == 8
assert len([o for o in objects if o.name.startswith("Turret_lantern_")]) == 8
assert "Sacristy_connector_roof" in objects
assert not any(o.name.startswith("CUT_") for o in objects)
for label in ("north","south"):
    assert f"Tower_stage_band_{label}_main_ridge_z" not in objects, "Band would obstruct tall window"
    for face in ("west","outer","east","inner"):
        assert f"Tower_window_{label}_{face}_upper" in objects
    inward=-1 if label == "north" else 1
    assert f"Buttress_tower_{label}_-1_{inward}_y_base" not in objects
assert 2*(a["tower_center_y"]["value"]-a["tower_width"]["value"]/2-a["tower_buttress_width_base"]["value"]/2) > a["portal_width"]["value"]
for obj in objects:
    if obj.type != "MESH":
        continue
    assert all(math.isfinite(v) for vertex in obj.data.vertices for v in vertex.co)
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    assert all(edge.is_manifold for edge in bm.edges), obj.name
    assert abs(bm.calc_volume()) > 1e-8, obj.name
    bm.free()
    assert set(json.loads(obj["assumption_ids"])) <= set(a), obj.name
print("FORM REGRESSION CHECKS PASSED: windows, independent piers, closed volumes, parameter provenance")
if "tracery_radius" in a:
    assert len([o for o in objects if o.name.startswith("Gable_window_")]) == 8
    assert len([o for o in objects if o.name.startswith("Pinnacle_tip_")]) == 8
    assert "Portal_tympanum" in objects and "Clock_ring" in objects
    # Clock glazing must sit in front of the old closed roof end, not behind it.
    roof_front=a["tower_center_x"]["value"]-a["tower_depth"]["value"]/2
    assert max(v.co.x for v in objects["Clock_window"].data.vertices) < roof_front
    params={key:record["value"] for key,record in a.items()}
    inner_y=(params["conch_half_width"]+params["roof_overhang"])*(params["main_ridge_z"]-params["side_roof_ridge_z"])/(params["main_ridge_z"]-params["wall_eave_z"])
    for side in (-1,1):
        roof=objects[f"Aisle_roof_{side}_1"]
        assert abs(roof.data.vertices[4].co.y-side*inner_y) < 1e-5
    assert len(bpy.data.collections["TRACERY"].objects) > 100
    used={m for o in objects if o.type == "MESH" for m in o.data.materials}
    procedural=[m for m in used if m.get("external_files_required") is False]
    assert len(procedural) == 4
    for obj in objects:
        if obj.type == "MESH":
            uv=obj.data.uv_layers.get("MetricCourses")
            assert uv is not None, obj.name
            assert all(math.isfinite(v) for loop in uv.data for v in loop.uv), obj.name
    for mat in used:
        assert not any(n.type == "TEX_IMAGE" for n in mat.node_tree.nodes), mat.name
    print("TEXTURED EXTERIOR CHECKS PASSED: detail counts, metric UVs, four self-contained textures")
