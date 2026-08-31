#!/usr/bin/env python3
"""
Safe OpenRouter video batch wrapper.

Safety behavior:
1. Loads .env from project root and lets .env override OS environment variables.
2. Checks /api/v1/videos/models and requires the requested model slug to appear EXACTLY.
3. If the slug is not listed (e.g. a :free variant not exposed by the video model API), aborts BEFORE submitting anything.
4. After every completed video job, prints generation_id and usage.cost.
5. If usage.cost > 0 and --allow-paid was NOT supplied, stops the batch immediately.

This is intentionally conservative: it prefers stopping over unexpected billing.
"""
import argparse, csv, os, sys, time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent.parent
API='https://openrouter.ai/api/v1'

def load_dotenv(path: Path):
    if not path.exists(): return
    for line in path.read_text(encoding='utf-8').splitlines():
        s=line.strip()
        if not s or s.startswith('#') or '=' not in s: continue
        k,v=s.split('=',1)
        os.environ[k.strip()] = v.strip().strip('"').strip("'")

def headers(key, json_content=True):
    h={'Authorization':f'Bearer {key}'}
    if json_content: h['Content-Type']='application/json'
    return h

def get_video_models(key):
    r=requests.get(f'{API}/videos/models', headers=headers(key,False), timeout=60)
    r.raise_for_status()
    return r.json().get('data',[])

def get_key_info(key):
    r=requests.get(f'{API}/key', headers=headers(key,False), timeout=60)
    if not r.ok:
        return {'error':f'{r.status_code} {r.text}'}
    return r.json().get('data',{})

def main():
    load_dotenv(ROOT/'.env')
    ap=argparse.ArgumentParser()
    ap.add_argument('--only-ids', nargs='*')
    ap.add_argument('--out-dir', default='./out_safe')
    ap.add_argument('--allow-paid', action='store_true', help='Explicitly allow paid video jobs.')
    ap.add_argument('--actions-csv', default=str(ROOT/'prompts'/'actions_v4.csv'))
    ap.add_argument('--common-prompt', default=str(ROOT/'prompts'/'common_prompt_v4.txt'))
    args=ap.parse_args()

    key=os.getenv('OPENROUTER_API_KEY')
    base=os.getenv('FIRST_FRAME_BASE_URL','').rstrip('/')
    model=os.getenv('OPENROUTER_MODEL','')
    duration=int(os.getenv('OPENROUTER_VIDEO_DURATION','4'))
    resolution=os.getenv('OPENROUTER_VIDEO_RESOLUTION','720p')
    aspect=os.getenv('OPENROUTER_VIDEO_ASPECT_RATIO','1:1')
    poll_interval=int(os.getenv('OPENROUTER_POLL_INTERVAL','8'))

    if not key: sys.exit('OPENROUTER_API_KEY missing in .env')
    if not base: sys.exit('FIRST_FRAME_BASE_URL missing in .env')
    if not model: sys.exit('OPENROUTER_MODEL missing in .env')

    info=get_key_info(key)
    print('Key info before batch:')
    for k in ('is_free_tier','limit','limit_remaining','usage','usage_daily'):
        if k in info: print(f'  {k}: {info.get(k)}')

    models=get_video_models(key)
    ids={m.get('id') for m in models}
    print(f'Requested model: {model}')
    print(f'Exact model exposed by /videos/models: {model in ids}')

    if model not in ids and not args.allow_paid:
        print('\nSAFETY STOP:')
        print(f'  {model!r} is NOT listed exactly by GET /api/v1/videos/models.')
        print('  OpenRouter currently exposes canonical video slugs there, not this variant.')
        print('  No video request was submitted, so this script did not spend credits.')
        print('  Do not use --allow-paid unless you intentionally accept billing.')
        sys.exit(2)

    # Even if exact slug exists, a non-:free model should require explicit paid opt-in.
    if not model.endswith(':free') and not args.allow_paid:
        print('\nSAFETY STOP: model does not end in :free. Use --allow-paid only if intentional.')
        sys.exit(2)

    common=Path(args.common_prompt).read_text(encoding='utf-8').strip()
    rows=list(csv.DictReader(Path(args.actions_csv).open(encoding='utf-8')))
    sel=set(args.only_ids or [])
    if sel: rows=[r for r in rows if r['id'] in sel]
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)

    for n,row in enumerate(rows,1):
        first=f"{base}/{row['first_frame_image']}"
        last=f"{base}/{row['last_frame_image']}"
        prompt=common+'\n\n'+row['action_prompt'].strip()
        print(f"\n[{n}/{len(rows)}] {row['id']} {row['name']}")
        print('first_frame:',first)
        print('last_frame :',last)

        payload={
            'model':model,'prompt':prompt,'duration':duration,
            'resolution':resolution,'aspect_ratio':aspect,'generate_audio':False,
            'frame_images':[
                {'type':'image_url','image_url':{'url':first},'frame_type':'first_frame'},
                {'type':'image_url','image_url':{'url':last},'frame_type':'last_frame'},
            ]
        }
        r=requests.post(f'{API}/videos',headers=headers(key),json=payload,timeout=120)
        if not r.ok: raise RuntimeError(f'Submit failed: {r.status_code} {r.text}')
        job=r.json()
        purl=job.get('polling_url') or f"{API}/videos/{job['id']}"

        while True:
            s=requests.get(purl,headers=headers(key),timeout=120)
            if not s.ok: raise RuntimeError(f'Poll failed: {s.status_code} {s.text}')
            data=s.json(); status=data.get('status')
            print('status=',status)
            if status=='completed': break
            if status in {'failed','cancelled','expired'}: raise RuntimeError(str(data))
            time.sleep(poll_interval)

        cost=float((data.get('usage') or {}).get('cost') or 0)
        print('generation_id:',data.get('generation_id'))
        print('usage.cost   : $%.6f' % cost)

        if cost > 0 and not args.allow_paid:
            print('\nSAFETY STOP: OpenRouter reported a non-zero video cost.')
            print('No further jobs will be submitted.')
            print('Check OpenRouter Logs/Activity for the actual billed model and report it if a :free slug was requested.')
            sys.exit(3)

        dest=out/f"{row['id']}_{row['name']}.mp4"
        with requests.get(f"{API}/videos/{data['id']}/content?index=0",headers=headers(key,False),stream=True,timeout=300) as vr:
            vr.raise_for_status()
            with dest.open('wb') as f:
                for chunk in vr.iter_content(8192):
                    if chunk: f.write(chunk)
        print('saved:',dest)

if __name__=='__main__': main()
