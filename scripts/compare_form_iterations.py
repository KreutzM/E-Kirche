"""Create a before/after plate from synthetic renders; no reference images edited."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("--before",default="phase_a_002")
parser.add_argument("--after",default="phase_a_003")
args=parser.parse_args()
plate=Image.new("RGB",(1200,1530),"#222222")
draw=ImageDraw.Draw(plate)
for row,view in enumerate(("W","NE","SE")):
    for col,iteration in enumerate((args.before,args.after)):
        path=root/"validation/renders"/iteration/f"INSPECT_{view}.png"
        with Image.open(path) as source:
            thumb=source.convert("RGB")
            thumb.thumbnail((600,480),Image.Resampling.LANCZOS)
        plate.paste(thumb,(col*600,row*510+30))
        draw.text((col*600+12,row*510+8),f"{iteration} / {view} / SAME CAMERA",fill="white")
out=root/"docs/iterations"/f"{args.after}_comparison.jpg"
plate.save(out,quality=90)
print(out)
