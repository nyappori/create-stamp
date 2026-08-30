#!/usr/bin/env python3
import argparse
import csv
import os
import sys
import time
from pathlib import Path

import requests


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE pairs from .env without external dependencies."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key] = value


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "bytedance/seedance-2.0:free")
DEFAULT_DURATION = int(os.getenv("OPENROUTER_VIDEO_DURATION", "4"))
DEFAULT_RESOLUTION = os.getenv("OPENROUTER_VIDEO_RESOLUTION", "720p")
DEFAULT_ASPECT_RATIO = os.getenv("OPENROUTER_VIDEO_ASPECT_RATIO", "1:1")
DEFAULT_POLL_INTERVAL = int(os.getenv("OPENROUTER_POLL_INTERVAL", "8"))
DEFAULT_SLEEP_BETWEEN_JOBS = int(os.getenv("OPENROUTER_SLEEP_BETWEEN_JOBS", "3"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_prompts(csv_path: Path):
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_headers(api_key: str):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openrouter.ai",
        "X-Title": "duck-sticker-generator",
    }


def submit_job(api_key, model, prompt, first_frame_url, duration, resolution, aspect_ratio):
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": False,
        "frame_images": [
            {
                "type": "image_url",
                "image_url": {"url": first_frame_url},
                "frame_type": "first_frame",
            }
        ],
    }
    r = requests.post(
        f"{API_BASE}/videos",
        headers=build_headers(api_key),
        json=payload,
        timeout=120,
    )
    if not r.ok:
        raise RuntimeError(f"Submit failed: {r.status_code} {r.text}")
    return r.json()


def poll_job(api_key, polling_url, interval):
    while True:
        r = requests.get(polling_url, headers=build_headers(api_key), timeout=120)
        if not r.ok:
            raise RuntimeError(f"Poll failed: {r.status_code} {r.text}")
        data = r.json()
        status = data.get("status")
        print(f"status={status} id={data.get('id')}")
        if status == "completed":
            return data
        if status in {"failed", "cancelled", "expired"}:
            raise RuntimeError(f"Job ended with status={status}: {data}")
        time.sleep(interval)


def download_video(api_key, job_id, output_path: Path):
    url = f"{API_BASE}/videos/{job_id}/content?index=0"
    with requests.get(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        stream=True,
        timeout=300,
    ) as r:
        if not r.ok:
            raise RuntimeError(f"Download failed: {r.status_code} {r.text}")
        with output_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="Generate OpenRouter videos from the duck action prompt CSV.")
    parser.add_argument("--api-key", default=os.getenv("OPENROUTER_API_KEY"))
    parser.add_argument("--first-frame-url", default=os.getenv("FIRST_FRAME_URL"))
    parser.add_argument("--common-prompt", default=str(PROJECT_ROOT / "prompts" / "common_prompt.txt"))
    parser.add_argument("--actions-csv", default=str(PROJECT_ROOT / "prompts" / "actions.csv"))
    parser.add_argument("--out-dir", default="./openrouter_videos")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION)
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO)
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL)
    parser.add_argument("--sleep-between-jobs", type=int, default=DEFAULT_SLEEP_BETWEEN_JOBS)
    parser.add_argument("--only-ids", nargs="*", help="Generate only these IDs, e.g. 01 02 51")
    args = parser.parse_args()

    if not args.api_key:
        print("OPENROUTER_API_KEY is missing. Put it in project-root .env", file=sys.stderr)
        sys.exit(1)
    if not args.first_frame_url:
        print("FIRST_FRAME_URL is missing. Put a public HTTPS image URL in project-root .env", file=sys.stderr)
        sys.exit(1)

    common_prompt = read_text(Path(args.common_prompt))
    actions = load_prompts(Path(args.actions_csv))
    selected_ids = set(args.only_ids or [])
    if selected_ids:
        actions = [a for a in actions if a["id"] in selected_ids]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, row in enumerate(actions, start=1):
        full_prompt = common_prompt + "\n\n" + row["action_prompt"].strip()
        print(f"\n[{idx}/{len(actions)}] Generating {row['id']} {row['name']}")
        job = submit_job(
            api_key=args.api_key,
            model=args.model,
            prompt=full_prompt,
            first_frame_url=args.first_frame_url,
            duration=args.duration,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
        )
        polling_url = job.get("polling_url") or f"{API_BASE}/videos/{job['id']}"
        final = poll_job(args.api_key, polling_url, args.poll_interval)
        output_path = out_dir / f"{row['id']}_{row['name']}.mp4"
        download_video(args.api_key, final["id"], output_path)
        print(f"saved: {output_path}")
        time.sleep(args.sleep_between_jobs)


if __name__ == "__main__":
    main()
