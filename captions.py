"""Burned-in captions driven by data/cues.json (SRT export lives in subtitles.py)."""
from manim import *

from components import label
from theme import BG_DEEP, CAPTION_BOTTOM_Y, INK


def build_caption(text: str) -> VGroup:
    lines = VGroup(*[label(line, 30, INK, BOLD) for line in text.split("\n")]).arrange(DOWN, buff=0.1)
    plate = RoundedRectangle(
        width=lines.width + 0.8,
        height=lines.height + 0.36,
        corner_radius=0.2,
        stroke_width=0,
        fill_color=BG_DEEP,
        fill_opacity=0.8,
    )
    caption = VGroup(plate, lines)
    caption.move_to(ORIGIN).align_to([0, CAPTION_BOTTOM_Y, 0], DOWN)
    caption.set_z_index(100)
    return caption


class CaptionTrack(VGroup):
    """Shows the caption whose window contains the scene clock, with a short fade."""

    def __init__(self, captions, clock, fade=0.12):
        super().__init__()
        self.captions = captions
        self.clock = clock
        self.fade = fade
        self.index = None
        self.add_updater(self._refresh)

    def _refresh(self, _mob):
        now = self.clock()
        index = next((i for i, c in enumerate(self.captions) if c["start"] <= now < c["end"]), None)
        if index != self.index:
            self.index = index
            self.remove(*self.submobjects)
            if index is not None:
                self.add(build_caption(self.captions[index]["text"]))
        if index is None:
            return
        cue = self.captions[index]
        alpha = max(0.0, min(1.0, (now - cue["start"]) / self.fade, (cue["end"] - now) / self.fade))
        plate, lines = self.submobjects[0]
        plate.set_fill(opacity=0.8 * alpha)
        lines.set_opacity(alpha)
