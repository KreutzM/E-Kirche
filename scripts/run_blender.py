#!/usr/bin/env python3
"""Portable background runner; host Python supplies YAML data as JSON."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def find_blender(explicit=None):
    candidate = explicit or os.environ.get("BLENDER_EXE") or shutil.which("blender")
    if candidate:
        return str(candidate)
    base = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Blender Foundation"
    candidates = list(base.glob("Blender */blender.exe"))
    if candidates:
        return str(max(candidates, key=lambda p: tuple(int(n) for n in p.parent.name.split()[-1].split("."))))
    raise SystemExit("Blender not found. Set BLENDER_EXE or pass --blender with the executable path.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("smoke", "scene", "render", "build", "inspect", "calibrate", "verify-form", "present", "web-export"))
    parser.add_argument("--blender")
    parser.add_argument("--output", type=Path, help="New .blend for build, or destination .glb for web-export")
    parser.add_argument("--scene", type=Path, help="Existing .blend to inspect/render")
    parser.add_argument("--cameras", type=Path, help="Camera solution JSON for calibrate")
    parser.add_argument("--iteration", default="phase_a_002")
    parser.add_argument("--structure", action="store_true", help="Include exterior buttresses and recessed openings")
    parser.add_argument("--assumptions", type=Path, default=ROOT / "data/assumptions.yaml")
    args = parser.parse_args()
    subprocess.run([os.sys.executable, str(ROOT / "scripts/validate_dataset.py")], check=True)
    env = os.environ.copy()
    env["EKIRCHE_ITERATION"] = args.iteration
    env["EKIRCHE_STRUCTURE"] = "1" if args.structure else "0"
    env["EKIRCHE_INSPECTION_JSON"] = json.dumps(yaml.safe_load((ROOT / "validation/inspection_views.yaml").read_text(encoding="utf-8")))
    if args.task == "calibrate":
        if not args.cameras or not args.output:
            parser.error("calibrate requires --cameras and --output")
        env["EKIRCHE_CAMERAS"] = str(args.cameras.resolve())
        env["EKIRCHE_OUTPUT"] = str(args.output.resolve())
    env["EKIRCHE_DIMENSIONS_JSON"] = json.dumps(yaml.safe_load((ROOT / "data/dimensions.yaml").read_text(encoding="utf-8")))
    if args.task == "build":
        subprocess.run([os.sys.executable, str(ROOT / "scripts/validate_dataset.py"), "--assets"], check=True)
        payload = {"dimensions": json.loads(env["EKIRCHE_DIMENSIONS_JSON"])}
        for name, path in (("assumptions", args.assumptions), ("inspection", "validation/inspection_views.yaml")):
            payload[name] = yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))
        env["EKIRCHE_MODEL_JSON"] = json.dumps(payload)
        env["EKIRCHE_OUTPUT"] = str((args.output or ROOT / "blender/scene" / f"{args.iteration}.blend").resolve())
    if args.task == "web-export":
        env["EKIRCHE_OUTPUT"] = str((args.output or ROOT / "web/assets/elisabethkirche.glb").resolve())
    cmd = [find_blender(args.blender), "--background"]
    scene = args.scene or ROOT / ("blender/scene/phase_a_001.blend" if args.task == "inspect" else "blender/scene/phase_a_004.blend" if args.task == "web-export" else "blender/scene/elisabethkirche.blend")
    if args.task in ("render", "inspect", "calibrate", "verify-form", "present", "web-export"):
        if not scene.exists():
            raise SystemExit("Scene missing; build and calibrate the model first.")
        cmd += [str(scene.resolve())]
    else:
        cmd += ["--factory-startup"]
    cmd += ["--python-exit-code", "1"]
    if args.task == "scene":
        if scene.exists():
            raise SystemExit("Scene already exists; preserve it before explicitly rebuilding.")
        scripts = ["00_scene_setup.py", "10_massing.py"]
    else:
        scripts = [{"smoke": "smoke_test.py", "render": "90_validation.py", "build": "20_exterior.py", "inspect": "80_inspection.py", "calibrate": "70_photo_cameras.py", "verify-form": "85_verify_form.py", "present": "95_presentation.py", "web-export": "96_web_export.py"}[args.task]]
    for script in scripts:
        cmd += ["--python", str(ROOT / "scripts/blender" / script)]
    return subprocess.run(cmd, cwd=ROOT, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
