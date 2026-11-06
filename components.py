import numpy as np
from manim import *
from theme import ACCENT, AMBER, BG, INK, MUTED, PANEL, PANEL_DEEP, FONT


def label(content, size=30, color=INK, weight=NORMAL):
    return Text(str(content), font=FONT, font_size=size, color=color, weight=weight)


def capsule(content, color=ACCENT, size=18):
    text = label(content, size, color, BOLD)
    plate = RoundedRectangle(
        width=text.width + 0.5,
        height=text.height + 0.32,
        corner_radius=0.15,
        stroke_color=color,
        stroke_width=2,
        fill_color=PANEL_DEEP,
        fill_opacity=1,
    )
    return VGroup(plate, text)


def heading(eyebrow, title):
    tag = label(eyebrow.upper(), 20, ACCENT, BOLD).move_to([0, 3.35, 0])
    headline = label(title, 42, INK, BOLD).move_to([0, 2.6, 0])
    return VGroup(tag, headline)


# ---------------------------------------------------------------- icons
def api_icon(color):
    window = RoundedRectangle(width=0.92, height=0.66, corner_radius=0.09, stroke_color=color, stroke_width=2.5, fill_opacity=0)
    bar = Line([-0.46, 0.17, 0], [0.46, 0.17, 0], color=color, stroke_width=2.5)
    dots = VGroup(*[Dot([x, 0.25, 0], radius=0.024, color=color) for x in (-0.37, -0.29, -0.21)])
    braces = label("{ }", 20, color, BOLD).move_to([0, -0.08, 0])
    return VGroup(window, bar, dots, braces)


def cache_icon(color):
    ring = Circle(radius=0.4, stroke_color=color, stroke_width=2.5, fill_opacity=0)
    bolt = Polygon(
        [0.10, 0.26, 0], [-0.14, -0.02, 0], [0.0, -0.02, 0],
        [-0.10, -0.26, 0], [0.15, 0.04, 0], [0.01, 0.04, 0],
        stroke_width=0, fill_color=color, fill_opacity=1,
    )
    return VGroup(ring, bolt)


def db_icon(color):
    width, ry = 0.8, 0.28
    bottom = Ellipse(width=width, height=ry, stroke_color=color, stroke_width=2.5, fill_color=PANEL, fill_opacity=1).move_to([0, -0.3, 0])
    body = Rectangle(width=width, height=0.6, stroke_width=0, fill_color=PANEL, fill_opacity=1)
    sides = VGroup(
        Line([-width / 2, 0.3, 0], [-width / 2, -0.3, 0], color=color, stroke_width=2.5),
        Line([width / 2, 0.3, 0], [width / 2, -0.3, 0], color=color, stroke_width=2.5),
    )
    band = Arc(radius=width / 2, start_angle=PI, angle=PI, color=color, stroke_width=2.5).stretch(ry / width, 1).move_to([0, 0.0, 0])
    top = Ellipse(width=width, height=ry, stroke_color=color, stroke_width=2.5, fill_color=PANEL, fill_opacity=1).move_to([0, 0.3, 0])
    return VGroup(bottom, body, sides, band, top)


def clock_icon(color, radius=0.2):
    ring = Circle(radius=radius, stroke_color=color, stroke_width=2.5, fill_opacity=0)
    hands = VGroup(
        Line(ORIGIN, UP * radius * 0.65, color=color, stroke_width=2.5),
        Line(ORIGIN, RIGHT * radius * 0.5, color=color, stroke_width=2.5),
    )
    return VGroup(ring, hands)


def chart_icon(color):
    bars = VGroup(*[
        Rectangle(width=0.18, height=h, stroke_width=0, fill_color=color, fill_opacity=1)
        for h in (0.28, 0.5, 0.74)
    ]).arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
    base = Line(bars.get_corner(DL) + LEFT * 0.08, bars.get_corner(DR) + RIGHT * 0.08, color=color, stroke_width=2.5)
    return VGroup(bars, base)


ICONS = {"api": api_icon, "cache": cache_icon, "db": db_icon}


# ---------------------------------------------------------------- nodes
class ServiceNode(VGroup):
    """Glowing service card with an icon, title and optional subtitle."""

    def __init__(self, name, accent, icon, subtitle=None, width=2.7, compact=False, position=ORIGIN):
        height = 1.25 if compact else 2.0
        self.accent = accent
        glow = VGroup(*[
            RoundedRectangle(
                width=width + gap, height=height + gap, corner_radius=0.22 + gap / 2,
                stroke_color=accent, stroke_width=w, stroke_opacity=op, fill_opacity=0,
            )
            for gap, w, op in ((0.12, 12, 0.10), (0.05, 5, 0.24))
        ])
        card = RoundedRectangle(
            width=width, height=height, corner_radius=0.22,
            stroke_color=accent, stroke_width=2.5, fill_color=PANEL, fill_opacity=1,
        )
        glyph = ICONS[icon](accent)
        title = label(name, 26 if compact else 30, INK, BOLD)
        parts = [glow, card, glyph, title]
        if compact:
            glyph.scale(0.78).move_to([-width / 2 + 0.6, 0, 0])
            title.next_to(glyph, RIGHT, buff=0.22)
        elif subtitle:
            glyph.move_to([0, 0.52, 0])
            title.move_to([0, -0.14, 0])
            parts.append(label(subtitle, 19, MUTED).move_to([0, -0.55, 0]))
        else:
            glyph.move_to([0, 0.35, 0])
            title.move_to([0, -0.35, 0])
        veil = RoundedRectangle(
            width=width, height=height, corner_radius=0.22, stroke_width=0,
            fill_color=BG, fill_opacity=0,
        )
        parts.append(veil)
        super().__init__(*parts)
        self.card = card
        self.glow = glow
        self.veil = veil
        target = np.array(position, dtype=float)
        if target.size == 2:
            target = np.append(target, 0.0)
        self.move_to(target)

    def fade_back(self, opacity=0.7):
        return self.veil.animate.set_fill(opacity=opacity)


# ---------------------------------------------------------------- lanes and packets
class Lane(VGroup):
    """Glowing arrow between two points. `route` is the path a packet travels."""

    def __init__(self, start, end, color, width=5, head_length=0.22):
        start = np.array(start, dtype=float)
        end = np.array(end, dtype=float)
        direction = (end - start) / np.linalg.norm(end - start)
        shaft_end = end - direction * head_length * 0.8
        glow = Line(start, shaft_end, color=color, stroke_width=width + 8, stroke_opacity=0.18)
        shaft = Line(start, shaft_end, color=color, stroke_width=width)
        head = Triangle(fill_color=color, fill_opacity=1, stroke_width=0).scale(head_length / 1.5)
        head.rotate(angle_of_vector(direction) - PI / 2).move_to(end - direction * head_length / 2)
        super().__init__(glow, shaft, head)
        self.route = Line(start, end - direction * 0.08)
        self._parts = (glow, shaft, head)

    def draw(self):
        glow, shaft, head = self._parts
        return AnimationGroup(Create(glow), Create(shaft), FadeIn(head), lag_ratio=0.0)


def packet(color=ACCENT, scale=1.0):
    halo = Dot(radius=0.27 * scale, color=color).set_opacity(0.13)
    mid = Dot(radius=0.17 * scale, color=color).set_opacity(0.38)
    core = Dot(radius=0.09 * scale, color=color)
    group = VGroup(halo, mid, core)
    group.tint = color
    return group


# ---------------------------------------------------------------- latency clock
class Clock(VGroup):
    """Stopwatch readout that can count to a value (no LaTeX needed)."""

    def __init__(self, color=AMBER, width=2.8, suffix=" ms"):
        self.suffix = suffix
        self.value = 0
        self.readout_color = INK
        plate = RoundedRectangle(
            width=width, height=0.66, corner_radius=0.18,
            stroke_color=color, stroke_width=2.2, fill_color=PANEL_DEEP, fill_opacity=1,
        )
        icon = clock_icon(color, 0.2).move_to(plate.get_left() + RIGHT * 0.45)
        readout = self._make_readout(0, icon)
        super().__init__(plate, icon, readout)
        self.plate = plate
        self.icon = icon
        self.readout = readout

    def _make_readout(self, value, icon=None):
        icon = icon if icon is not None else self.icon
        return label(f"{value:.0f}{self.suffix}", 28, self.readout_color, BOLD).next_to(icon, RIGHT, buff=0.22)

    def count_to(self, target, run_time):
        start = self.value
        self.value = target

        def update(mob, alpha):
            mob.become(self._make_readout(start + (target - start) * alpha))

        return UpdateFromAlphaFunc(self.readout, update, run_time=run_time, rate_func=linear)

    def recolor(self, color):
        self.readout_color = color
        return AnimationGroup(
            self.plate.animate.set_stroke(color=color),
            self.icon.animate.set_color(color),
            self.readout.animate.set_color(color),
        )
