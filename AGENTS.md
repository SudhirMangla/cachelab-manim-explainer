# Repository Guidelines

## Project Structure

This repository produces a short CacheLab motion-graphics explainer based on `create-motion-graphics-with-chatgpt-and-manim.md`.

- `cachelab_explainer.py` contains the Manim explainer scene ("follow the request": one glowing packet travels through every scene). `render_video.py` renders it, mixes the voice-over, and writes the MP4 and SRT into `deliverables/`.
- `theme.py` contains shared colors, typography and the caption-band constants. Do not hard-code hex colors in scenes.
- `components.py` contains reusable Manim helpers: `ServiceNode` (icon cards), `Lane` (glowing arrows), `packet`, `Clock`, `capsule`, `heading`, `label`.
- `backdrop.py` builds the persistent background (radial gradient, drifting grid, floating specks).
- `captions.py` draws the burned-in captions from `data/cues.json`; `subtitles.py` exports the SRT.
- `data/metrics.json` provides the explicitly synthetic latency values used in the explainer.
- `data/cues.json` is the single timing source: scene start/end times and caption text/timings, measured from `VoiceOver.mp3` (FFmpeg `silencedetect`). Scenes sync with `self.until(<seconds>)` against Manim's render clock; never use hard-coded `wait()` values.
- `VISUAL_IMPROVEMENT_PLAN.md` records the review and task list behind this design.
- `deliverables/` is the destination for generated media. Keep generated outputs out of source files.

There is no test suite or separate assets directory at present.

## Build and Development

Run the renderer from the repository root:

```powershell
python render_video.py
```

It renders `CacheLabExplainer` with Manim at 1080p30 (burned-in captions included), then adds the narration from `VoiceOver.mp3` (loudness-normalised, 0.35 s fade-out) and writes `deliverables/cachelab_explainer.mp4` plus `deliverables/cachelab_explainer.srt`. Intermediate files go under `.tmp/manim_media/`. A full render takes several minutes; for quick checks use `python -m manim -ql --media_dir .tmp	est_media cachelab_explainer.py CacheLabExplainer`. To inspect the encoded file, run:

```powershell
& 'C:\Program Files\ShareX\ffmpeg.exe' -i deliverables/cachelab_explainer.mp4 -f null NUL
```

This reports duration, dimensions, frame rate, and codecs. The final video includes AAC narration and should last about 46.1 s (`video_duration` in `data/cues.json`). If the voice-over changes, re-measure the pauses, update `data/cues.json`, and re-render.

### Manim on this machine

Manim Community 0.22.1 is installed globally with `uv tool install manim`. Its uv environment is at `%APPDATA%\uv\tools\manim`, and the command shim is `%USERPROFILE%\.local\bin\manim.exe`. Check it from PowerShell with:

```powershell
manim --version
```

In the Codex Windows session, launching the shim may fail with `Access is denied`, even though Manim is installed. In that case, use the global tool's site-packages through the active Python 3.13 interpreter:

```powershell
$env:PYTHONPATH = Join-Path $env:APPDATA 'uv\tools\manim\Lib\site-packages'
python -m manim --version
python -m manim -qm --media_dir .tmp\manim_media path\to\scene.py SceneName
```

Run the render command from the repository root and replace `path\to\scene.py` and `SceneName` with the scene file and class being rendered. Keep temporary Manim output under `.tmp`; use `deliverables/` for final media. `render_video.py` now invokes the Manim scene and handles the global uv package path used on this machine.

## Style and Naming

Use Python 4-space indentation, descriptive `snake_case` function and variable names, and uppercase names for shared theme constants. Keep reusable visual helpers in `components.py`, design tokens in `theme.py`, and input measurements in JSON rather than duplicating them in animation logic. Use the existing palette and Arial font unless a deliberate design change requires updating the theme. Keep diagrams above `CAPTION_TOP_Y` so they never collide with captions, and keep on-screen text at 18 pt or larger. Label sample measurements as synthetic; do not present them as a benchmark.

## Validation

No automated tests or formatter are configured. For rendering changes, run `python render_video.py` to rebuild the final explainer. Inspect the MP4 with FFmpeg and review representative frames for visual quality and timing. Check any changed values in `data/metrics.json` for positive millisecond values and preserve the synthetic-data disclosure (the "SYNTHETIC EXAMPLE · NOT A BENCHMARK" pill and the word "Synthetic" in the captions). Review frames at roughly 0:02, 0:09, 0:18, 0:27, 0:36 and 0:44, and confirm the caption text still matches the audio.

## Commits and Pull Requests

No Git commit-message convention is established in the available history. Use a short imperative subject (for example, `Improve cache hit animation`). Pull requests should describe the visual or data change, include the render command, and attach a preview or representative frames when motion or layout changes.
