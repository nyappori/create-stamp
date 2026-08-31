# OpenRouter free retry pack v1

このZIPは、OpenRouterを使っていた頃のスクリプト・画像・60種プロンプトをまとめ直した再配布パックです。

## 含まれるもの
- scripts/openrouter_seedance_batch_v4.py
  - 以前の一括実行スクリプト
- scripts/openrouter_seedance_batch_safe.py
  - モデル名の exact match と usage.cost を確認し、想定外課金の可能性があれば止める安全版
- scripts/list_video_models.py
  - OpenRouter の video model 一覧確認用
- prompts/video_prompts/*.txt
  - 01〜60 の個別動画プロンプト
- prompts/actions_v4.csv
  - 01〜60 の一覧CSV
- assets/heroes/*.png
  - 01〜60 の first/last frame 用ヒーロー画像
- assets/base/*.png
  - front/side/bow/sprint などの参考画像・基礎素材

## 使い方の考え方
スクリプトはローカル画像を直接送るのではなく、`FIRST_FRAME_BASE_URL` で公開URLを指定して参照します。
そのため `assets/heroes/` を GitHub などへ置き、raw URL を `.env` に設定して使います。

例:
FIRST_FRAME_BASE_URL=https://raw.githubusercontent.com/<user>/<repo>/main/assets/heroes

## 最低限の手順
1. ZIPを展開
2. `.env.example` を `.env` にコピー
3. `OPENROUTER_API_KEY` を設定
4. `FIRST_FRAME_BASE_URL` を設定
5. `OPENROUTER_MODEL` を試したいモデル名に設定
6. 最初は `openrouter_seedance_batch_safe.py` で 01 だけ試す

## 実行例
### モデル一覧
```bat
py scripts\list_video_models.py
```

### 安全版で1件テスト
```bat
py scripts\openrouter_seedance_batch_safe.py --only-ids 01 --out-dir .\out_safe_01
```

### 元スクリプトで01〜60
```bat
py scripts\openrouter_seedance_batch_v4.py --only-ids 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 --out-dir .\out_01_60
```

## 注意
- 以前 `:free` を付けても実際には課金扱いになった可能性があるため、最初は安全版推奨です。
- `assets/heroes/` のファイル名は `01.png`〜`60.png` です。
