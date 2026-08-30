# Duck Sticker Pack v5

v4.2 をベースに、**60動作それぞれの決めポーズ用プロンプト**を追加した版です。

## 今回追加したもの

- `prompts/poster_pose_design_60.csv`
  - 60動作分の設計表
- `prompts/poster_pose_design_60.md`
  - 人間が読みやすい一覧
- `prompts/poster_pose_prompts/*.txt`
  - 60個の決めポーズ画像生成用プロンプト
- `prompts/video_prompts/*.txt`
  - 60個の動画生成用フルプロンプト（common + action）
- `scripts/check_poster_assets.py`
  - 60個の決めポーズPNGが揃ったか確認する補助スクリプト

## ポイント

今回のZIPは **60枚の画像そのものを一括生成したものではありません**。
代わりに、60枚の決めポーズPNGを順番に作るための
**設計表 + 個別プロンプト60本** をまとめています。

理由:
- 60枚すべてをいきなり本番品質で作るのは重い
- まず設計を固めた方が後の手戻りが少ない
- OpenRouter / 画像生成AI / ChatGPT Image などで順次作れる

## おすすめの使い方

### 1. まずは優先度の高い決めポーズから作る
おすすめ順:
- 57 slip_and_fall
- 35 turn_away_and_sulk
- 49 march_away_angry
- 29 run_away
- 30 hard_brake
- 31 cry_loudly
- 41 stomp_one_foot
- 60 sprint_across_frame

### 2. 決めポーズPNGのファイル名は設計表どおりにする
例:
- `01_big_jump_pose.png`
- `02_flapping_celebration_pose.png`
- `60_sprint_across_frame_pose.png`

### 3. PNGが揃ったら確認
```bat
py scripts/check_poster_assets.py --assets-dir ./assets_generated
```

### 4. 動画生成時は、そのPNGを first_frame / last_frame に使う
既存の `openrouter_seedance_batch_v4.py` を土台に、
実際の `first_frame_image` / `last_frame_image` を差し替えていく運用を想定しています。

## 既存v4.2ファイルについて

- `common_prompt_v4.txt`
- `actions_v4.csv`
- `openrouter_seedance_batch_v4.py`
- `prepare_line_frames_v2.py`

はそのまま残しています。

## 備考

- 51番のお辞儀は **正面向き** 前提で設計済みです。
- 却下候補の動き案は後で再利用できるよう、元の `actions_original_60.csv` も残しています。
- 将来、良い動画ができたら `extract_poster_asset.py` でその瞬間から決めポーズPNGを作る方法も使えます。
