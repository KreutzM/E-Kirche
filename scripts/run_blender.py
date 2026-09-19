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
    parser.add_argument("task", choices=("smoke", "scene", "render"))
    parser.add_argument("--blender")
    args = parser.parse_args()
    subprocess.run([os.sys.executable, str(ROOT / "scripts/validate_dataset.py")], check=True)
    env = os.environ.copy()
    env["EKIRCHE_DIMENSIONS_JSON"] = json.dumps(yaml.safe_load((ROOT / "data/dimensions.yaml").read_text(encoding="utf-8")))
    cmd = [find_blender(args.blender), "--background"]
    scene = ROOT / "blender/scene/elisabethkirche.blend"
    if args.task == "render":
        if not scene.exists():
            raise SystemExit("Scene missing; build and calibrate the model first.")
        cmd += [str(scene)]
    else:
        cmd += ["--factory-startup"]
    cmd += ["--python-exit-code", "1"]
    if args.task == "scene":
        if scene.exists():
            raise SystemExit("Scene already exists; preserve it before explicitly rebuilding.")
        scripts = ["00_scene_setup.py", "10_massing.py"]
    else:
        scripts = ["smoke_test.py" if args.task == "smoke" else "90_validation.py"]
    for script in scripts:
        cmd += ["--python", str(ROOT / "scripts/blender" / script)]
    return subprocess.run(cmd, cwd=ROOT, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
