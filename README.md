# Digital Security — YouTube Shorts 自動投稿システム

35本のデジタルセキュリティTipsを1日1本ずつ自動投稿します。

## 投稿時間
- 毎日 JST 22:00（UTC 13:00）

## GitHub Secrets（cocktaillog-youtubeと共通）
| Secret名 | 内容 |
|---|---|
| `GCP_API_KEY` | Google Cloud TTS APIキー |
| `YOUTUBE_CLIENT_ID` | YouTube OAuth クライアントID |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth クライアントシークレット |
| `YOUTUBE_REFRESH_TOKEN` | YouTube リフレッシュトークン |

## アセット配置
```
assets/
  illustrations/
    img_tech.png      ← スマホ・AI・社会カテゴリ用（1枚）
    img_warning.png   ← 写真・QRコードカテゴリ用（1枚）
    img_calm.png      ← デジタル全般・政府レポカテゴリ用（1枚）
  bgm/
    bgm_tech.mp3      ← テクノロジー系BGM
    bgm_warning.mp3   ← 警告系BGM
    bgm_calm.mp3      ← 落ち着いたBGM
```

## 動画仕様
- 解像度: 1080 × 1920 (9:16)
- 尺: 20秒
- ナレーション: 英語（Google Cloud TTS）
- カテゴリ別BGM: 3種類
- 画像: カテゴリ別3種類

## BGM・画像の振り分け
| BGM | 画像 | カテゴリ |
|---|---|---|
| bgm_tech.mp3 | img_tech.png | スマホ・AI・社会 |
| bgm_warning.mp3 | img_warning.png | 写真・QRコード |
| bgm_calm.mp3 | img_calm.png | デジタル全般・政府レポ |
