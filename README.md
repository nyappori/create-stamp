# Duck Sticker v3 patch

既存の `openrouter_duck_pack` に上書きして使う更新パックです。

## 変更点

1. 正面画像1枚だけではなく、向き別4画像を使用
   - front_neutral.png
   - threeq_neutral.png
   - side_neutral.png
   - back_neutral.png

2. 生成動画は、空画面や棒立ちで終わらず、意味の分かる決めポーズで終わるよう強化。

3. LINE用APNGでは最終的に
   `決めポーズ → 動作 → 同じ決めポーズ`
   とする。
   1フレーム目と最終フレームは同じ画像にする。

4. `60 sprint` のような動作は画面外へ完全に消えないよう指示。
   それでも消えた場合はAPNG化前に画面外へ出る部分をカットする。

## GitHub

このpatchの `assets/*.png` を以下へpush:

https://github.com/nyappori/create-stamp/tree/main/assets

`.env` は:

```env
FIRST_FRAME_BASE_URL=https://raw.githubusercontent.com/nyappori/create-stamp/main/assets
```

## 既存フォルダへの適用

このZIPを既存 `openrouter_duck_pack` に展開し、同名ファイルは追加/上書き。

既存の:
`prompts/actions.csv`
はそのまま残してください。

## テスト

```bat
py scripts/openrouter_seedance_batch_v3.py --only-ids 02 15 51 57 60 --out-dir ./out_test_v3
```

## LINE用の決めポーズ処理

例:

```bat
py scripts/prepare_line_frames.py out_test_v3/60_sprint_across_frame.mp4 --poster-time 2.15 --start 0.1 --end 3.1 --fps 4.5
```

生成された `ordered` は:
- 001.png = 決めポーズ
- 中間 = アニメ
- 最後 = 001.png と同じ決めポーズ

最終的に20フレーム以下になるようfps/区間を調整してください。
