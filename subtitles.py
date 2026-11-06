"""SRT export for data/cues.json captions (no Manim dependency)."""


def format_srt_time(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def cues_to_srt(captions) -> str:
    blocks = []
    for index, cue in enumerate(captions, start=1):
        blocks.append(
            f"{index}\n{format_srt_time(cue['start'])} --> {format_srt_time(cue['end'])}\n{cue['text']}\n"
        )
    return "\n".join(blocks)
