"""Fit camera hypotheses to fixed model landmarks; keep independent check points."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.optimize import least_squares
import yaml

ROOT = Path(__file__).resolve().parents[1]


def landmarks(a):
    p = {key: record["value"] for key, record in a["assumptions"].items()}
    x, y, r = p["tower_center_x"], p["tower_center_y"], p["tower_spire_radius"]
    front = x-p["tower_depth"]/2
    end = p["conch_shoulder"]+p["conch_half_width"]*math.cos(math.pi/10)
    points = {"west_portal_ground": [front,0,0], "south_conch_ground": [0,-end,0],
              "east_conch_ground": [end,0,0], "south_conch_ridge": [0,-p["conch_shoulder"],p["main_ridge_z"]],
              "east_conch_ridge": [p["conch_shoulder"],0,p["main_ridge_z"]],
              "crossing_turret_tip": [0,0,p["crossing_turret_tip_z"]]}
    for name, sign in (("north",1),("south",-1)):
        points[f"tower_{name}_tip"] = [x,sign*y,80]
        points[f"tower_{name}_helm_front"] = [x-r*math.cos(math.pi/8),sign*y,p["tower_spire_base_z"]]
        points[f"tower_{name}_helm_east"] = [x+r*math.cos(math.pi/8),sign*y,p["tower_spire_base_z"]]
        for label, z in (("ground",0),("shaft",p["tower_shaft_z"]),("eave",p["wall_eave_z"])):
            points[f"tower_{name}_{label}_front" if label != "ground" else f"tower_{name}_front_ground"] = [front,sign*y,z]
    return points


def basis(camera):
    yaw,pitch,roll = camera[3:6]
    forward = np.array([math.cos(pitch)*math.cos(yaw),math.cos(pitch)*math.sin(yaw),math.sin(pitch)])
    right = np.array([math.sin(yaw),-math.cos(yaw),0])
    up = np.cross(right,forward)
    return math.cos(roll)*right+math.sin(roll)*up, -math.sin(roll)*right+math.cos(roll)*up, forward


def project(camera, points, size):
    right,up,forward = basis(camera)
    relative = np.asarray(points)-np.asarray(camera[:3])
    depth = relative @ forward
    shift_x, shift_y = camera[7:9] if len(camera) > 7 else (0,0)
    return np.column_stack((size[0]/2+shift_x+camera[6]*(relative@right)/depth,
                            size[1]/2+shift_y-camera[6]*(relative@up)/depth))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="phase_a_002")
    parser.add_argument("--assumptions", type=Path, default=ROOT/"data/assumptions.yaml")
    parser.add_argument("--refine", action="store_true", help="Propose shared heights from M03/M10/M11; M02 withheld")
    args = parser.parse_args()
    observations = yaml.safe_load((ROOT/"validation/photo_landmarks.yaml").read_text(encoding="utf-8"))
    assumptions = yaml.safe_load(args.assumptions.read_text(encoding="utf-8"))
    world = landmarks(assumptions)
    solutions = {}
    out = ROOT/"validation/reports"/args.output
    out.mkdir(parents=True, exist_ok=True)
    render = ROOT/"validation/renders"/args.output
    render.mkdir(parents=True, exist_ok=True)
    for name, view in observations["views"].items():
        fit = [p for p in view["points"] if p["use"] == "fit"]
        xyz = [world[p["name"]] for p in fit]
        uv = np.array([p["uv"] for p in fit])
        sigma = np.array([p["sigma_px"] for p in fit])[:,None]
        initial = np.array(view["initial_camera"]+[0, view["image_size"][1]*0.36], dtype=float)
        initial[2] = 1.7
        initial[4] = 0
        initial[5] = 0
        free = [0,1,3,4,5,6,8]
        lower = np.array(view["camera_bounds"][0]+[-view["image_size"][0]*0.3, -view["image_size"][1]*0.6])
        upper = np.array(view["camera_bounds"][1]+[view["image_size"][0]*0.3, view["image_size"][1]*0.6])
        lower[5], upper[5] = -0.05, 0.05
        lower[4], upper[4] = -0.2, 1.0
        lower[6] = 150
        def expand(values):
            camera = initial.copy()
            camera[free] = values
            return camera
        def residual(values):
            camera = expand(values)
            return ((project(camera,xyz,view["image_size"])-uv)/sigma).ravel()
        result = least_squares(residual, initial[free], bounds=(lower[free],upper[free]),
                               x_scale="jac", loss="linear", max_nfev=3000)
        camera = expand(result.x)
        points = []
        with Image.open(ROOT/"validation/renders/digitization"/f"{name}.png") as source:
            image = source.convert("RGB")
        draw = ImageDraw.Draw(image)
        for point in view["points"]:
            pred = project(camera,[world[point["name"]]],view["image_size"])[0]
            obs = point["uv"]
            error = float(np.linalg.norm(pred-obs))
            points.append({**point,"xyz":world[point["name"]],"projected_uv":pred.tolist(),"error_px":error})
            draw.line([tuple(obs),tuple(pred)], fill="yellow", width=2)
            draw.ellipse((obs[0]-4,obs[1]-4,obs[0]+4,obs[1]+4),outline="lime",width=2)
            draw.ellipse((pred[0]-4,pred[1]-4,pred[0]+4,pred[1]+4),outline="red",width=2)
        draw.rectangle((0,0,image.width,18),fill="black")
        draw.text((4,3),f"{name}: GREEN observed / RED projected / camera hypothesis, not validated",fill="white")
        image.save(render/f"{name}_landmarks.png")
        def rmse(use):
            selected=[p["error_px"]**2 for p in points if p["use"]==use]
            return float(np.sqrt(np.mean(selected))) if selected else None
        solutions[name] = {"camera":camera.tolist(),"image_size":view["image_size"],
                           "status":"provisional_model_dependent_camera_fit", "optimizer_success":bool(result.success),
                           "fit_rmse_px":rmse("fit"),"check_rmse_px":rmse("check"),
                           "parameters_at_bounds":np.flatnonzero(result.active_mask).tolist(),"points":points}
        print(name,"fit",round(rmse("fit"),2),"check",round(rmse("check"),2),"camera",camera.round(3).tolist())
    report = {"projection":observations["projection"],"assumptions_sha256":hashlib.sha256(args.assumptions.read_bytes()).hexdigest(),
              "observations_sha256":hashlib.sha256((ROOT/"validation/photo_landmarks.yaml").read_bytes()).hexdigest(),"views":solutions}
    (out/"camera_solutions.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if args.refine:
        keys = ["wall_eave_z", "tower_shaft_z", "main_ridge_z", "crossing_turret_tip_z"]
        values = [assumptions["assumptions"][key]["value"] for key in keys]
        prior_sigma = np.array([2, 4, 4, 5])
        selected = ["M03", "M10", "M11"]
        free = [0,1,3,4,5,6,8]
        start = list(values)
        lows, highs = [20.2,38,27,43], [25,48,38,58]
        for name in selected:
            start.extend(np.array(solutions[name]["camera"])[free])
            view = observations["views"][name]
            lo = view["camera_bounds"][0]+[-1000,-view["image_size"][1]*0.6]
            hi = view["camera_bounds"][1]+[1000,view["image_size"][1]*0.6]
            lo[4],hi[4],lo[5],hi[5],lo[6] = -0.2,1.0,-0.03,0.03,150
            lows.extend(np.array(lo)[free]); highs.extend(np.array(hi)[free])
        def residual_all(x):
            inferred = copy.deepcopy(assumptions)
            for key, value in zip(keys,x[:4]):
                inferred["assumptions"][key]["value"] = float(value)
            points3d = landmarks(inferred)
            result = list((x[:4]-values)/prior_sigma)
            for index,name in enumerate(selected):
                view = observations["views"][name]
                camera = np.array(solutions[name]["camera"])
                camera[free] = x[4+index*7:4+(index+1)*7]
                # Occluded tower bases are not calibration observations.
                points = [p for p in view["points"] if p["use"] in ("fit","check") and "front_ground" not in p["name"]]
                xyz = [points3d[p["name"]] for p in points]
                target = np.array([p["uv"] for p in points])
                sigma = np.array([max(p["sigma_px"],4) for p in points])[:,None]
                result.extend(((project(camera,xyz,view["image_size"])-target)/sigma).ravel())
            return np.array(result)
        refined = least_squares(residual_all,start,bounds=(lows,highs),x_scale="jac",max_nfev=3000)
        proposal = copy.deepcopy(assumptions)
        for key,value in zip(keys,refined.x[:4]):
            proposal["assumptions"][key].update(value=round(float(value),2),iteration="phase_a_002",
                reason="Joint provisional height inference from M03/M10/M11 image controls with fixed plan and 80 m anchor; M02 withheld; not a survey.",
                evidence_ids=["M03","M10","M11"],confidence="low")
        (ROOT/"tmp/phase_a_002_proposal.yaml").write_text(yaml.safe_dump(proposal,sort_keys=False),encoding="utf-8")
        (out/"height_proposal.json").write_text(json.dumps({"keys":keys,"before":values,"after":refined.x[:4].tolist(),
            "withheld_view":"M02", "optimizer_success":bool(refined.success),"note":"Calibration data reused for refinement; training residuals are not independent validation."},indent=2),encoding="utf-8")
        print("PROPOSED",dict(zip(keys,refined.x[:4].round(3))))


if __name__ == "__main__":
    main()
