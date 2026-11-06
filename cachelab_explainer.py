from manim import *
import json
from pathlib import Path

from theme import (
    ACCENT, AMBER, BG, HIT_GREEN, INK, MISS_RED, MUTED, PANEL, PANEL_DEEP, PANEL_HI, SECONDARY,
)
from components import (
    Clock, Lane, ServiceNode, capsule, chart_icon, clock_icon, heading, label, packet,
)
from backdrop import build_backdrop
from captions import CaptionTrack

ROOT = Path(__file__).parent
SCENE_COUNT = 6


class CacheLabExplainer(Scene):
    """Follow the request: one glowing packet is the protagonist of every scene."""

    # ------------------------------------------------------------ setup
    def construct(self):
        self.camera.background_color = BG
        self.metrics = json.loads((ROOT / "data" / "metrics.json").read_text(encoding="utf-8"))
        self.cues = json.loads((ROOT / "data" / "cues.json").read_text(encoding="utf-8"))
        self.spans = [(s["start"], s["end"]) for s in self.cues["scenes"]]

        image, grid, specks = build_backdrop(ROOT / ".tmp")
        self.brand = self._brand()
        self.progress = self._progress()
        captions = CaptionTrack(self.cues["captions"], self.now)
        self.add(image, grid, specks, self.brand, self.progress, captions)
        self.persistent = set(self.mobjects)
        self.progress_state(0, animate=False)

        scenes = [self._opening, self._problem, self._pattern, self._comparison, self._metrics, self._closing]
        for index, scene in enumerate(scenes):
            start, end = self.spans[index]
            self.until(start)
            scene(start, end)
            if index < SCENE_COUNT - 1:
                self.leave(end, index + 1)
        self.until(self.cues["video_duration"])

    # ------------------------------------------------------------ timing helpers
    def now(self):
        """Exact render time in seconds (Manim's own frame clock)."""
        return self.renderer.time

    def until(self, seconds):
        remaining = seconds - self.now()
        if remaining > 1 / 30:
            self.wait(remaining)

    def leave(self, end, next_index):
        """Slide everything that is not persistent out to the left, then advance progress."""
        self.until(end - 0.4)
        leaving = [m for m in self.mobjects if m not in self.persistent]
        self.play(
            *[FadeOut(mob, shift=LEFT * 0.6) for mob in leaving],
            self.progress_state(next_index),
            run_time=0.4,
        )
        self.remove(*leaving)

    def fly(self, pkt, lane, run_time, *also):
        """Move a packet along a lane's route with a short glowing trail."""
        pkt.move_to(lane.route.get_start())
        trail = TracedPath(pkt.get_center, stroke_color=pkt.tint, stroke_width=5, dissipating_time=0.3)
        self.add(trail, pkt)
        self.play(MoveAlongPath(pkt, lane.route), *also, run_time=run_time, rate_func=linear)
        self.remove(trail)

    def pulse(self, node, color=None, run_time=0.55):
        """Ripple ring plus a quick scale bump; returns an animation."""
        color = color or node.accent
        ring = node.card.copy().set_fill(opacity=0).set_stroke(color=color, width=3.5, opacity=0.9)
        self.add(ring)
        return AnimationGroup(
            ring.animate(run_time=run_time).scale(1.3).set_stroke(opacity=0),
            node.animate(run_time=0.35, rate_func=there_and_back).scale(1.045),
        )

    # ------------------------------------------------------------ persistent chrome
    def _brand(self):
        mark = Circle(radius=0.22, color=ACCENT, stroke_width=2.5)
        mark_text = label("C", 18, ACCENT, BOLD).move_to(mark)
        word = label("CACHELAB", 20, MUTED, BOLD).next_to(mark, RIGHT, buff=0.18)
        brand = VGroup(mark, mark_text, word).to_corner(UL, buff=0.45)
        brand.set_z_index(50)
        return brand

    def _progress(self):
        segments = VGroup(*[
            RoundedRectangle(width=0.3, height=0.07, corner_radius=0.035, stroke_width=0, fill_color=PANEL_HI, fill_opacity=1)
            for _ in range(SCENE_COUNT)
        ]).arrange(RIGHT, buff=0.07)
        segments.next_to(self.brand, DOWN, buff=0.16, aligned_edge=LEFT)
        segments.set_z_index(50)
        return segments

    def progress_state(self, active, animate=True):
        updates = [
            segment.animate.set_fill(ACCENT if i <= active else PANEL_HI, opacity=1)
            for i, segment in enumerate(self.progress)
        ]
        if not animate:
            for i, segment in enumerate(self.progress):
                segment.set_fill(ACCENT if i <= active else PANEL_HI, opacity=1)
            return None
        return AnimationGroup(*updates)

    # ------------------------------------------------------------ scene 1: open
    def _opening(self, start, end):
        eyebrow = label("A CACHELAB EXPLAINER", 20, ACCENT, BOLD).move_to([0, 3.3, 0])
        first = label("Cache the read.", 72, INK, BOLD).move_to([0, 2.3, 0])
        second = label("Keep the source.", 72, ACCENT, BOLD).move_to([0, 1.25, 0])
        hint = label("A practical guide to faster repeated API reads", 26, MUTED).move_to([0, 0.45, 0])

        y = -1.15
        api = ServiceNode("API", ACCENT, "api", "request", position=[-4.7, y])
        cache = ServiceNode("Cache", SECONDARY, "cache", "reuse", position=[0, y])
        db = ServiceNode("Database", AMBER, "db", "source of truth", position=[4.7, y])
        lane_a = Lane([-3.23, y, 0], [-1.47, y, 0], ACCENT)
        lane_b = Lane([1.47, y, 0], [3.23, y, 0], AMBER)

        self.play(FadeIn(eyebrow, shift=DOWN * 0.15), run_time=0.3)
        self.play(FadeIn(first, shift=RIGHT * 0.7), run_time=0.5)
        self.play(FadeIn(second, shift=LEFT * 0.7), run_time=0.5)
        self.play(FadeIn(hint, shift=UP * 0.1), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(n, shift=UP * 0.35) for n in (api, cache, db)], lag_ratio=0.25), run_time=0.9)
        self.play(lane_a.draw(), lane_b.draw(), run_time=0.4)

        # Two request loops, with the pulses overlapping the next hop so the open ends on its cue.
        previous_pulse = None
        for _ in range(2):
            pkt = packet(ACCENT)
            self.fly(pkt, lane_a, 0.55, *([previous_pulse] if previous_pulse else []))
            pkt.tint = AMBER
            pkt.set_color(AMBER)
            self.fly(pkt, lane_b, 0.55, self.pulse(cache, SECONDARY, 0.5))
            self.remove(pkt)
            previous_pulse = self.pulse(db, AMBER, 0.5)
        self.play(previous_pulse, run_time=0.4)

    # ------------------------------------------------------------ scene 2: problem
    def _problem(self, start, end):
        title = heading("The problem", "Every repeat goes back to the database")
        y = 0.2
        api = ServiceNode("API", ACCENT, "api", "same read", position=[-4.6, y])
        db = ServiceNode("Database", AMBER, "db", "same source", width=2.9, position=[4.4, y])
        out_lane = Lane([-3.13, y + 0.3, 0], [2.83, y + 0.3, 0], AMBER)
        back_lane = Lane([2.83, y - 0.3, 0], [-3.13, y - 0.3, 0], ACCENT)
        chip = capsule("SAME REQUEST", AMBER, 18).move_to([-0.15, y + 0.85, 0])

        clock = Clock(AMBER, width=3.0).move_to([-4.6, -1.5, 0])
        clock_note = label("synthetic waiting time", 17, MUTED).move_to([-4.6, -2.1, 0])
        meter_label = label("DATABASE LOAD", 17, MUTED, BOLD).move_to([4.4, -1.1, 0])
        meter = VGroup(*[
            RoundedRectangle(width=0.66, height=0.26, corner_radius=0.08, stroke_color=PANEL_HI, stroke_width=1.5, fill_color=PANEL_DEEP, fill_opacity=1)
            for _ in range(4)
        ]).arrange(RIGHT, buff=0.1).move_to([4.4, -1.6, 0])
        load_colors = [AMBER, "#FB923C", "#F97316", MISS_RED]

        self.play(
            FadeIn(title, shift=LEFT * 0.5),
            FadeIn(api, shift=LEFT * 0.5), FadeIn(db, shift=LEFT * 0.5),
            out_lane.draw(), back_lane.draw(),
            FadeIn(clock), FadeIn(clock_note), FadeIn(meter_label), FadeIn(meter),
            run_time=0.9,
        )
        self.play(GrowFromCenter(chip), run_time=0.25)

        round_trip = 1.3
        first_trip = self.now()
        for i in range(4):
            self.until(first_trip + i * round_trip)
            request = packet(AMBER)
            self.fly(request, out_lane, 0.5)
            self.play(
                self.pulse(db, AMBER, 0.45),
                meter[i].animate.set_fill(load_colors[i], opacity=1).set_stroke(color=load_colors[i]),
                run_time=0.3,
            )
            self.remove(request)
            response = packet(ACCENT)
            self.fly(response, back_lane, 0.5, clock.count_to(self.metrics["before_ms"] * (i + 1), 0.5))
            self.remove(response)

    # ------------------------------------------------------------ scene 3: pattern
    def _pattern(self, start, end):
        title = heading("The pattern", "Miss once. Reuse the result next time.")
        y = 0.4
        api = ServiceNode("API", ACCENT, "api", "caller", position=[-4.9, y])
        cache = ServiceNode("Cache", SECONDARY, "cache", "key → value", position=[0, y])
        db = ServiceNode("Database", AMBER, "db", "source of truth", position=[4.9, y])
        req = Lane([-3.43, y + 0.27, 0], [-1.47, y + 0.27, 0], ACCENT)
        back = Lane([-1.47, y - 0.27, 0], [-3.43, y - 0.27, 0], ACCENT)
        fetch = Lane([1.47, y + 0.27, 0], [3.43, y + 0.27, 0], AMBER)
        fill = Lane([3.43, y - 0.27, 0], [1.47, y - 0.27, 0], SECONDARY)

        def pill(number, text):
            content = label(f"{number}   {text}", 24, MUTED, BOLD)
            plate = RoundedRectangle(
                width=2.7, height=0.66, corner_radius=0.2, stroke_color=MUTED, stroke_width=1.5,
                stroke_opacity=0.45, fill_color=PANEL_DEEP, fill_opacity=1,
            )
            return VGroup(plate, content)

        steps = VGroup(pill(1, "MISS"), pill(2, "FILL"), pill(3, "HIT")).arrange(RIGHT, buff=0.5).move_to([0, -1.6, 0])

        def activate(step, color):
            return AnimationGroup(
                step[0].animate.set_stroke(color=color, width=2.8, opacity=1).set_fill(color, opacity=0.2),
                step[1].animate.set_color(color),
            )

        self.play(
            FadeIn(title, shift=LEFT * 0.5),
            LaggedStart(*[FadeIn(n, shift=LEFT * 0.4) for n in (api, cache, db)], lag_ratio=0.2),
            run_time=0.9,
        )
        self.play(req.draw(), back.draw(), fetch.draw(), fill.draw(), FadeIn(steps), run_time=0.6)
        self.play(self.pulse(cache, SECONDARY, 0.7), run_time=0.7)  # "A cache keeps a copy near the API"

        # 1. MISS
        self.until(17.1)
        miss_pkt = packet(MISS_RED)
        miss_stamp = capsule("MISS", MISS_RED, 22).move_to([0, y + 1.45, 0])
        self.play(activate(steps[0], MISS_RED), run_time=0.2)
        self.fly(miss_pkt, req, 0.6)
        self.play(GrowFromCenter(miss_stamp), self.pulse(cache, MISS_RED, 0.5), run_time=0.4)
        miss_pkt.tint = AMBER
        miss_pkt.set_color(AMBER)
        self.fly(miss_pkt, fetch, 0.7, AnimationGroup(Wait(0.4), self.pulse(db, AMBER, 0.4), lag_ratio=1))
        self.remove(miss_pkt)

        # 2. FILL
        self.until(19.2)
        data_pkt = packet(AMBER)
        card = capsule("42 → data", SECONDARY, 20).move_to([0, y + 1.45, 0])
        self.play(FadeOut(miss_stamp, shift=UP * 0.2), activate(steps[1], SECONDARY), run_time=0.25)
        self.fly(data_pkt, fill, 0.65)
        self.remove(data_pkt)
        self.add(card)
        self.play(
            card.animate.move_to([0, y - 0.1, 0]).scale(0.55).set_opacity(0),
            self.pulse(cache, SECONDARY, 0.5),
            run_time=0.5,
        )

        # 3. HIT
        self.until(20.5)
        hit_pkt = packet(HIT_GREEN)
        hit_stamp = capsule("HIT", HIT_GREEN, 22).move_to([0, y + 1.45, 0])
        untouched = label("not touched", 20, HIT_GREEN, BOLD).next_to(db, DOWN, buff=0.18)
        self.play(activate(steps[2], HIT_GREEN), db.fade_back(0.7), FadeIn(untouched), run_time=0.3)
        self.fly(hit_pkt, req, 0.5)
        self.play(GrowFromCenter(hit_stamp), self.pulse(cache, HIT_GREEN, 0.5), run_time=0.35)
        self.fly(hit_pkt, back, 0.5)
        self.play(self.pulse(api, HIT_GREEN, 0.5), run_time=0.4)
        self.remove(hit_pkt)

    # ------------------------------------------------------------ scene 4: comparison
    def _comparison(self, start, end):
        before_ms, after_ms = self.metrics["before_ms"], self.metrics["after_ms"]
        title = heading("Why it helps", "Same answer. A shorter route.")
        row_a, row_b = 0.8, -1.2
        label_a = label("WITHOUT CACHE", 20, MUTED, BOLD).to_edge(LEFT, buff=0.55).set_y(1.85)
        label_b = label("WITH CACHE", 20, ACCENT, BOLD).to_edge(LEFT, buff=0.55).set_y(-0.25)

        api_a = ServiceNode("API", ACCENT, "api", width=2.5, compact=True, position=[-5.4, row_a])
        db_a = ServiceNode("Database", AMBER, "db", width=2.9, compact=True, position=[5.3, row_a])
        api_b = ServiceNode("API", ACCENT, "api", width=2.5, compact=True, position=[-5.4, row_b])

        start_x, end_x = -4.03, 3.73
        out_a = Lane([start_x, row_a + 0.2, 0], [end_x, row_a + 0.2, 0], AMBER)
        back_a = Lane([end_x, row_a - 0.2, 0], [start_x, row_a - 0.2, 0], AMBER)
        length_b = (end_x - start_x) * after_ms / before_ms
        cache_x = start_x + length_b + 0.12 + 1.25
        cache = ServiceNode("Cache", SECONDARY, "cache", width=2.5, compact=True, position=[cache_x, row_b])
        out_b = Lane([start_x, row_b + 0.2, 0], [start_x + length_b, row_b + 0.2, 0], ACCENT)
        back_b = Lane([start_x + length_b, row_b - 0.2, 0], [start_x, row_b - 0.2, 0], ACCENT)

        clock_a = Clock(AMBER, width=2.6).move_to([5.5, 1.85, 0])
        clock_b = Clock(ACCENT, width=2.6).move_to([5.5, -0.25, 0])
        same = capsule("SAME ANSWER", HIT_GREEN, 20).move_to([0.2, -0.25, 0])

        self.play(
            FadeIn(title, shift=LEFT * 0.5), FadeIn(label_a), FadeIn(label_b),
            FadeIn(api_a, shift=LEFT * 0.4), FadeIn(db_a, shift=LEFT * 0.4),
            FadeIn(api_b, shift=LEFT * 0.4), FadeIn(cache, shift=LEFT * 0.4),
            out_a.draw(), back_a.draw(), out_b.draw(), back_b.draw(),
            FadeIn(clock_a), FadeIn(clock_b),
            run_time=0.9,
        )
        self.until(24.2)
        self.play(GrowFromCenter(same), run_time=0.3)

        # The race: same speed, shorter route; clocks count real (synthetic) milliseconds.
        self.until(25.3)
        speed = out_a.route.get_length() / (before_ms / 200 / 2)
        half_a = out_a.route.get_length() / speed
        half_b = out_b.route.get_length() / speed
        pkt_a, pkt_b = packet(AMBER), packet(ACCENT)
        pkt_a.move_to(out_a.route.get_start())
        pkt_b.move_to(out_b.route.get_start())
        self.add(pkt_a, pkt_b)
        self.play(
            Succession(
                MoveAlongPath(pkt_a, out_a.route, run_time=half_a, rate_func=linear),
                AnimationGroup(self.pulse(db_a, AMBER, 0.4), run_time=0.1),
                MoveAlongPath(pkt_a, back_a.route, run_time=half_a, rate_func=linear),
            ),
            Succession(
                MoveAlongPath(pkt_b, out_b.route, run_time=half_b, rate_func=linear),
                AnimationGroup(self.pulse(cache, SECONDARY, 0.4), run_time=0.1),
                MoveAlongPath(pkt_b, back_b.route, run_time=half_b, rate_func=linear),
            ),
            clock_a.count_to(before_ms, 2 * half_a + 0.1),
            Succession(clock_b.count_to(after_ms, 2 * half_b), Wait(2 * half_a + 0.1 - 2 * half_b)),
        )
        self.remove(pkt_a, pkt_b)
        self.play(clock_b.recolor(HIT_GREEN), clock_a.recolor(MISS_RED), run_time=0.4)

    # ------------------------------------------------------------ scene 5: metrics
    def _metrics(self, start, end):
        before = int(self.metrics["before_ms"])
        after = int(self.metrics["after_ms"])
        reduction = (before - after) / before * 100
        title = heading("The result", "Illustrative p95 response time")
        disclosure = capsule("SYNTHETIC EXAMPLE · NOT A BENCHMARK", MUTED, 15).to_corner(UR, buff=0.4)

        axis_x, max_width, max_value = -4.7, 6.0, 450
        row_before, row_after = 1.0, -0.6

        def bar_row(y, value, color):
            width = max_width * value / max_value
            bar = RoundedRectangle(
                width=max(width, 0.14), height=0.72, corner_radius=min(0.16, max(width, 0.14) / 2),
                stroke_width=0, fill_color=color, fill_opacity=0.98,
            )
            bar.move_to([axis_x + bar.width / 2, y, 0])
            value_label = label(f"{value:.0f} ms", 28, INK, BOLD).next_to(bar, RIGHT, buff=0.22)
            return VGroup(bar, value_label)

        def grow(row_group, y, value, color):
            return UpdateFromAlphaFunc(
                row_group,
                lambda mob, alpha: mob.become(bar_row(y, value * alpha, color)),
                rate_func=rate_functions.ease_out_cubic,
            )

        before_row = bar_row(row_before, 0, SECONDARY)
        after_row = bar_row(row_after, 0, ACCENT)
        names = VGroup(
            label("Before", 28, INK, BOLD).next_to([axis_x, row_before, 0], LEFT, buff=0.3),
            label("After", 28, INK, BOLD).next_to([axis_x, row_after, 0], LEFT, buff=0.3),
        )
        axis_y = -1.55
        axis = Line([axis_x, axis_y, 0], [axis_x + max_width, axis_y, 0], color="#496079", stroke_width=2)
        ticks = VGroup()
        for fraction, text in [(0, "0"), (0.5, f"{max_value / 2:.0f}"), (1, f"{max_value} ms")]:
            x = axis_x + max_width * fraction
            tick = Line([x, axis_y - 0.09, 0], [x, axis_y + 0.09, 0], color="#496079", stroke_width=2)
            ticks.add(tick, label(text, 18, MUTED).next_to(tick, DOWN, buff=0.08))
        footnote = label("Illustrative values only · your workload will differ", 20, MUTED).move_to([0, -2.35, 0])

        after_end = axis_x + max_width * after / max_value
        before_end = axis_x + max_width * before / max_value
        delta = DoubleArrow([after_end, 0.2, 0], [before_end, 0.2, 0], color=HIT_GREEN, buff=0, stroke_width=4, tip_length=0.18)
        delta_label = label(f"−{before - after} ms", 24, HIT_GREEN, BOLD).move_to([(after_end + before_end) / 2, -0.12, 0])
        hero = label("0.0%", 88, ACCENT, BOLD).move_to([5.0, 0.55, 0])
        hero_caption = label("lower in this example", 22, MUTED).move_to([5.0, -0.4, 0])

        self.play(
            FadeIn(title, shift=LEFT * 0.5), FadeIn(disclosure, shift=LEFT * 0.5),
            FadeIn(names), Create(axis), FadeIn(ticks), FadeIn(footnote),
            run_time=0.8,
        )
        self.add(before_row, after_row)
        self.until(32.9)
        self.play(grow(before_row, row_before, before, SECONDARY), run_time=1.0)
        self.until(35.2)
        self.play(grow(after_row, row_after, after, ACCENT), run_time=0.9)
        self.play(GrowFromCenter(delta), FadeIn(delta_label, shift=UP * 0.1), run_time=0.4)
        self.add(hero)
        self.play(
            UpdateFromAlphaFunc(
                hero,
                lambda mob, alpha: mob.become(label(f"{reduction * alpha:.1f}%", 88, ACCENT, BOLD).move_to([5.0, 0.55, 0])),
                rate_func=rate_functions.ease_out_cubic,
            ),
            FadeIn(hero_caption),
            run_time=1.2,
        )

    # ------------------------------------------------------------ scene 6: close
    def _closing(self, start, end):
        mark = Circle(radius=0.4, color=ACCENT, stroke_width=3.5).move_to([0, 3.15, 0])
        mark_c = label("C", 30, ACCENT, BOLD).move_to(mark)
        title = label("Cache repeated reads.", 56, INK, BOLD).move_to([0, 2.25, 0])
        statement = label("Keep the database as your source of truth.", 30, ACCENT).move_to([0, 1.4, 0])

        def card(icon, heading_text, sub_text, color, x):
            plate = RoundedRectangle(
                width=5.8, height=2.5, corner_radius=0.26, stroke_color=color, stroke_width=2.5,
                fill_color=PANEL, fill_opacity=1,
            )
            glow = RoundedRectangle(
                width=5.95, height=2.65, corner_radius=0.32, stroke_color=color, stroke_width=10,
                stroke_opacity=0.12, fill_opacity=0,
            )
            icon.move_to([0, 0.55, 0])
            heading_label = label(heading_text, 27, INK, BOLD).move_to([0, -0.3, 0])
            sub = label(sub_text, 20, MUTED).move_to([0, -0.8, 0])
            return VGroup(glow, plate, icon, heading_label, sub).move_to([x, -0.4, 0])

        ttl = clock_icon(SECONDARY, 0.38).scale(1.0)
        left = card(ttl, "Set a freshness rule", "Decide how long a copy stays valid", SECONDARY, -3.3)
        right = card(chart_icon(ACCENT).scale(1.1), "Measure your own workload", "Your numbers matter, not ours", ACCENT, 3.3)
        endline = label("Hit → reuse     ·     Miss → fetch and fill", 24, MUTED).move_to([0, -2.05, 0])

        self.play(
            Create(mark), FadeIn(mark_c), FadeIn(title, shift=LEFT * 0.5), FadeIn(statement, shift=LEFT * 0.5),
            run_time=0.7,
        )
        self.until(40.25)
        self.play(FadeIn(left, shift=UP * 0.35), run_time=0.5)
        self.until(41.6)
        self.play(FadeIn(right, shift=UP * 0.35), run_time=0.5)
        self.until(43.0)
        self.play(FadeIn(endline, shift=UP * 0.15), run_time=0.5)
        self.play(Indicate(mark, color=ACCENT, scale_factor=1.15), run_time=0.8)
