<p align="center">
  <img
    src="https://raw.githubusercontent.com/ZJU-LLMs/Agent-Kernel/main/assets/agentkernel_logo.png"
    width="400"
  />
</p>

# Agent-Kernel 分散版

**Agent-Kernel 分散版** は、**Ray** を活用した分散実行により大規模環境をサポートする、マルチエージェントシステム（MAS）開発フレームワークです。異なるノードやプロセスにまたがる複数のインテリジェントエージェントの連携に最適です。

---

## 🚀 クイックスタート

### 1. 動作要件

- `Python ≥ 3.11, < 3.13`

### 2. 開発者向け（ソースから）

```bash
# リポジトリルートから実行
uv sync --all-extras
```

### 3. PyPI からインストール

`uv` を使って Agent-Kernel 分散版を直接インストールできます。

```bash
uv add agentkernel-distributed
```

> 分散版パッケージは Ray に依存しており、自動的にインストールされます。

**オプション機能のインストール**

Agent-Kernel 分散版は、Web サービスやストレージソリューション向けのオプション依存関係をサポートしています。必要に応じてインストールできます。

- `web` → `aiohttp`, `fastapi`, `uvicorn` をインストール
- `storages` → `asyncpg`, `pymilvus`, `redis` をインストール
- `all` → `web` と `storages` の両方をインストール

以下の形式でオプションを指定してインストールします:

```bash
# Web 機能付きでインストール
uv add "agentkernel-distributed[web]"

# ストレージ機能付きでインストール
uv add "agentkernel-distributed[storages]"

# 全オプション機能付きでインストール
uv add "agentkernel-distributed[all]"
```
