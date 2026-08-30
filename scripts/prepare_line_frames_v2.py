#!/usr/bin/env python3
"""
Prepare LINE animation frames as:

EXACT POSTER PNG -> animation frames -> EXACT SAME POSTER PNG

This guarantees the first and final frames are identical even if the video model
does not return to the requested final pose.

Requires ffmpeg in PATH.

Example:
  py scripts/prepare_line_frames_v2.py \
      out_v4/60_sprint_across_frame.mp4 \
      --poster assets/60_sprint_pose.png \
      --start 0.10 --end 3.90 --fps 4.5
"""

import argparse
import shutil
import subprocess
from pathlib import Path
from PIL import Image

def run(cmd):
    print(" ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--poster", required=True,
                    help="Representative poster PNG. Used as BOTH first and final frame.")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=4.0)
    ap.add_argument("--fps", type=float, default=4.0)
    ap.add_argument("--out-dir")
    args = ap.parse_args()

    video = Path(args.video)
    poster = Path(args.poster)
    if not poster.exists():
        raise SystemExit(f"Poster not found: {poster}")

    out = Path(args.out_dir or (video.stem + "_line_frames"))
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    temp = out / "raw_%03d.png"
    run([
        "ffmpeg", "-y",
        "-ss", str(args.start),
        "-to", str(args.end),
        "-i", str(video),
        "-vf", f"fps={args.fps}",
        str(temp),
    ])

    raw = sorted(out.glob("raw_*.png"))
    if not raw:
        raise SystemExit("No animation frames extracted.")

    # Keep max 18 animation frames because poster frame is inserted at both ends.
    # LINE max is 20 total frames.
    if len(raw) > 18:
        # Uniformly reduce frames.
        indexes = [round(i * (len(raw)-1) / 17) for i in range(18)]
        raw = [raw[i] for i in indexes]

    ordered = out / "ordered"
    ordered.mkdir()

    # Normalize poster to the same dimensions as the first extracted video frame.
    with Image.open(raw[0]) as ref:
        target_size = ref.size

    with Image.open(poster).convert("RGB") as p:
        # Preserve full poster canvas; resize only to video frame dimensions.
        p = p.resize(target_size, Image.Resampling.LANCZOS)
        p.save(ordered / "001.png")

    n = 2
    for frame in raw:
        shutil.copy2(frame, ordered / f"{n:03d}.png")
        n += 1

    # Final frame is byte-for-byte generated from same poster source.
    shutil.copy2(ordered / "001.png", ordered / f"{n:03d}.png")

    print(f"total frames: {n}")
    print(f"first frame: {ordered/'001.png'}")
    print(f"final frame: {ordered/f'{n:03d}.png'}")
    print("The first and final visual pose are identical.")
    print("Keep total <= 20 frames for LINE.")

if __name__ == "__main__":
    main()
