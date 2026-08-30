#!/usr/bin/env python3
"""
Validate and organize 60 poster pose PNGs.

Usage:
  py scripts/check_poster_assets.py --assets-dir ./assets_generated

What it does:
- reads prompts/poster_pose_design_60.csv
- checks which expected PNG files exist
- outputs a coverage report CSV
"""
import argparse, csv
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--assets-dir', required=True)
    ap.add_argument('--design-csv', default=str(Path(__file__).resolve().parent.parent/'prompts'/'poster_pose_design_60.csv'))
    args=ap.parse_args()

    assets=Path(args.assets_dir)
    rows=list(csv.DictReader(open(args.design_csv, encoding='utf-8')))
    report=[]
    for row in rows:
        p=assets/row['poster_image_file']
        report.append({
            'id': row['id'],
            'name': row['name'],
            'poster_image_file': row['poster_image_file'],
            'exists': 'yes' if p.exists() else 'no',
        })
    out=assets/'poster_asset_coverage.csv'
    with out.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=report[0].keys())
        w.writeheader(); w.writerows(report)
    print(out)

if __name__=='__main__':
    main()
