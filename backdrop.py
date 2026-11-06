"""Persistent background: radial gradient, slowly drifting grid and floating specks."""
import random
from pathlib import Path

import numpy as np
from manim import *

from theme import BG_DEEP, BG_GLOW, GRID


def _hex_to_rgb(value):
    value = value.lstrip("#")
    return np.array([int(value[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def gradient_png(path: Path, width=1920, height=1080):
    from PIL import Image

    ys, xs = np.mgrid[0:height, 0:width]
    dx = (xs - width * 0.5) / (width * 0.62)
    dy = (ys - height * 0.42) / (height * 0.78)
    dist = np.clip(np.sqrt(dx * dx + dy * dy), 0, 1)[..., None]
    inner, outer = _hex_to_rgb(BG_GLOW), _hex_to_rgb(BG_DEEP)
    rgb = inner * (1 - dist) + outer * dist
    rgb += np.random.default_rng(7).uniform(-1.0, 1.0, size=(height, width, 1))  # dither against banding
    Image.fromarray(np.clip(rgb, 0, 255).astype("uint8")).save(path)


def build_backdrop(cache_dir: Path):
    cache_dir.mkdir(parents=True, exist_ok=True)
    png = cache_dir / "backdrop.png"
    gradient_png(png)
    image = ImageMobject(str(png)).set_height(config.frame_height).set_z_index(-20)

    grid = VGroup()
    for x in range(-10, 11):
        grid.add(Line([x, -5, 0], [x, 5, 0], color=GRID, stroke_width=0.9, stroke_opacity=0.26))
    for y in range(-5, 6):
        grid.add(Line([-10, y, 0], [10, y, 0], color=GRID, stroke_width=0.9, stroke_opacity=0.22))
    grid.set_z_index(-19)

    def drift_grid(mob, dt):
        mob.shift(RIGHT * 0.12 * dt)
        if mob.get_center()[0] > 1:
            mob.shift(LEFT)

    grid.add_updater(drift_grid)

    rng = random.Random(11)
    specks = VGroup()
    speeds = []
    for _ in range(22):
        dot = Dot(
            [rng.uniform(-7, 7), rng.uniform(-4.2, 4.2), 0],
            radius=rng.uniform(0.025, 0.06),
            color=GRID,
        ).set_opacity(rng.uniform(0.18, 0.38))
        specks.add(dot)
        speeds.append(rng.uniform(0.06, 0.2))
    specks.set_z_index(-18)

    def float_specks(mob, dt):
        for dot, speed in zip(mob, speeds):
            dot.shift(UP * speed * dt)
            if dot.get_y() > 4.3:
                dot.set_y(-4.3)

    specks.add_updater(float_specks)
    return image, grid, specks
