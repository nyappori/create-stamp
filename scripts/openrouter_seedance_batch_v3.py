#!/usr/bin/env python3
"""
v3 batch generator.
Uses your EXISTING prompts/actions.csv and adds:
- direction-specific first-frame images
- strengthened common prompt
- action-specific ending rules

Expected project structure after copying this patch into your existing project:
  .env
  prompts/actions.csv                 <- existing 60 prompts
  prompts/common_prompt_v3.txt
  prompts/direction_and_ending_map.csv
  scripts/openrouter_seedance_batch_v3.py
  assets/front_neutral.png etc.
"""
import argparse, csv, os, sys, time
from pathlib import Path
import requests

API="https://openrouter.ai/api/v1"
ROOT=Path(__file__).resolve().parent.parent

def load_env():
    p=ROOT/".env"
    if not p.exists(): return
    for line in p.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("#") or "=" not in s: continue
        k,v=s.split("=",1)
        os.environ[k.strip()]=v.strip().strip('"').strip("'")

def h(key, json=True):
    d={"Authorization":f"Bearer {key}"}
    if json: d["Content-Type"]="application/json"
    return d

def main():
    load_env()
    ap=argparse.ArgumentParser()
    ap.add_argument("--only-ids",nargs="*")
    ap.add_argument("--out-dir",default="./out_v3")
    a=ap.parse_args()

    key=os.getenv("OPENROUTER_API_KEY")
    base=os.getenv("FIRST_FRAME_BASE_URL","").rstrip("/")
    model=os.getenv("OPENROUTER_MODEL","bytedance/seedance-2.0:free")
    duration=int(os.getenv("OPENROUTER_VIDEO_DURATION","4"))
    res=os.getenv("OPENROUTER_VIDEO_RESOLUTION","720p")
    aspect=os.getenv("OPENROUTER_VIDEO_ASPECT_RATIO","1:1")
    poll_seconds=int(os.getenv("OPENROUTER_POLL_INTERVAL","8"))

    if not key: sys.exit("OPENROUTER_API_KEY missing")
    if not base: sys.exit("FIRST_FRAME_BASE_URL missing")

    actions={r["id"]:r for r in csv.DictReader((ROOT/"prompts/actions.csv").open(encoding="utf-8"))}
    rules={r["id"]:r for r in csv.DictReader((ROOT/"prompts/direction_and_ending_map.csv").open(encoding="utf-8"))}
    common=(ROOT/"prompts/common_prompt_v3.txt").read_text(encoding="utf-8").strip()

    ids=sorted(actions)
    if a.only_ids: ids=[i for i in ids if i in set(a.only_ids)]
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)

    for pos,i in enumerate(ids,1):
        action=actions[i]
        rule=rules[i]
        image_url=f"{base}/{rule['first_frame_asset']}"
        prompt=common+"\n\n"+action["action_prompt"].strip()+"\n\n"+rule["ending_instruction"].strip()

        print(f"\n[{pos}/{len(ids)}] {i} {action['name']}")
        print("reference:",image_url)

        payload={
            "model":model,
            "prompt":prompt,
            "duration":duration,
            "resolution":res,
            "aspect_ratio":aspect,
            "generate_audio":False,
            "frame_images":[{
                "type":"image_url",
                "image_url":{"url":image_url},
                "frame_type":"first_frame"
            }]
        }
        r=requests.post(f"{API}/videos",headers=h(key),json=payload,timeout=120)
        if not r.ok: raise RuntimeError(f"{r.status_code} {r.text}")
        job=r.json()
        purl=job.get("polling_url") or f"{API}/videos/{job['id']}"

        while True:
            s=requests.get(purl,headers=h(key),timeout=120)
            if not s.ok: raise RuntimeError(f"{s.status_code} {s.text}")
            data=s.json()
            print("status=",data.get("status"))
            if data.get("status")=="completed": break
            if data.get("status") in {"failed","cancelled","expired"}: raise RuntimeError(str(data))
            time.sleep(poll_seconds)

        dest=out/f"{i}_{action['name']}.mp4"
        with requests.get(f"{API}/videos/{data['id']}/content?index=0",headers=h(key,False),stream=True,timeout=300) as vr:
            vr.raise_for_status()
            with dest.open("wb") as f:
                for c in vr.iter_content(8192):
                    if c: f.write(c)
        print("saved:",dest)

if __name__=="__main__":
    main()
