# Oreza プロジェクトサマリー

## 実装完了日
2025年10月4日

## プロジェクト概要

Orezaは、ユーザーとAIが協働して創造的な作品を生み出すための、次世代対話型AI画像生成プラットフォームです。「AIに作らせる」受動的な体験から、「AIと共作する」能動的な体験への転換を目指しています。

## 実装済み機能

### Phase 1: プロジェクト構造の確立
- ✅ モノレポ構成（apps/web, apps/api, infra, workflows）
- ✅ React + Vite + Tailwind CSS + shadcn/ui
- ✅ Zustand状態管理
- ✅ Git初期化とGitHubリポジトリ作成

### Phase 2: UI改善の実装
- ✅ **下部固定の入力フォーム**
  - `sticky bottom-0` による固定配置
  - `safe-area-inset-bottom` でモバイル対応
  - メインコンテンツに `pb-48` で余白確保
  
- ✅ **適切なボタン余白**
  - すべてのインタラクティブ要素に44pxのタッチターゲット
  - `h-11 w-11` (44px) の統一サイズ
  - 周囲に適切な `gap-2` でスペース確保
  
- ✅ **Shift+Enter改行、Enter送信**
  - `onKeyDown` イベントで `e.shiftKey` を判定
  - ヘルパーテキストでユーザーに明示
  
- ✅ **下スクロールボタン**
  - スクロール位置を監視して自動表示/非表示
  - スムーズスクロールアニメーション
  - `fixed right-6 bottom-24` で配置

### Phase 3: Midnight Journeyモードの実装
- ✅ **テーマシステム**
  - `lib/themes.js` でテーマ定義
  - CSS変数による動的テーマ切替
  - `data-theme` 属性でスタイル適用
  
- ✅ **Midnight Journeyテーマ**
  - 暗部表現：`oklch(0.08 0.01 240)` ベース
  - ネオンアクセント：紫-青 `oklch(0.65 0.2 280)`
  - 微細なグロー効果
  
- ✅ **プロンプト自動拡張**
  - `getThemePromptModifiers()` 関数
  - シネマティックライティング、ネオングロー等のキーワード自動追加
  - ネガティブプロンプトの自動生成
  
- ✅ **画像生成UI**
  - Midnight Journeyモードトグル
  - プロンプト入力エリア
  - 生成ボタン（適切な余白とサイズ）
  - 画像ギャラリー

### コンポーネント構成

```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatContainer.jsx    # チャット全体のコンテナ
│   │   ├── ChatInput.jsx        # 入力フォーム（固定、余白最適化）
│   │   └── ChatMessage.jsx      # メッセージ表示
│   ├── ImageGen/
│   │   ├── ImageGenerator.jsx   # 画像生成UI（MJモード対応）
│   │   └── ImageGallery.jsx     # 生成画像ギャラリー
│   └── UI/
│       ├── Header.jsx            # ヘッダー（モード切替）
│       ├── ScrollToBottomButton.jsx  # 下スクロールボタン
│       └── ThemeSwitcher.jsx     # テーマ切替ドロップダウン
└── lib/
    ├── api.js      # APIクライアント
    ├── state.js    # Zustand状態管理
    └── themes.js   # テーマ定義と適用
```

## 技術的ハイライト

### 1. モバイルファーストUI
すべてのインタラクティブ要素が44px以上のタッチターゲットを確保し、モバイルでの操作性を最優先に設計しました。

### 2. テーマシステムの柔軟性
CSS変数とJavaScriptの組み合わせにより、ランタイムでのテーマ切替を実現。将来的に無限のテーマ追加が可能です。

### 3. プロンプトエンジニアリングの自動化
ユーザーは簡潔なプロンプトを入力するだけで、テーマに応じた詳細なプロンプトが自動生成されます。

## 未実装機能（今後の開発予定）

### バックエンド
- FastAPI サーバー
- ComfyUI連携
- LLMプロバイダ統合（Ollama/OpenAI）
- Web検索機能（Tavily/SerpAPI）

### フロントエンド
- カメラ機能
- Web検索機能
- 画像履歴とセッション管理
- 差分編集UI
- ストーリーモード

### インフラ
- Docker構成
- CI/CD パイプライン
- 本番デプロイメント

## Git運用方針

### ブランチ戦略
- **main**: 安定版（表向けの公開ブランチ）
- **dev**: 開発版（AIが自動更新するバックヤード）
- **feature/***: 新機能開発
- **fix/***: バグ修正

### コミットルール
- プレフィックス：`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`
- 日本語または英語で明確に記述

## 開発環境

- Node.js: 22.x
- pnpm: 10.x
- React: 19.x
- Vite: 6.x
- Tailwind CSS: 最新版
- shadcn/ui: 最新版

## リポジトリ情報

- GitHub: https://github.com/nori368/oreza
- ブランチ: `main` (安定版), `dev` (開発版)
- ライセンス: MIT

## 次のマイルストーン

1. **FastAPIバックエンドの実装**
   - ヘルスチェックエンドポイント
   - チャット完了エンドポイント
   - 画像生成エンドポイント
   - Web検索エンドポイント

2. **ComfyUI連携**
   - ワークフローJSON管理
   - WebSocket進捗監視
   - Midnight Journeyプリセット

3. **実際の画像生成テスト**
   - SDXLモデルでの検証
   - Midnight Journeyスタイルの調整
   - プロンプトプリセットの最適化

## 開発者メモ

このプロジェクトは、人間（nori368）とAI（Manus）の協働により開発されています。「人が観測し、AIが動く」という新しい開発スタイルの実験でもあり、Orezaのコンセプトそのものを体現しています。
