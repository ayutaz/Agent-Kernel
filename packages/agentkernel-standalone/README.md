<p align="center">
  <img
    src="https://raw.githubusercontent.com/ZJU-LLMs/Agent-Kernel/main/assets/agentkernel_logo.png"
    width="400"
  />
</p>

# Agent-Kernel スタンドアロン版

**Agent-Kernel スタンドアロン版** は、ローカル環境向けの軽量で自己完結型のマルチエージェントシステム（MAS）開発フレームワークです。分散版と同じモジュラーマイクロカーネルアーキテクチャを提供しつつ、単一マシン上で完結して動作します。Ray や外部サービスは不要です。

---

## 🚀 インストール

### 1. 動作要件

- Python ≥ 3.11, < 3.13

### 2. 開発者向け（ソースから）

```bash
# リポジトリルートから実行
uv sync --all-extras
```

### 3. PyPI からインストール

`uv` を使って Agent-Kernel スタンドアロン版を直接インストールできます。

```bash
uv add agentkernel-standalone
```

**オプション機能のインストール**

Agent-Kernel スタンドアロン版は、Web サービスやストレージソリューション向けのオプション依存関係をサポートしています。必要に応じてインストールできます。

- `web` → `aiohttp`, `fastapi`, `uvicorn` をインストール
- `storages` → `asyncpg`, `pymilvus`, `redis` をインストール
- `all` → `web` と `storages` の両方をインストール

以下の形式でオプションを指定してインストールします:

```bash
# Web 機能付きでインストール
uv add "agentkernel-standalone[web]"

# ストレージ機能付きでインストール
uv add "agentkernel-standalone[storages]"

# 全オプション機能付きでインストール
uv add "agentkernel-standalone[all]"
```
