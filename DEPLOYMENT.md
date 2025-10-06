# Oreza デプロイメント情報

## デプロイ日時
2025年10月4日

## デプロイ方法
Manus Deploy (静的サイトホスティング)

## ビルド情報
- フレームワーク: React 19 + Vite 6
- ビルドサイズ: 432KB
- 最適化: Production build with minification

## デプロイ済みファイル
```
dist/
├── index.html (0.46 KB)
├── favicon.ico (16 KB)
└── assets/
    ├── index-DZYaHmts.css (88.86 KB)
    └── index-DU9R8qps.js (322.56 KB)
```

## 機能一覧
- チャットインターフェース
- 画像生成UI（Midnight Journeyモード対応）
- Web検索UI
- カメラUI
- テーマ切替（ライト/ダーク/Midnight Journey）
- レスポンシブデザイン
- モバイル最適化（44pxタッチターゲット）

## 技術スタック
- React 19
- Vite 6
- Tailwind CSS
- shadcn/ui
- Zustand (状態管理)
- Lucide Icons

## 今後の拡張
- バックエンドAPI連携
- ComfyUI統合
- 実際の画像生成機能
- LLM統合（Ollama/OpenAI）
- Web検索機能（Tavily/SerpAPI）

## メンテナンス
- GitHubリポジトリ: https://github.com/nori368/oreza
- 開発ブランチ: dev
- 本番ブランチ: main
