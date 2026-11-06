from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from subtitles import cues_to_srt


ROOT = Path(__file__).resolve().parent
SCENE = ROOT / "cachelab_explainer.py"
MEDIA_DIR = ROOT / ".tmp" / "manim_media"
OUTPUT = ROOT / "deliverables" / "cachelab_explainer.mp4"
OUTPUT_SRT = ROOT / "deliverables" / "cachelab_explainer.srt"
CUES = ROOT / "data" / "cues.json"
VOICEOVER = ROOT / "VoiceOver.mp3"
FFMPEG = Path(r"C:\Program Files\ShareX\ffmpeg.exe")
RESOLUTION = "1920,1080"
FPS = "30"
AUDIO_FADE_SECONDS = 0.35


def main() -> None:
    cues = json.loads(CUES.read_text(encoding="utf-8"))
    duration = float(cues["video_duration"])

    env = os.environ.copy()
    global_manim_site = Path(env.get("APPDATA", "")) / "uv" / "tools" / "manim" / "Lib" / "site-packages"
    if global_manim_site.is_dir():
        current_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(global_manim_site) + (os.pathsep + current_pythonpath if current_pythonpath else "")

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "manim",
        "--resolution",
        RESOLUTION,
        "--fps",
        FPS,
        "--disable_caching",
        "--media_dir",
        str(MEDIA_DIR),
        str(SCENE),
        "CacheLabExplainer",
    ]
    subprocess.run(command, cwd=ROOT, env=env, check=True)

    rendered = MEDIA_DIR / "videos" / SCENE.stem / f"{RESOLUTION.split(',')[1]}p{FPS}" / "CacheLabExplainer.mp4"
    if not rendered.is_file():
        raise FileNotFoundError(f"Manim finished, but the expected video was not found: {rendered}")

    if VOICEOVER.is_file():
        if not FFMPEG.is_file():
            raise FileNotFoundError(f"Voiceover mixing needs FFmpeg at {FFMPEG}")
        mixed = MEDIA_DIR / "CacheLabExplainer_with_voice.mp4"
        audio_filter = (
            "[1:a:0]asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-2:LRA=11,apad,"
            f"afade=t=out:st={duration - AUDIO_FADE_SECONDS:.2f}:d={AUDIO_FADE_SECONDS}[aout]"
        )
        mix_command = [
            str(FFMPEG), "-y",
            "-i", str(rendered),
            "-i", str(VOICEOVER),
            "-filter_complex", audio_filter,
            "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "160k",
            "-t", f"{duration:.2f}",
            "-movflags", "+faststart",
            str(mixed),
        ]
        subprocess.run(mix_command, cwd=ROOT, check=True)
        shutil.copy2(mixed, OUTPUT)
    else:
        shutil.copy2(rendered, OUTPUT)
        print(f"No voiceover found at {VOICEOVER}; copied the silent render.")

    OUTPUT_SRT.write_text(cues_to_srt(cues["captions"]), encoding="utf-8")
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    print(f"Created {OUTPUT_SRT}")


if __name__ == "__main__":
    main()
