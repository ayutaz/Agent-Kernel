# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Agent-Kernelは、大規模社会シミュレーション向けのマルチエージェントシステム（MAS）開発フレームワーク。モジュラーマイクロカーネルアーキテクチャを採用し、集合知のスケーリング則を探求する。Python 3.11以上、Apache 2.0ライセンス。

## リポジトリ構成

モノレポ構成で3つのパッケージから成る:

- **`packages/agentkernel-standalone/`** — 単一プロセスで動作するスタンドアロン版（PyPI: `agentkernel-standalone`）
- **`packages/agentkernel-distributed/`** — Ray 2.49.2ベースの分散版（PyPI: `agentkernel-distributed`）
- **`society-panel/`** — Web管理UI（FastAPIバックエンド + Vue 3フロントエンド、分散版専用）
- **`examples/`** — standalone_test / distributed_test の実行サンプル

standaloneとdistributedは同じコアアーキテクチャを共有し、distributedは追加で `mas/pod/` モジュールを持つ。

## コマンド

### 開発環境セットアップ
```bash
# uv をインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS/Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 依存関係を同期（.venv 自動作成）
uv sync --all-extras
```

### シミュレーション実行
```bash
# スタンドアロン版（リポジトリルートから）
uv run python -m examples.standalone_test.run_simulation

# 分散版
uv run python -m examples.distributed_test.run_simulation
```
実行前に `examples/*/configs/models_config.yaml` にAPIキーを設定すること。

### インストール（PyPIエンドユーザー向け）
```bash
pip install "agentkernel-standalone[all]"     # スタンドアロン版（全依存込み）
pip install "agentkernel-distributed[all]"    # 分散版（全依存込み）
```
オプション依存: `[web]`（FastAPI/aiohttp）、`[storages]`（asyncpg/Redis/Milvus）、`[all]`（全部）

### PCGツール（データ生成）
```bash
uv run pcg  # エージェントプロファイル、関係性、空間データの自動生成CLIツール
```

### Society Panel（分散版Web UI）
```bash
# Linux/macOS
./scripts/start_society_panel.sh
# Windows
scripts\start_society_panel.bat
```

### ビルド
```bash
uv build  # パッケージディレクトリ内で実行（hatchling に自動委譲）
```

### テスト
専用のテストフレームワーク（pytest等）は未導入。`examples/` のシミュレーション実行が統合テストとして機能する。

## アーキテクチャ

### マイクロカーネルパターン

5つのコアモジュールとプラグインシステムで構成:

```
Controller（調整層）
 ├── Agent（エージェント）    ← 6コンポーネント: Profile, Perceive, Plan, Invoke, State, Reflect
 ├── Environment（環境）      ← Space, Relation, Generic
 ├── Action（アクション）      ← Communication, Tools, OtherActions
 └── System（システム）        ← Timer, Messager, Recorder
```

### コンポーネント-プラグイン委譲パターン

全モジュールが同じパターンに従う: **Component** がインターフェース、**Plugin** が実装を担当。各Componentは1つのPluginを持つ。

```
base/component_base.py  →  ComponentBase[PluginType]（ジェネリック基底クラス）
base/plugin_base.py     →  PluginBase（プラグイン基底クラス）
components/*.py         →  各種Component定義
```

プラグイン間アクセスは `peer_plugin(name, PluginType)` で型安全に行う。

### ライフサイクル

1. **Builder.init()** — YAMLコンフィグ読み込み → 全コンポーネント構築（`asyncio.gather()`で並行初期化）
2. **シミュレーションループ** — `controller.step_agent()` → `system.run("messager", "dispatch_messages")` をtick毎に繰り返し
3. **シャットダウン** — `controller.close()` → `system.close()`

### リソースマップ

プラグイン解決の中心機構。`examples/*/registry.py` で定義:
```python
RESOURCES_MAPS = {
    "agent_components": {...},
    "agent_plugins": {...},
    "action_components": {...},
    "action_plugins": {...},
    "environment_components": {...},
    "environment_plugins": {...},
    "models": {...},
    "adapters": {...},
}
```

### YAML設定駆動

`simulation_config.yaml` がエントリーポイント。ここから agent_templates, environment, actions, system, models, database の各コンフィグを参照。データファイルはJSON/JSONL/YAML。全設定は `types/configs/` のPydanticモデルで検証される。

### ストレージ抽象化

`toolkit/storages/` で `DatabaseAdapter` インターフェースを定義:
- SQL: PostgreSQL（asyncpg）
- KV: Redis
- Graph: Redis
- VectorDB: Milvus

### モデル統合

`toolkit/models/router.py` の `ModelRouter` がLLMルーティングを提供。フックシステム（`post_chat`, `on_error`）でトークン使用量追跡やテレメトリに対応。OpenAI APIプロバイダが標準実装。

## 主要ファイル（コード理解の起点）

- `packages/agentkernel-standalone/agentkernel_standalone/mas/builder.py` — 初期化・組み立て
- `packages/agentkernel-standalone/agentkernel_standalone/mas/controller/controller.py` — シミュレーション制御
- `packages/agentkernel-standalone/agentkernel_standalone/mas/agent/agent.py` — エージェントコンテナ
- `packages/agentkernel-standalone/agentkernel_standalone/mas/agent/base/plugin_base.py` — プラグイン基底
- `examples/standalone_test/registry.py` — リソース登録例
- `examples/standalone_test/run_simulation.py` — 実行エントリーポイント例

## 技術スタック

| 分類 | 技術 |
|------|------|
| 言語 | Python 3.11+ |
| データ検証 | Pydantic 2.x |
| 設定 | PyYAML |
| LLM | OpenAI API |
| 非同期 | asyncio, uvicorn |
| 分散 | Ray 2.49.2（distributed版のみ） |
| Web | FastAPI + Vue 3 + Vite + Pinia |
| 通信 | WebSocket（FastMCP, aiohttp） |
| パッケージ管理 | uv（ワークスペース） |
| ビルド | Hatchling |

## 開発時の注意点

- 全I/O処理は `async/await` で記述する
- 新しいプラグインは対応する `PluginBase` を継承し、`examples/*/plugins/` のパターンに従う
- コンフィグ追加時は `types/configs/` にPydanticモデルを定義する
- standaloneとdistributedでコア構造は共通。distributed固有コードは `mas/pod/` に配置
- 環境変数 `MAS_PROJECT_ABS_PATH` と `MAS_PROJECT_REL_PATH` はシミュレーション実行時に必要
