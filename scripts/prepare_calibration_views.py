"""Generate fixed-size digitization previews, preserving all reference originals."""
import json
from PIL import Image, ImageDraw
from fetch_assets import ROOT, destination

out = ROOT / "validation/renders/digitization"
out.mkdir(parents=True, exist_ok=True)
for record in json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8")):
    if record["id"] not in ("M02", "M03", "M10", "M11", "M05", "M07", "M09"):
        continue
    with Image.open(destination(record)) as original:
        image = original.convert("RGB")
        image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    image.save(out / f'{record["id"]}.png')
    if record["id"] == "M11":
        image.crop((250,700,680,1080)).resize((1075,950)).save(out / "M11_base_crop.png")
        image.crop((280,480,660,800)).resize((1140,960)).save(out / "M11_shaft_crop.png")
    draw = ImageDraw.Draw(image)
    for x in range(0, image.width, 100):
        draw.line((x, 0, x, image.height), fill=(160, 160, 160), width=1)
        draw.text((x+2, 3), str(x), fill="red", stroke_width=1, stroke_fill="white")
    for y in range(0, image.height, 100):
        draw.line((0, y, image.width, y), fill=(160, 160, 160), width=1)
        draw.text((2, y+2), str(y), fill="red", stroke_width=1, stroke_fill="white")
    image.save(out / f'{record["id"]}_grid.png')
    print(record["id"], image.size)
