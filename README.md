# Oreza AI

次世代の対話型AI画像生成プラットフォーム

## 概要

Orezaは、ユーザーとAIが協働して創造的な作品を生み出すための、革新的なUI/UXを備えたプラットフォームです。

### 主な特徴

- **対話型クリエイティブプロセス**: 一発勝負ではなく、AIと対話しながら作品を進化させる
- **Midnight Journeyモード**: シネマティックな暗部表現とネオンアクセントを特徴とする独自のスタイル
- **直感的なUI**: モバイルファーストのデザインで、適切なタッチターゲット（44px）を確保
- **セッション管理**: 各画像にセッションIDを割り当て、差分指示を容易に

## 技術スタック

### フロントエンド
- React 19 + Vite
- Tailwind CSS
- shadcn/ui コンポーネント
- Zustand (状態管理)
- Lucide Icons

### バックエンド（予定）
- FastAPI
- ComfyUI連携
- Ollama / Oreza AI (LLM)
- Tavily / SerpAPI (Web検索)

## プロジェクト構造

```
oreza/
├── apps/
│   ├── web/              # React フロントエンド
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Chat/
│   │   │   │   ├── ImageGen/
│   │   │   │   ├── Camera/
│   │   │   │   ├── Search/
│   │   │   │   └── UI/
│   │   │   ├── pages/
│   │   │   └── lib/
│   │   │       ├── api.js
│   │   │       ├── state.js
│   │   │       └── themes.js
│   │   └── ...
│   └── api/              # FastAPI バックエンド（未実装）
├── infra/
│   └── docker/
├── workflows/            # ComfyUI ワークフロー
├── .env.example
└── README.md
```

## セットアップ

### 前提条件

- Node.js 22.x
- pnpm

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/nori-diamond/oreza.git
cd oreza

# フロントエンドの依存関係をインストール
cd apps/web
pnpm install

# 開発サーバーを起動
pnpm run dev
```

ブラウザで `http://localhost:5173` を開きます。

### 環境変数

`.env.example` をコピーして `.env` を作成し、必要な値を設定してください。

```bash
cp .env.example .env
```

## 実装済み機能

### UI/UX改善
- ✅ 下部固定の入力フォーム
- ✅ 適切なボタン余白（44px タッチターゲット）
- ✅ Shift+Enter で改行、Enter で送信
- ✅ 下スクロールボタン（自動表示/非表示）

### Midnight Journeyモード
- ✅ テーマ切替UI
- ✅ ダークテーマ with ネオンアクセント
- ✅ プロンプト自動拡張（シネマティックライティング等）
- ✅ 画像生成時のスタイル適用

### 基本機能
- ✅ チャットインターフェース
- ✅ 画像生成UI
- ✅ モード切替（チャット/画像生成/Web検索/カメラ）
- ⏳ バックエンドAPI連携（未実装）

## 今後の開発予定

### バックエンド
- [ ] FastAPI サーバーの実装
- [ ] ComfyUI連携
- [ ] LLMプロバイダ統合（Ollama/OpenAI）
- [ ] Web検索機能（Tavily/SerpAPI）

### フロントエンド
- [ ] カメラ機能の実装
- [ ] Web検索機能の実装
- [ ] 画像履歴ギャラリー
- [ ] 差分編集UI
- [ ] ストーリーモード

### インフラ
- [ ] Docker構成
- [ ] CI/CD パイプライン
- [ ] デプロイメント設定

## ライセンス

MIT

## 貢献

プルリクエストを歓迎します！大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 作者

nori-diamond
