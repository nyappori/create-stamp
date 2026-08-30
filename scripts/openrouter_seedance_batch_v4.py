#!/usr/bin/env python3
import argparse, csv, os, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
API_BASE = "https://openrouter.ai/api/v1"

def load_dotenv(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k,v=s.split("=",1)
        # .env is authoritative for this project.
        os.environ[k.strip()] = v.strip().strip('"').strip("'")

def headers(key, json_content=True):
    h={"Authorization":f"Bearer {key}"}
    if json_content:
        h["Content-Type"]="application/json"
    return h

def main():
    load_dotenv(ROOT/".env")

    ap=argparse.ArgumentParser()
    ap.add_argument("--only-ids",nargs="*")
    ap.add_argument("--out-dir",default="./out_v4")
    args=ap.parse_args()

    key=os.getenv("OPENROUTER_API_KEY")
    base=os.getenv("FIRST_FRAME_BASE_URL","").rstrip("/")
    model=os.getenv("OPENROUTER_MODEL","bytedance/seedance-2.0:free")
    duration=int(os.getenv("OPENROUTER_VIDEO_DURATION","4"))
    resolution=os.getenv("OPENROUTER_VIDEO_RESOLUTION","720p")
    aspect=os.getenv("OPENROUTER_VIDEO_ASPECT_RATIO","1:1")
    poll_interval=int(os.getenv("OPENROUTER_POLL_INTERVAL","8"))
    sleep_between=int(os.getenv("OPENROUTER_SLEEP_BETWEEN_JOBS","3"))

    if not key:
        sys.exit("OPENROUTER_API_KEY is missing in .env")
    if not base:
        sys.exit("FIRST_FRAME_BASE_URL is missing in .env")

    common=(ROOT/"prompts/common_prompt_v4.txt").read_text(encoding="utf-8").strip()
    rows=list(csv.DictReader((ROOT/"prompts/actions_v4.csv").open(encoding="utf-8")))
    selected=set(args.only_ids or [])
    if selected:
        rows=[r for r in rows if r["id"] in selected]

    out=Path(args.out_dir)
    out.mkdir(parents=True,exist_ok=True)

    for n,row in enumerate(rows,1):
        first_url=f"{base}/{row['first_frame_image']}"
        last_url=f"{base}/{row['last_frame_image']}"
        prompt=common+"\n\n"+row["action_prompt"].strip()

        print(f"\n[{n}/{len(rows)}] {row['id']} {row['name']}")
        print("first_frame:", first_url)
        print("last_frame :", last_url)
        print("poster_type:", row["poster_type"])

        payload={
            "model":model,
            "prompt":prompt,
            "duration":duration,
            "resolution":resolution,
            "aspect_ratio":aspect,
            "generate_audio":False,
            "frame_images":[
                {
                    "type":"image_url",
                    "image_url":{"url":first_url},
                    "frame_type":"first_frame"
                },
                {
                    "type":"image_url",
                    "image_url":{"url":last_url},
                    "frame_type":"last_frame"
                }
            ]
        }

        r=requests.post(f"{API_BASE}/videos",headers=headers(key),json=payload,timeout=120)
        if not r.ok:
            raise RuntimeError(f"Submit failed: {r.status_code} {r.text}")
        job=r.json()
        polling_url=job.get("polling_url") or f"{API_BASE}/videos/{job['id']}"

        while True:
            s=requests.get(polling_url,headers=headers(key),timeout=120)
            if not s.ok:
                raise RuntimeError(f"Poll failed: {s.status_code} {s.text}")
            data=s.json()
            print("status=",data.get("status"))
            if data.get("status")=="completed":
                break
            if data.get("status") in {"failed","cancelled","expired"}:
                raise RuntimeError(str(data))
            time.sleep(poll_interval)

        dest=out/f"{row['id']}_{row['name']}.mp4"
        with requests.get(
            f"{API_BASE}/videos/{data['id']}/content?index=0",
            headers=headers(key,False),stream=True,timeout=300
        ) as vr:
            vr.raise_for_status()
            with dest.open("wb") as f:
                for chunk in vr.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        print("saved:",dest)
        time.sleep(sleep_between)

if __name__=="__main__":
    main()
