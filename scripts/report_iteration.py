#!/usr/bin/env python3
"""Quantitative plan calibration and a derived overlay; source images stay untouched."""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
import yaml

from fetch_assets import ROOT, destination


def main():
    calibration = yaml.safe_load((ROOT / "data/plan_calibration.yaml").read_text(encoding="utf-8"))
    dimensions = yaml.safe_load((ROOT / "data/dimensions.yaml").read_text(encoding="utf-8"))
    iteration = calibration["iteration"]
    directory = ROOT / "validation/reports" / iteration
    geometry = json.loads((directory / "geometry.json").read_text(encoding="utf-8"))
    first, second = calibration["scale_points_uv"]
    anchor = dimensions[calibration["scale_anchor"]]["value"]
    pixels_per_metre = math.dist(first, second) / anchor
    checks = {}
    for name, check in calibration["checks"].items():
        measured = math.dist(*check["points_uv"]) / pixels_per_metre
        result = {"plan_derived_m": measured, "role": check["role"]}
        if "documented_dimension" in check:
            documented = dimensions[check["documented_dimension"]]["value"]
            result.update(documented_m=documented, residual_m=measured-documented,
                          residual_percent=100*(measured/documented-1))
        checks[name] = result
    result = {"iteration": iteration, "status": "provisional_manual_calibration",
              "preview_pixels_per_metre": pixels_per_metre, "checks": checks,
              "warning": "Image-derived historical dimensions are not surveyed present-day measurements. Residuals include manual picking and definition differences."}
    (directory / "plan_calibration.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")

    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    row = next(row for row in manifest if row["id"] == calibration["evidence_id"])
    with Image.open(destination(row)) as source:
        if list(source.size) != calibration["original_size_px"]:
            raise ValueError("Plan resolution changed; review calibration explicitly")
        canvas = source.convert("RGB").resize(tuple(calibration["digitization_size_px"]), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(canvas)
    origin_u, origin_v = calibration["origin_uv"]
    def pixel(xy):
        x, y = xy
        return (origin_u-y*pixels_per_metre, origin_v-x*pixels_per_metre)
    for name, polygon in geometry["footprints_xy_m"].items():
        points = [pixel(point) for point in polygon]
        draw.line(points+[points[0]], fill=(200,35,35), width=3)
    draw.line([tuple(first), tuple(second)], fill=(0,110,220), width=4)
    draw.ellipse((origin_u-8,origin_v-8,origin_u+8,origin_v+8), outline=(0,110,220), width=3)
    draw.rectangle((10, 10, 1000, 72), fill="white")
    draw.text((20,20), "P01 / PHASE A 001 / RED: INFERRED COARSE FOOTPRINT / BLUE: SCALE ANCHOR + ORIGIN", fill="black")
    draw.text((20,42), "Historical plan overlay - provisional, not a measured present-day survey", fill="black")
    out = ROOT / "validation/renders" / iteration
    out.mkdir(parents=True, exist_ok=True)
    canvas.save(out / "plan_overlay.png")
    preview = out / "INSPECT_SE.png"
    if preview.exists():
        with Image.open(preview) as rendered:
            rendered.thumbnail((960, 800))
            target = ROOT / "docs/iterations" / f"{iteration}_preview.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            rendered.save(target)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
