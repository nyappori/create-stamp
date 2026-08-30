#!/usr/bin/env python3
"""
Prepare frames as:
representative pose -> animation -> same representative pose

Requires ffmpeg in PATH.

Example:
  py scripts/prepare_line_frames.py out/60_sprint_across_frame.mp4 \
      --poster-time 2.5 --start 0 --end 4 --fps 4.5
"""
import argparse, shutil, subprocess
from pathlib import Path

def run(cmd):
    print(" ".join(map(str,cmd)))
    subprocess.run(cmd,check=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--poster-time",type=float,required=True)
    ap.add_argument("--start",type=float,default=0)
    ap.add_argument("--end",type=float,default=4)
    ap.add_argument("--fps",type=float,default=4.5)
    ap.add_argument("--out-dir")
    args=ap.parse_args()

    video=Path(args.video)
    out=Path(args.out_dir or (video.stem+"_line_frames"))
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    poster=out/"poster.png"
    run(["ffmpeg","-y","-ss",str(args.poster_time),"-i",str(video),"-frames:v","1",str(poster)])
    run([
        "ffmpeg","-y","-ss",str(args.start),"-to",str(args.end),"-i",str(video),
        "-vf",f"fps={args.fps}",str(out/"anim_%03d.png")
    ])

    anim=sorted(out.glob("anim_*.png"))
    ordered=out/"ordered"
    ordered.mkdir()
    shutil.copy2(poster,ordered/"001.png")
    n=2
    for p in anim:
        shutil.copy2(p,ordered/f"{n:03d}.png")
        n+=1
    shutil.copy2(poster,ordered/f"{n:03d}.png")

    print("total frames:",n)
    print("output:",ordered)
    print("LINE final APNG: keep total frames <= 20.")

if __name__=="__main__":
    main()
