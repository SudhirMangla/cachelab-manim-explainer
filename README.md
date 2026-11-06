# CacheLab Manim Explainer

A short (~46 s, 1080p30) motion-graphics explainer about how a cache works, built with [Manim](https://www.manim.community/) and narrated with a voice-over. The idea is "follow the request": one glowing packet travels through every scene, from client to cache to database and back.

## Companion article

This repository is the supporting code for the article
**[Create Motion Graphics with ChatGPT and Manim](https://developersvoice.com/blog/ai_in_daily_life/create-motion-graphics-with-chatgpt-and-manim/)**
on [Developers Voice](https://developersvoice.com). Read it for the workflow of using ChatGPT to plan and write the Manim scenes.

## What's inside

| File | Purpose |
|---|---|
| `cachelab_explainer.py` | The Manim scene (`CacheLabExplainer`) |
| `render_video.py` | Renders the scene, mixes in the voice-over, writes the MP4 and SRT to `deliverables/` |
| `theme.py` | Shared colors, typography and caption-band constants |
| `components.py` | Reusable helpers: `ServiceNode`, `Lane`, `packet`, `Clock`, `capsule`, `heading`, `label` |
| `backdrop.py` | Persistent animated background |
| `captions.py`, `subtitles.py` | Burned-in captions and SRT export |
| `data/cues.json` | Single timing source: scene and caption timings measured from the voice-over |
| `data/metrics.json` | Synthetic latency values used in the video |
| `VoiceOver.mp3`, `cachelab_voiceover_script.txt` | Narration audio and script |
| `deliverables/` | Rendered `cachelab_explainer.mp4` and `.srt` |

## Run it

Requirements: Python 3.13, Manim Community 0.22.x, and FFmpeg.

```powershell
python render_video.py
```

This renders the scene, normalises and adds the narration, and writes `deliverables/cachelab_explainer.mp4` and `deliverables/cachelab_explainer.srt`. A full render takes several minutes. For a quick low-quality preview:

```powershell
python -m manim -ql --media_dir .tmp\manim_media cachelab_explainer.py CacheLabExplainer
```

If you change the voice-over, re-measure the pauses, update `data/cues.json`, and re-render.

## Note on the data

All latency numbers are **synthetic examples, not a benchmark**. The video states this on screen.
