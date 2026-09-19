#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw
import json, math

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT/"data"/"manifest.json").read_text(encoding="utf-8"))
OUT = ROOT/"references"/"contact_sheets"
OUT.mkdir(parents=True, exist_ok=True)

def path_for(r):
    if r["group"] == "modern":
        base = ROOT/"references"/"images"/"modern"
    elif r["group"] == "historic_pd":
        base = ROOT/"references"/"images"/"historic"
    else:
        base = ROOT/"references"/"plans"/"downloaded"
    return base/f'{r["id"]}_{Path(r["title"]).name}'

def sheet(name, rows, cols=4, tile=(500,380)):
    rows = [r for r in rows if path_for(r).exists()]
    if not rows:
        print("skip", name, "(no downloaded files)")
        return
    nrows = math.ceil(len(rows)/cols)
    canvas = Image.new("RGB",(cols*tile[0],nrows*tile[1]),"white")
    draw = ImageDraw.Draw(canvas)
    for i,r in enumerate(rows):
        img = Image.open(path_for(r)).convert("RGB")
        img.thumbnail((tile[0]-20,tile[1]-70))
        x=(i%cols)*tile[0]+(tile[0]-img.width)//2
        y=(i//cols)*tile[1]+10
        canvas.paste(img,(x,y))
        draw.text(((i%cols)*tile[0]+10,(i//cols)*tile[1]+tile[1]-50),
                  f'{r["id"]} | {r["view"]} | P{r["priority"]}',fill="black")
    canvas.save(OUT/f"{name}.jpg",quality=88)

sheet("overview",[r for r in MANIFEST if r["priority"]==1])
sheet("west",[r for r in MANIFEST if r["view"].startswith(("W","SW"))])
sheet("south",[r for r in MANIFEST if r["view"].startswith(("S","SE"))])
sheet("north",[r for r in MANIFEST if r["view"].startswith(("N","NE"))])
sheet("plans",[r for r in MANIFEST if r["group"]=="plans"])
