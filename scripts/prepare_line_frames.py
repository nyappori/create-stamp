#!/usr/bin/env python3
"""
Extract LINE-ready candidate frames while forcing:
poster pose -> animation -> same poster pose

Requires ffmpeg.

Example:
py scripts/prepare_line_frames.py 60_sprint_across_frame.mp4 --poster-time 2.15 --start 0.2 --end 3.15 --fps 5
"""
import argparse, subprocess, shutil
from pathlib import Path

def run(x): subprocess.run(x,check=True)

p=argparse.ArgumentParser()
p.add_argument("video")
p.add_argument("--poster-time",type=float,required=True)
p.add_argument("--start",type=float,default=0)
p.add_argument("--end",type=float,default=4)
p.add_argument("--fps",type=float,default=4.5)
p.add_argument("--out-dir")
a=p.parse_args()

v=Path(a.video)
root=Path(a.out_dir or (v.stem+"_line_frames"))
if root.exists(): shutil.rmtree(root)
root.mkdir()
poster=root/"poster.png"

run(["ffmpeg","-y","-ss",str(a.poster_time),"-i",str(v),"-frames:v","1",str(poster)])
run(["ffmpeg","-y","-ss",str(a.start),"-to",str(a.end),"-i",str(v),"-vf",f"fps={a.fps}",str(root/"anim_%03d.png")])

anim=sorted(root.glob("anim_*.png"))
ordered=root/"ordered"; ordered.mkdir()
shutil.copy2(poster,ordered/"001.png")
n=2
for x in anim:
    shutil.copy2(x,ordered/f"{n:03d}.png"); n+=1
shutil.copy2(poster,ordered/f"{n:03d}.png")
print("frames:",n)
print("output:",ordered)
print("Keep final total <= 20 frames for LINE.")
