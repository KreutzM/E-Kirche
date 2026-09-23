"""Create a before/after plate from synthetic renders; no reference images edited."""
from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
plate=Image.new("RGB",(1200,1530),"#222222")
draw=ImageDraw.Draw(plate)
for row,view in enumerate(("W","NE","SE")):
    for col,iteration in enumerate(("phase_a_002","phase_a_003")):
        path=root/"validation/renders"/iteration/f"INSPECT_{view}.png"
        with Image.open(path) as source:
            thumb=source.convert("RGB")
            thumb.thumbnail((600,480),Image.Resampling.LANCZOS)
        plate.paste(thumb,(col*600,row*510+30))
        draw.text((col*600+12,row*510+8),f"{iteration} / {view} / SAME CAMERA",fill="white")
out=root/"docs/iterations/phase_a_003_comparison.jpg"
plate.save(out,quality=90)
print(out)
