"""
ManimGL volumetric ray-marching demo using a Shadertoy fragment shader.
"""

from pathlib import Path
import sys

import numpy as np

from manimlib import Scene
from manimlib import config

# Ensure project root is importable so we can reuse ShaderSurface helper
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from shadersence.mobject.sphere_surface import ShaderSurface
except ImportError:  # fallback minimal base if project structure changes
    from manimlib.mobject.three_dimensions import Surface as ShaderSurface  # type: ignore


class VolumeRaymarchSurface(ShaderSurface):
    """Plane surface that runs a Shadertoy-style ray marching shader."""

    shader_folder = str(Path(__file__).parent / "shaders")

    def __init__(self, **kwargs):
        def plane(u, v):
            # Map UV in [0,1]² to a clip-filling square in the XY plane.
            x = 2.0 * (u - 0.5)
            y = 2.0 * (v - 0.5)
            return np.array([x, y, 0.0])

        # Use low mesh resolution; fragment shader handles complexity.
        super().__init__(
            uv_func=plane,
            u_range=(0.0, 1.0),
            v_range=(0.0, 1.0),
            resolution=(4, 4),
            brightness=1.0,
            **kwargs,
        )

        # Base ShaderSurface already sets time uniform and updater.
        pixel_size = self._current_resolution()
        self.set_uniform(resolution=pixel_size)
        self.set_uniform(mouse=np.array([0.0, 0.0], dtype=float))

        # Keep resolution in sync if window size changes at runtime.
        self.add_updater(lambda mob, dt: mob._sync_resolution())

    def _sync_resolution(self):
        pixel_size = self._current_resolution()
        self.set_uniform(resolution=pixel_size)
        return self

    @staticmethod
    def _current_resolution():
        width = float(getattr(config, "pixel_width", 1280))
        height = float(getattr(config, "pixel_height", 720))
        return np.array([width, height], dtype=float)


class ShaderVolumeDemo(Scene):
    """Scene that displays the volumetric ray-marched object."""

    def construct(self):
        volume = VolumeRaymarchSurface()
        volume.scale(3.2)  # ensure the quad fills the viewport
        self.add(volume)

        # Let the shader run for a while
        self.wait(12)


if __name__ == "__main__":
    import os

    script_dir = Path(__file__).parent
    script_name = Path(__file__).stem
    os.system(f"cd {script_dir} && manimgl {script_name}.py ShaderVolumeDemo")
