#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import requests


def load_dotenv(path: Path) -> None:
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

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("OPENROUTER_API_KEY is missing. Put it in project-root .env", file=sys.stderr)
    sys.exit(1)

r = requests.get(
    "https://openrouter.ai/api/v1/videos/models",
    headers={"Authorization": f"Bearer {API_KEY}"},
    timeout=60,
)
r.raise_for_status()
data = r.json().get("data", [])
for m in data:
    print(m.get("id"))
    print(f"  durations: {m.get('supported_durations')}")
    print(f"  resolutions: {m.get('supported_resolutions')}")
    print(f"  aspect ratios: {m.get('supported_aspect_ratios') or m.get('supported_sizes')}")
    print(f"  frame images: {m.get('supported_frame_images')}")
    print()
