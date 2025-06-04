# 🩺 ハイリスク語抽出アプリ（Japanese High-Risk Word Extractor）

このアプリは、医療文章などの日本語テキストから IBM Watson Knowledge Studio（WKS）で構築したカスタムモデルを用いて「ハイリスク語」や「注意語（hazard）」「状態語（state）」などを抽出し、色付きで可視化するStreamlitベースのWebアプリです。

## 🚀 機能概要

- IBM Watson NLU にデプロイした WKSモデルを使ってエンティティ抽出
- ラベル（`high_risk`, `risk`, `hazard`, `state`）ごとに異なる色で文章をハイライト表示
- Streamlit Cloud にそのままデプロイ可能

## 🔧 使用技術

- Streamlit
- IBM Watson Natural Language Understanding (NLU)
- Watson Knowledge Studio（で作成したモデルを利用）
- Python + Requests ライブラリ

## 💡 ラベルと色の対応

| ラベル       | 意味             | 表示色    |
|--------------|------------------|-----------|
| `high_risk`  | 高リスク語       | 紫        |
| `risk`       | リスク語         | 赤　　　  |
| `hazard`     | 注意語・危険要素 | 緑        |
| `state`      | 状態語           | グレー    |

## 📦 セットアップ手順

### 1. 環境準備

```bash
pip install streamlit requests
