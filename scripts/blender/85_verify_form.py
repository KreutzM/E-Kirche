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
