#!/usr/bin/env python3
"""Split a video into clips using a segments JSON file.

Usage:
    python3 split_animations.py <input.mp4> <segments.json> [output_dir]

segments.json is a list of {"start": sec, "end": sec, "file": "name.mp4", ...}.
Clips are re-encoded (H.264 + AAC) so every cut is frame-accurate.
"""
import json
import os
import shutil
import subprocess
import sys


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: install ffmpeg or `pip install imageio-ffmpeg`")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, seg_path = sys.argv[1], sys.argv[2]
    out_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(seg_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    ffmpeg = find_ffmpeg()

    with open(seg_path, encoding="utf-8") as f:
        segments = json.load(f)

    for seg in segments:
        dst = os.path.join(out_dir, seg["file"])
        cmd = [
            ffmpeg, "-y", "-loglevel", "error",
            "-ss", f"{seg['start']:.3f}", "-to", f"{seg['end']:.3f}", "-i", src,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            dst,
        ]
        subprocess.run(cmd, check=True)
        print(f"{seg['file']:40s} {seg['start']:7.2f}s -> {seg['end']:7.2f}s")


if __name__ == "__main__":
    main()
