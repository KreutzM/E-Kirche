"""Optional calibration tests; run with requirements-calibration.txt installed."""
import importlib.util
from pathlib import Path
import unittest

AVAILABLE = all(importlib.util.find_spec(name) for name in ("numpy", "scipy"))
if AVAILABLE:
    spec = importlib.util.spec_from_file_location("solve_cameras", Path(__file__).resolve().parents[1] / "scripts/solve_cameras.py")
    solver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver)


@unittest.skipUnless(AVAILABLE, "optional calibration dependencies not installed")
class CameraProjectionTests(unittest.TestCase):
    def test_shifted_pinhole_axes(self):
        camera = [0, 0, 0, 0, 0, 0, 100, 12, 25]
        actual = solver.project(camera, [[10, 0, 0], [10, -1, 0], [10, 0, 1]], [800, 600])
        solver.np.testing.assert_allclose(actual, [[412, 325], [422, 325], [412, 315]])

    def test_basis_is_orthonormal(self):
        basis = solver.np.array(solver.basis([2, 3, 4, .6, .2, -.03, 500]))
        solver.np.testing.assert_allclose(basis @ basis.T, solver.np.eye(3), atol=1e-12)

    def test_translation_invariance(self):
        camera = [0, 0, 0, .1, .2, .03, 100, 0, 0]
        shifted = camera.copy()
        shifted[:3] = [2, 3, 4]
        solver.np.testing.assert_allclose(
            solver.project(camera, [[10, 1, 1]], [800, 600]),
            solver.project(shifted, [[12, 4, 5]], [800, 600]))
