#!/usr/bin/env python3
"""
Extract one representative poster frame from a generated green-background MP4,
normalize the chroma background to exact #00FF00, crop around the visible content,
and save a clean 1024x1024 PNG.

Example:
  py scripts/extract_poster_asset.py out/31_cry_loudly.mp4 --time 2.25 --output assets/31_cry_pose.png
"""
import argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--time",type=float,required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--target-size",type=int,default=760)
    args=ap.parse_args()

    cap=cv2.VideoCapture(args.video)
    cap.set(cv2.CAP_PROP_POS_MSEC,args.time*1000)
    ok,frame=cap.read()
    cap.release()
    if not ok:
        raise SystemExit("Could not read requested frame.")

    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    arr=frame.astype(np.int16)
    R,G,B=arr[:,:,0],arr[:,:,1],arr[:,:,2]

    # Safe signed arithmetic; do not use uint8 subtraction here.
    green=(G>110)&((G-R)>35)&((G-B)>35)
    arr[green]=[0,255,0]
    arr=np.clip(arr,0,255).astype(np.uint8)

    fg=~((arr[:,:,0]==0)&(arr[:,:,1]==255)&(arr[:,:,2]==0))
    ys,xs=np.where(fg)
    if len(xs)==0:
        raise SystemExit("No foreground found.")

    margin=8
    x1=max(0,xs.min()-margin); x2=min(arr.shape[1],xs.max()+1+margin)
    y1=max(0,ys.min()-margin); y2=min(arr.shape[0],ys.max()+1+margin)

    img=Image.fromarray(arr[y1:y2,x1:x2])
    scale=min(args.target_size/img.width,args.target_size/img.height)
    img=img.resize((int(img.width*scale),int(img.height*scale)),Image.Resampling.LANCZOS)

    canvas=Image.new("RGB",(1024,1024),(0,255,0))
    canvas.paste(img,((1024-img.width)//2,(1024-img.height)//2))

    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(out)
    print(out)

if __name__=="__main__":
    main()
