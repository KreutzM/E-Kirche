"""Fast guards for detail placement; mesh/material tests run inside Blender."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]


class DetailParameterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p={key:record["value"] for key,record in yaml.safe_load((ROOT/"data/assumptions.yaml").read_text(encoding="utf-8"))["assumptions"].items()}

    def test_clock_backing_clears_original_roof(self):
        self.assertGreater(self.p["west_gable_depth"], self.p["opening_recess"])

    def test_side_roof_meets_main_slope(self):
        p=self.p
        ratio=(p["main_ridge_z"]-p["side_roof_ridge_z"])/(p["main_ridge_z"]-p["wall_eave_z"])
        self.assertGreater(ratio,0)
        self.assertLess(ratio,1)

    def test_pinnacles_below_main_helm(self):
        p=self.p
        self.assertLess(p["pinnacle_body_height"],p["pinnacle_tip_height"])
        self.assertLess(p["tower_shaft_z"]+p["pinnacle_tip_height"],p["tower_spire_base_z"])
