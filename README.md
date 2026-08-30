# Duck Sticker Pack v4

前回の壊れた assets を使わない完全修正版です。

## 重要な修正

- キャラクターシートの白背景を雑に透明化する処理を廃止。
- `よこ` / `うしろ` / `基本4方向` などの文字が参照画像に入らないよう、個別PNG化。
- 背景は動画参照用に #00FF00 の均一グリーンへ正規化。
- 影・床・ラベルを参照画像に含めない。
- 01 / 02 / 15 / 51 / 57 / 60 は、実際に生成した動画から良い瞬間を抜いて「決めポーズ画像」を作成。
- OpenRouterには同じ決めポーズ画像を `first_frame` と `last_frame` の両方へ渡す。
  → 最初と最後を同じリアクションに寄せる。
- プロンプトでも「画面外に消えない」「棒立ちに戻らない」「同じ決めポーズで終わる」を明示。

## GitHubへpush

このZIPの `assets/` を以下へそのまま配置してください。

`https://github.com/nyappori/create-stamp/tree/main/assets`

`.env`:

```env
OPENROUTER_API_KEY=...
FIRST_FRAME_BASE_URL=https://raw.githubusercontent.com/nyappori/create-stamp/main/assets
OPENROUTER_MODEL=bytedance/seedance-2.0:free
OPENROUTER_VIDEO_DURATION=4
OPENROUTER_VIDEO_RESOLUTION=720p
OPENROUTER_VIDEO_ASPECT_RATIO=1:1
OPENROUTER_POLL_INTERVAL=8
OPENROUTER_SLEEP_BETWEEN_JOBS=3
```

## 60番だけ再テスト

```bat
py scripts/openrouter_seedance_batch_v4.py --only-ids 60 --out-dir ./out_v4_test
```

実行時に次の2行が同じ `60_sprint_pose.png` ならOKです。

```text
first_frame: .../60_sprint_pose.png
last_frame : .../60_sprint_pose.png
```

## 60個のポスター画像について

現在、専用の決めポーズを確定済みなのは主にテスト済みの
`01 / 02 / 15 / 51 / 57 / 60` です。

その他のIDはまず向きに合った綺麗なベース画像を割り当てています。
良い動画が生成できたら、以下でその動画のベスト瞬間を新しい決めポーズPNGにできます。

```bat
py scripts/extract_poster_asset.py out_v4/31_cry_loudly.mp4 --time 2.2 --output assets/31_cry_pose.png
```

その後 `prompts/actions_v4.csv` の
`first_frame_image` と `last_frame_image` を `31_cry_pose.png` に変更すると、
以後はその決めポーズから始まり、同じ決めポーズへ戻る生成ができます。

## LINE用APNG

最終的には
`決めポーズ → 動画 → 同じ決めポーズ`
にします。

```bat
py scripts/prepare_line_frames.py out_v4_test/60_sprint_across_frame.mp4 --poster-time 2.5 --fps 4.5
```

LINE用の最終フレーム数は20以下に調整してください。
