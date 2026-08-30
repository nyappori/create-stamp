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


## v4.1追加修正

- `assets/front_bow_pose.png` の左側に混入していた白線を除去。完全に描き直したクリーン版へ差し替え。
- `assets/back_sulk_pose.png` に混入していた白い謎エフェクトを除去。今回はまず破綻しないよう、クリーンな背面ポーズ版へ差し替え。
  - 将来的に「より sulk 感のある背面決めポーズ」が必要なら、良い動画フレームから再抽出してください。
- その他ファイルは v4 と同じです。


## v4.2 修正

### back_sulk_pose.png
旧 `back_sulk_pose.png` は白い謎エフェクトが混入していたため完全削除しました。

ID 35 / 49 は当面:
- first_frame_image = back_neutral.png
- last_frame_image = back_neutral.png

を使います。

これは「壊れた決めポーズを使うより安全」を優先した暫定対応です。
35 / 49 の動画から良い背面いじけ・怒りポーズが生成できたら、
`extract_poster_asset.py` で専用ポスターPNGを作り、
`actions_v4.csv` の画像名を差し替えるのが理想です。

### 生成動画の最後が参照ポーズと一致しない問題
Seedanceへ同じPNGを first_frame / last_frame として渡しても、
生成結果が最終フレームで完全一致するとは限りません。

そのため `scripts/prepare_line_frames_v2.py` を追加しました。

60番の例:

```bat
py scripts/prepare_line_frames_v2.py ^
  out_v4_test/60_sprint_across_frame.mp4 ^
  --poster assets/60_sprint_pose.png ^
  --start 0.1 ^
  --end 3.9 ^
  --fps 4
```

最終出力は必ず:

1. `001.png` = 60_sprint_pose.png
2. 中間 = 動画
3. 最後 = 001.png と同じ決めポーズ

になります。

これにより、LINEトーク上の静止表示とアニメーション終了時を
確実に同じリアクションポーズへできます。
