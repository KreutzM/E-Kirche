#!/usr/bin/env python3
from pathlib import Path
import argparse, json, math, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
parser = argparse.ArgumentParser()
parser.add_argument("--assets", action="store_true", help="Also require readable Priority-1 reference images")
args = parser.parse_args()

def fail(msg):
    errors.append(msg)

rows = json.loads((ROOT/"data"/"manifest.json").read_text(encoding="utf-8"))
ids = [r.get("id") for r in rows]
if len(ids) != len(set(ids)):
    fail("duplicate IDs in data/manifest.json")

required = {"id","group","title","view","role","priority","metric_use","commons_page"}
for i, row in enumerate(rows):
    missing = required - set(row)
    if missing:
        fail(f"manifest row {i} missing {sorted(missing)}")
    if row.get("priority") not in (1,2,3):
        fail(f'{row.get("id")}: priority must be 1..3')
    if not str(row.get("commons_page","")).startswith("https://commons.wikimedia.org/wiki/"):
        fail(f'{row.get("id")}: invalid Commons page')
    if row.get("group") not in ("modern", "historic_pd", "plans"):
        fail(f'{row.get("id")}: invalid reference group')

sources = yaml.safe_load((ROOT/"sources"/"sources.yaml").read_text(encoding="utf-8"))

def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

dims = yaml.safe_load((ROOT/"data"/"dimensions.yaml").read_text(encoding="utf-8"))
for name, d in dims.items():
    for key in ("value","unit","confidence","scope","source_id"):
        if key not in d:
            fail(f"dimension {name} missing {key}")
    if d.get("confidence") not in ("high","medium","low"):
        fail(f"dimension {name}: invalid confidence")
    if not numeric(d.get("value")) or d["value"] <= 0:
        fail(f"dimension {name}: expected positive finite value")
    if d.get("unit") != "m" or not isinstance(d.get("exterior_direct"), bool):
        fail(f"dimension {name}: metres and explicit exterior_direct required")
    if d.get("source_id") not in sources:
        fail(f"dimension {name}: unknown source_id")

coords = yaml.safe_load((ROOT/"data"/"coordinate_system.yaml").read_text(encoding="utf-8"))
if coords.get("units") != "metres":
    fail("coordinate system must use metres")
if coords.get("axes",{}).get("z_positive") != "up":
    fail("Z axis must be up")
for axis, direction in (("x_positive", "east"), ("y_positive", "north")):
    if coords.get("axes", {}).get(axis) != direction:
        fail(f"{axis} must be {direction}")
if coords.get("handedness") != "right":
    fail("coordinate system must be right handed")
if coords.get("origin", {}).get("definition") != "centre of crossing at nominal floor level":
    fail("origin must be centre of crossing at nominal floor level")

assumptions = yaml.safe_load((ROOT/"data"/"assumptions.yaml").read_text(encoding="utf-8"))
if "assumptions" not in assumptions:
    fail("data/assumptions.yaml must contain top-level 'assumptions'")
entries = assumptions.get("assumptions", {})
if not isinstance(entries, dict):
    fail("assumptions must be an ID-keyed mapping")
else:
    for name, entry in entries.items():
        if not isinstance(entry, dict):
            fail(f"assumption {name}: expected mapping")
            continue
        missing = {"value", "unit", "reason", "confidence", "evidence_ids", "iteration"} - entry.keys()
        if missing:
            fail(f"assumption {name}: missing {sorted(missing)}")
        if not numeric(entry.get("value")):
            fail(f"assumption {name}: expected finite numeric value")
        if entry.get("confidence") not in ("high", "medium", "low"):
            fail(f"assumption {name}: invalid confidence")
        for key in ("unit", "reason", "iteration"):
            if not str(entry.get(key, "")).strip():
                fail(f"assumption {name}: empty {key}")
        evidence = entry.get("evidence_ids")
        if not isinstance(evidence, list) or not evidence or any(e not in ids and e not in sources for e in evidence):
            fail(f"assumption {name}: evidence_ids must reference known evidence/sources")

views = yaml.safe_load((ROOT/"validation"/"reference_views.yaml").read_text(encoding="utf-8"))["views"]
for name, view in views.items():
    for evidence in view.get("evidence", []):
        if evidence not in ids:
            fail(f"view {name}: unknown evidence {evidence}")

if args.assets:
    from PIL import Image
    from fetch_assets import destination
    for row in rows:
        if row["priority"] != 1:
            continue
        try:
            with Image.open(destination(row)) as img:
                img.verify()
        except (OSError, ValueError) as exc:
            fail(f'{row["id"]}: missing/unreadable reference: {exc}')

if errors:
    print("VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print(f"VALIDATION OK: {len(rows)} reference records, {len(dims)} documented dimensions")
