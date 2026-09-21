"""Derived diagnostic overlays; no source image is overwritten."""
import argparse
from PIL import Image,ImageDraw,ImageFilter
from fetch_assets import ROOT

parser=argparse.ArgumentParser()
parser.add_argument("iteration")
args=parser.parse_args()
directory=ROOT/"validation/renders"/args.iteration
for path in directory.glob("VAL_M*.png"):
    evidence=path.stem[4:]
    with Image.open(ROOT/"validation/renders/digitization"/f"{evidence}.png") as source:
        background=source.convert("RGBA")
    with Image.open(path) as source:
        render=source.convert("RGBA")
    assert background.size==render.size
    alpha=render.getchannel("A")
    silhouette=Image.new("RGBA",render.size,(255,60,20,0))
    silhouette.putalpha(alpha.point(lambda x:round(x*0.20)))
    composite=Image.alpha_composite(background,silhouette)
    edges=alpha.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    ink=Image.new("RGBA",render.size,(255,55,10,0))
    ink.putalpha(edges)
    composite=Image.alpha_composite(composite,ink)
    draw=ImageDraw.Draw(composite)
    draw.rectangle((0,0,render.width,20),fill="black")
    draw.text((4,4),f"{evidence} / {args.iteration} / ORANGE: PROJECTED MODEL / OCCLUSIONS NOT MASKED",fill="white")
    composite.convert("RGB").save(directory/f"{evidence}_overlay.png")
    print(evidence)
