"""Phase A: parametric exterior envelope, deliberately without fine architecture."""
import json
import math
import os
import runpy
from pathlib import Path

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
payload = json.loads(os.environ["EKIRCHE_MODEL_JSON"])
A = payload["assumptions"]["assumptions"]
D = payload["dimensions"]
iteration = os.environ.get("EKIRCHE_ITERATION", "phase_a_002")
out = Path(os.environ["EKIRCHE_OUTPUT"])
if out.exists():
    raise RuntimeError(f"Refusing to overwrite working artifact: {out}")


def p(name):
    return A[name]["value"]


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    return mat


stone = material("Clay sandstone (display only)", (0.48, 0.39, 0.28))
slate = material("Clay slate (display only)", (0.12, 0.16, 0.20))


def mesh(name, verts, faces, group, mat, keys):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    bpy.data.collections[group].objects.link(obj)
    obj.data.materials.append(mat)
    obj["iteration"] = iteration
    obj["evidence_status"] = "inferred coarse exterior envelope; not surveyed"
    obj["assumption_ids"] = json.dumps(keys)
    return obj


def prism(name, polygon, top, group="MASSING", mat=stone, keys=(), bottom=0):
    count = len(polygon)
    verts = [(x, y, bottom) for x, y in polygon] + [(x, y, top) for x, y in polygon]
    faces = [tuple(reversed(range(count))), tuple(range(count, 2 * count))]
    faces += [(i, (i + 1) % count, (i + 1) % count + count, i + count) for i in range(count)]
    return mesh(name, verts, faces, group, mat, keys)


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rotate(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(c*x-s*y, s*x+c*y) for x, y in points]


def roof(name, polygon, apexes, faces, keys):
    verts = [(x, y, p("wall_eave_z")) for x, y in polygon] + apexes
    return mesh(name, verts, [tuple(reversed(range(len(polygon))))] + faces, "ROOFS", slate, keys)


def gable(name, x0, x1, half, base, ridge, mat=slate, group="ROOFS", angle=0, offset=(0, 0), keys=()):
    xy = rotate([(x0, -half), (x1, -half), (x1, half), (x0, half), (x0, 0), (x1, 0)], angle)
    verts = [(x+offset[0], y+offset[1], base if i < 4 else ridge) for i, (x, y) in enumerate(xy)]
    faces = [(3, 2, 1, 0), (0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5)]
    return mesh(name, verts, faces, group, mat, keys)


def cone(name, xy, radius, base, top, mat, group, keys):
    ring = [(xy[0]+radius*math.cos(i*math.tau/8+math.pi/8), xy[1]+radius*math.sin(i*math.tau/8+math.pi/8)) for i in range(8)]
    verts = [(x, y, base) for x, y in ring] + [(xy[0], xy[1], top)]
    return mesh(name, verts, [tuple(reversed(range(8)))] + [(i, (i+1)%8, 8) for i in range(8)], group, mat, keys)


# Start from factory startup and keep the project collections explicit.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for old in list(bpy.data.collections):
    bpy.data.collections.remove(old)
for name in ("MASSING", "TOWERS", "ROOFS", "BUTTRESSES", "OPENINGS", "TRACERY", "DETAIL", "CAMERAS", "REFERENCE"):
    bpy.context.scene.collection.children.link(bpy.data.collections.new(name))
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1
scene["axis_convention"] = "X east, Y north, Z up"
scene["origin_definition"] = "centre of crossing at nominal floor level"
scene["iteration"] = iteration
scene["validation_status"] = "PROVISIONAL: inspection cameras only; photographic calibration pending"
scene["model_inputs"] = json.dumps(payload, ensure_ascii=False)

w, h, shoulder = p("nave_half_width"), p("conch_half_width"), p("conch_shoulder")
eave = p("wall_eave_z")
footprints = {}
main_parts = []
poly = rect(p("nave_west_x"), p("nave_east_x"), -w, w)
footprints["nave"] = poly
main_parts.append(prism("Nave_envelope", poly, eave, keys=["nave_west_x", "nave_east_x", "nave_half_width", "wall_eave_z"]))
# Includes the crossing so the three arms form one continuous exterior shell.
for name, angle in (("east", 0), ("north", math.pi/2), ("south", -math.pi/2)):
    arc = [(shoulder+h*math.cos(-math.pi/2+i*math.pi/p("conch_facets")), h*math.sin(-math.pi/2+i*math.pi/p("conch_facets"))) for i in range(int(p("conch_facets"))+1)]
    local = [(-h, -h)] + arc + [(-h, h)]
    poly = rotate(local, angle)
    footprints[name] = poly
    main_parts.append(prism("Conch_"+name, poly, eave, keys=["conch_half_width", "conch_shoulder", "conch_facets", "wall_eave_z"]))

# Boolean union removes internal massing faces; no interior architecture is created.
body = main_parts[0]
bpy.context.view_layer.objects.active = body
for other in main_parts[1:]:
    modifier = body.modifiers.new("Envelope_union", "BOOLEAN")
    modifier.operation = "UNION"
    modifier.solver = "EXACT"
    modifier.object = other
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(other, do_unlink=True)
body.name = "Church_exterior_envelope"
body["assumption_ids"] = json.dumps(["nave_west_x", "nave_east_x", "nave_half_width", "conch_half_width", "conch_shoulder", "conch_facets", "wall_eave_z"])

# Towers are separate parametric exterior masses, not hidden interior rooms.
tx, ty, tw, td = p("tower_center_x"), p("tower_center_y"), p("tower_width"), p("tower_depth")
for label, sign in (("north", 1), ("south", -1)):
    y = sign*ty
    poly = rect(tx-td/2, tx+td/2, y-tw/2, y+tw/2)
    footprints["tower_"+label] = poly
    prism("Tower_"+label, poly, p("tower_shaft_z"), "TOWERS", stone,
          ["tower_center_x", "tower_center_y", "tower_width", "tower_depth", "tower_shaft_z"])
    ring = [(tx+p("tower_spire_radius")*math.cos(i*math.tau/8+math.pi/8), y+p("tower_spire_radius")*math.sin(i*math.tau/8+math.pi/8)) for i in range(8)]
    prism("Tower_upper_octagon_"+label, ring, p("tower_spire_base_z"), "TOWERS", stone,
          ["tower_center_x", "tower_center_y", "tower_spire_radius", "tower_shaft_z", "tower_spire_base_z"], bottom=p("tower_shaft_z"))
    # Upper four gables form gross silhouette, no tracery/pinnacles yet.
    for j, angle in enumerate((0, math.pi/2)):
        gable("Tower_gabled_stage_"+label+str(j), -tw/2, tw/2, tw/2,
              p("tower_shaft_z"), p("tower_spire_base_z"), stone, "TOWERS", angle, (tx, y),
              ["tower_width", "tower_shaft_z", "tower_spire_base_z"])
    cone("Tower_stone_helm_"+label, (tx, y), p("tower_spire_radius"),
         p("tower_spire_base_z"), D["tower_height"]["value"], stone, "TOWERS",
         ["tower_spire_radius", "tower_spire_base_z"])["documented_dimension"] = "tower_height (approximate 80 m)"

prism("West_hall", rect(tx-td/2, p("nave_west_x"), -ty+tw/2, ty-tw/2), eave,
      keys=["tower_center_x", "tower_depth", "tower_center_y", "tower_width", "nave_west_x", "wall_eave_z"])
gable("West_hall_roof", tx-td/2, p("nave_west_x"), ty-tw/2, eave, p("west_hall_roof_z"),
      keys=["west_hall_roof_z", "tower_center_x", "tower_depth", "tower_center_y", "tower_width", "nave_west_x", "wall_eave_z"])

# Central ridge and three polygonal hipped choir roofs.
over = p("roof_overhang")
gable("Nave_main_roof", p("nave_west_x"), 0, h+over, eave, p("main_ridge_z"),
      keys=["nave_west_x", "conch_half_width", "roof_overhang", "wall_eave_z", "main_ridge_z"])
for name, angle in (("east", 0), ("north", math.pi/2), ("south", -math.pi/2)):
    radius = h+over
    facets = int(p("conch_facets"))
    arc = [(shoulder+radius*math.cos(-math.pi/2+i*math.pi/facets), radius*math.sin(-math.pi/2+i*math.pi/facets)) for i in range(facets+1)]
    polygon = rotate([(0, -radius)] + arc + [(0, radius)], angle)
    n = len(polygon)
    peaks = rotate([(0, 0), (shoulder, 0)], angle)
    roof("Choir_roof_"+name, polygon, [(x, y, p("main_ridge_z")) for x,y in peaks],
         [(0, 1, n+1, n)] + [(i, i+1, n+1) for i in range(1, n-2)] + [(n-2, n-1, n, n+1), (n-1, 0, n)],
         ["conch_half_width", "conch_shoulder", "conch_facets", "roof_overhang", "main_ridge_z", "wall_eave_z"])

span = (p("nave_east_x")-p("nave_west_x"))/p("side_roof_bays")
for side in (-1, 1):
    for index in range(int(p("side_roof_bays"))):
        x0 = p("nave_west_x")+index*span
        x1 = x0+span
        # Hipped outer end; transverse ridge runs towards central nave roof.
        y0, y1 = side*h, side*(w+over)
        polygon = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        apex = [((x0+x1)/2,y0,p("side_roof_ridge_z")), ((x0+x1)/2,side*(w-span/2),p("side_roof_ridge_z"))]
        roof(f"Aisle_roof_{side}_{index+1}", polygon, apex,
             [(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)],
             ["nave_west_x", "nave_east_x", "side_roof_bays", "side_roof_ridge_z", "nave_half_width", "conch_half_width", "roof_overhang", "wall_eave_z"])

radius = p("crossing_turret_radius")
ring = [(radius*math.cos(i*math.tau/8+math.pi/8),radius*math.sin(i*math.tau/8+math.pi/8)) for i in range(8)]
prism("Crossing_turret_envelope", ring, p("crossing_turret_shoulder_z"), "ROOFS", slate,
      ["crossing_turret_radius", "crossing_turret_shoulder_z", "main_ridge_z"], bottom=p("main_ridge_z")-radius)
cone("Crossing_turret_helm", (0,0), radius, p("crossing_turret_shoulder_z"), p("crossing_turret_tip_z"), slate, "ROOFS",
     ["crossing_turret_radius", "crossing_turret_shoulder_z", "crossing_turret_tip_z"])

sx, sy = p("sacristy_center_x"), p("sacristy_center_y")
dx, dy = p("sacristy_size_x")/2, p("sacristy_size_y")/2
poly = rect(sx-dx, sx+dx, sy-dy, sy+dy)
footprints["sacristy"] = poly
skeys = [k for k in A if k.startswith("sacristy_")]
prism("Sacristy_envelope", poly, p("sacristy_eave_z"), keys=skeys)
prism("Sacristy_connector_envelope", rect(h, sx-dx, sy-dy, sy+dy), p("sacristy_eave_z"), keys=skeys+["conch_half_width"])
mesh("Sacristy_pyramid_roof", [(x,y,p("sacristy_eave_z")) for x,y in poly]+[(sx,sy,p("sacristy_roof_z"))],
     [(3,2,1,0),(0,1,4),(1,2,4),(2,3,4),(3,0,4)], "ROOFS", slate, skeys)

if os.environ.get("EKIRCHE_STRUCTURE") == "1":
    runpy.run_path(str(ROOT/"scripts/blender/30_structure.py"),init_globals=dict(globals()))

# Fixed diagnostic cameras, deliberately not named VAL_*.
settings = payload["inspection"]
for name, spec in settings["views"].items():
    data = bpy.data.cameras.new(name)
    data.type = "ORTHO"
    data.ortho_scale = spec["ortho_scale"]
    obj = bpy.data.objects.new(name, data)
    bpy.data.collections["CAMERAS"].objects.link(obj)
    obj.location = spec["position"]
    obj.rotation_euler = (Vector(spec["target"])-obj.location).to_track_quat("-Z", "Y").to_euler()
    obj["calibration_status"] = settings["status"]
    obj["camera_reason"] = settings["reason"]
scene.camera = bpy.data.objects["INSPECT_SE"]
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 24
scene.render.resolution_x, scene.render.resolution_y = settings["resolution"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.65,0.65,0.65,1)
background.inputs["Strength"].default_value = 0.8
sun = bpy.data.lights.new("Inspection_sun", "SUN")
sun.energy = 3
sun.angle = math.radians(15)
obj = bpy.data.objects.new("Inspection_sun", sun)
bpy.data.collections["CAMERAS"].objects.link(obj)
obj.rotation_euler = (math.radians(25), math.radians(-30), math.radians(-25))
scene.view_settings.view_transform = "AgX"

# Geometry checks operate on generated meshes, not just parameter echoes.
meshes = [o for o in scene.objects if o.type == "MESH"]
vertices = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
mins = [min(v[i] for v in vertices) for i in range(3)]
maxs = [max(v[i] for v in vertices) for i in range(3)]
assert abs(maxs[2]-D["tower_height"]["value"]) < 1e-5
assert mins[0] < 0 < maxs[0] and mins[1] < 0 < maxs[1]
nonmanifold = []
for obj in meshes:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    if any(not e.is_manifold for e in bm.edges):
        nonmanifold.append(obj.name)
    bm.free()
assert not nonmanifold, nonmanifold
bpy.context.view_layer.update()
framing = {}
for camera in (o for o in scene.objects if o.type == "CAMERA"):
    projected = [world_to_camera_view(scene, camera, v) for v in vertices]
    limits = [min(v.x for v in projected), max(v.x for v in projected), min(v.y for v in projected), max(v.y for v in projected)]
    framing[camera.name] = limits
    assert limits[0] >= 0.015 and limits[1] <= 0.985 and limits[2] >= 0.015 and limits[3] <= 0.985, (camera.name, limits)
metrics = {"iteration": iteration, "status": "provisional_not_photo_validated", "mesh_objects": len(meshes),
           "bounds_min_m": mins, "bounds_max_m": maxs, "dimensions_m": [maxs[i]-mins[i] for i in range(3)],
           "nonmanifold_objects": nonmanifold, "footprints_xy_m": footprints, "camera_framing_normalized": framing,
           "tower_height_anchor_residual_m": maxs[2]-D["tower_height"]["value"],
           "anchor_note": "Zero residual is a construction constraint, not independent accuracy evidence.",
           "photo_reprojection_error_px": None, "silhouette_iou": None}
report_dir = ROOT / "validation/reports" / iteration
report_dir.mkdir(parents=True, exist_ok=True)
(report_dir / "geometry.json").write_text(json.dumps(metrics, indent=2)+"\n", encoding="utf-8")
out.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print("EXTERIOR BUILD OK", out)
