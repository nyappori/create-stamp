# OpenRouter Duck Sticker Pack

## セットアップ

### 1. `.env` を作る

プロジェクト直下で `.env.example` を `.env` にコピーします。

Windows CMD:

```bat
copy .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` を編集します。

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
FIRST_FRAME_URL=https://raw.githubusercontent.com/your-user/your-repo/main/assets/duck_reference_green.png
OPENROUTER_MODEL=bytedance/seedance-2.0:free
OPENROUTER_VIDEO_DURATION=4
OPENROUTER_VIDEO_RESOLUTION=720p
OPENROUTER_VIDEO_ASPECT_RATIO=1:1
```

スクリプトはプロジェクト直下の `.env` を自動読み込みします。追加ライブラリは不要です。

`.env` にはAPIキーが入るため、Gitにはコミットしないでください。`.gitignore` に最初から `.env` を追加してあります。

### 2. FIRST_FRAME_URLを用意する

`assets/duck_reference_green.png` をpublic GitHubリポジトリなどに置き、Raw URLを `.env` の `FIRST_FRAME_URL` に入れます。

例:

```env
FIRST_FRAME_URL=https://raw.githubusercontent.com/USER/REPO/main/assets/duck_reference_green.png
```

## 実行

利用可能な動画モデルを確認:

```bash
python scripts/list_video_models.py
```

まず大ジャンプ1本だけ:

```bash
python scripts/openrouter_seedance_batch.py --only-ids 01 --out-dir ./out_test
```

動きの違う5本を試す:

```bash
python scripts/openrouter_seedance_batch.py --only-ids 01 05 28 51 57 --out-dir ./out_test5
```

全60本:

```bash
python scripts/openrouter_seedance_batch.py --out-dir ./out_all
```

## ファイル構成

- `assets/duck_reference_green.png` : 動画生成用1羽画像
- `assets/duck_character_sheet.png` : キャラクターシート
- `prompts/common_prompt.txt` : 共通プロンプト
- `prompts/actions.csv` : 60動作の個別プロンプト
- `prompts/sample_prompts.md` : コピペ用サンプル
- `scripts/list_video_models.py` : モデル確認
- `scripts/openrouter_seedance_batch.py` : 生成・ポーリング・MP4保存
- `.env.example` : 設定例
- `.gitignore` : APIキー誤コミット防止
