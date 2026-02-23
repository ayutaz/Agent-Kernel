<div align="center">
 <img
  src="assets/agentkernel_cover.png"
  alt="Agent-Kernel ロゴ"
  width="800"
 />
</div>

<div align="center">
    <!-- Core Metrics -->
    <a href="https://github.com/ZJU-LLMs/Agent-Kernel/stargazers">
        <img alt="GitHub Stars" src="https://img.shields.io/github/stars/ZJU-LLMs/Agent-Kernel?label=Stars&logo=github&color=brightgreen">
    </a>
    <!-- <a href="https://github.com/ZJU-LLMs/Agent-Kernel/stargazers">
        <img alt="GitHub Stars" src="https://img.shields.io/github/stars/ZJU-LLMs/Agent-Kernel?style=social">
    </a> -->
    <a href="https://github.com/ZJU-LLMs/Agent-Kernel/releases">
        <img alt="Version" src="https://img.shields.io/github/v/release/ZJU-LLMs/Agent-Kernel?color=blue&label=Version">
    </a>
    <!-- <a href="https://github.com/ZJU-LLMs/Agent-Kernel/releases">
        <img alt="Version" src="https://img.shields.io/badge/Version-1.0.0-blue">
    </a> -->
    <!-- Project Resources -->
    <a href="https://www.agent-kernel.tech">
        <img alt="Homepage" src="https://img.shields.io/badge/Homepage-Website-1f4b99?logo=home&logoColor=white">
    </a>
    <a href="https://arxiv.org/abs/2512.01610">
        <img alt="Paper" src="https://img.shields.io/badge/Paper-arXiv-b31b1b.svg?logo=arxiv&logoColor=white">
    </a>
    <!-- Community -->
    <a href="https://www.agent-kernel.tech/societyhub">
        <img alt="SocietyHub" src="https://img.shields.io/badge/SocietyHub-Community-2ea44f?logo=discourse&logoColor=white">
    </a>
    <!-- <a href="[YOUR_DISCORD_INVITE_LINK]">
        <img alt="Join us on Discord" src="https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white">
    </a> -->
    <!-- Contribution -->
    <a href="https://github.com/ZJU-LLMs/Agent-Kernel/pulls">
        <img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-Welcome-8fce00.svg">
    </a>
    <!-- License -->
    <a href="https://github.com/ZJU-LLMs/Agent-Kernel/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-Apache_2.0-orange.svg">
    </a>
</div>

<br>

<div align="center">
  <i>Agent-Kernel に GitHub で 🌟 Star をつけて応援してください！</i>
</div>

---

# 集合知のスケーリング則を探求する

**Agent-Kernel** は、**大規模**社会シミュレーションを強力に実現する、ユーザーフレンドリーなマルチエージェントシステム開発フレームワークです。**集合知のスケーリング則の探求**に新たな可能性を提供します。

## ✨ 特長

Agent-Kernel は以下をサポートします:

- **LLMベースのエージェントを実行時に動的に追加・削除**;

- **エージェント数の無制限スケーリング**;

- **シミュレーション実行中のリアルタイム介入**;

- **エージェントの行動と大規模言語モデル出力の信頼性検証**;

- **異なるシミュレーションシナリオ間でのコード再利用**。

- **シミュレーションの録画とリプレイ** — 実行結果をJSON形式で保存し、Society PanelのリプレイビューやAgent Mapで可視化・再生。

- **集合知スケーリング実験** — エージェント数と集団パフォーマンスの関係を測定するWisdom of Crowds実験フレームワークを内蔵。知識断片の分散探索・共有タスクで、スケーリング則を検証可能。

## 🎬 活用事例

Agent-Kernel は複数の複雑な社会シミュレーションシナリオに適用されています:

### 1. Universe 25 実験

有名な「Universe 25」社会学実験をシミュレーションし、人口密度・社会構造・行動異常の関係を探求します。

<div align="center">
  <a href="https://www.bilibili.com/video/BV1dz2DBDERB/" target="_blank">
    <img src="assets/rat.jpg" alt="Universe 25 実験" width="700"/>
  </a>
</div>

<!--
<div align="center">
  <img src="assets/rat.jpg" alt="Universe 25 実験" width="700"/>
</div> -->

### 2. 浙江大学キャンパスライフ

高精度なキャンパス環境シミュレーションを構築し、歩行者の流動パターン、リソース配分、社会的インタラクションを研究します。

<div align="center">
  <a href="https://www.bilibili.com/video/BV1xamQBuEgS/" target="_blank">
    <img src="assets/zju.png" alt="浙江大学キャンパスライフ" width="700"/>
  </a>
</div>

<!-- <div align="center">
 <img src="assets/zju.png" alt="浙江大学キャンパスライフ" width="700"/>
</div> -->

### 3. 集合知スケーリング実験（Wisdom of Crowds）

個体では解けないが集団なら解ける分散情報集約タスクを導入し、エージェント数と集団パフォーマンスの関係（スケーリング則）を測定します。300x300マップ上に散らばった20個の知識断片を、エージェント同士の `share_knowledge` アクションで集約し、N=10〜120で収束速度・カバレッジ・知識格差（ジニ係数）の変化を検証します。

```bash
# 18条件（6エージェント数 × 3シード）の自動実行
uv run python -m examples.standalone_test.run_wisdom_experiment
```

## 📍 目次

- [✨ 特長](#-特長)
- [🎬 活用事例](#-活用事例)
  - [Universe 25 実験](#1-universe-25-実験)
  - [浙江大学キャンパスライフ](#2-浙江大学キャンパスライフ)
- [🎯 コア優位性：なぜ Agent-Kernel を選ぶのか？](#-コア優位性なぜ-agent-kernel-を選ぶのか)
  - [適応性](#1-適応性)
  - [設定可能性](#2-設定可能性)
  - [信頼性](#3-信頼性)
  - [再利用性](#4-再利用性)
- [🏛️ アーキテクチャと設計](#️-アーキテクチャと設計)
  - [フレームワーク概要](#1-フレームワーク概要)
  - [ソフトウェア設計](#2-ソフトウェア設計)
- [🚀 クイックスタート](#-クイックスタート)
  - [動作要件](#1-動作要件)
  - [インストール](#2-インストール)
  - [（オプション）Society-Panel の起動](#3-オプションsociety-panel-の起動)
- [集合知スケーリング実験](#3-集合知スケーリング実験wisdom-of-crowds)
- [📂 プロジェクト構成](#-プロジェクト構成)
- [🎓 引用](#-引用)
- [🤝 コントリビューター](#-コントリビューター)
- [📜 ライセンス](#-ライセンス)

## 🎯 コア優位性：なぜ Agent-Kernel を選ぶのか？

Agent-Kernel は社会シミュレーションのための4つのコア優位性を提供し、マルチエージェントシステム研究において際立った存在です:

### 1. 適応性

Agent-Kernel は実行時にエージェントの追加・削除、環境の変更、行動の修正をサポートします。これにより、人口流動、環境変化、行動パターンの進化を自然に反映するシミュレーションが可能になります。

### 2. 設定可能性

Controller モジュールにより、シミュレーション実行中にパラメータやイベントをリアルタイムに調整できます。これにより、複雑な社会学的仮説の検証が容易になります。

### 3. 信頼性

Agent-Kernel は厳格なシステムレベルの検証メカニズムを採用し、すべてのエージェント行動を検証します。これにより、シミュレーション行動が物理的・社会的ルールに従うことを保証し、科学的厳密性を維持します。

### 4. 再利用性

Agent-Kernel は標準化されたプラグインベースのモジュール設計を採用しています。コードはシナリオを跨いで再利用でき、研究の反復速度を大幅に向上させます。

## 🏛️ アーキテクチャと設計

### 1. フレームワーク概要

Agent-Kernel フレームワークはモジュラーマイクロカーネルアーキテクチャを採用しています。**Agent**、**Environment**、**Action**、**Controller**、**System** モジュールで構成されるコアシステムと、複数のプラグインで成り立っています。コアはプラグイン登録、行動検証、非同期通信などの中核的な責務を管理し、プラグインが社会シミュレーションに必要な専門機能を提供します。以下の図をご覧ください:

<p align="center">

<img src="assets/framework.png" alt="Agent-Kernel フレームワーク" width="700"/>

</p>

### 2. ソフトウェア設計

Agent-Kernel フレームワークのコア設計目標を実現するため、以下の図に示す一連のソフトウェア設計を行いました:

<p align="center">

<img src="assets/softwaredesign.png" alt="Agent-Kernel ソフトウェア設計" width="700"/>

</p>

## 🚀 クイックスタート

### 1. 動作要件

- `Python ≥ 3.11, < 3.13`
- [uv](https://docs.astral.sh/uv/)（開発時推奨）

### 2. インストール

#### 開発者向け（ソースから）

```bash
# uv をインストール（未インストールの場合）
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# クローンしてセットアップ
git clone https://github.com/ZJU-LLMs/Agent-Kernel.git
cd Agent-Kernel
uv sync --all-extras    # .venv を自動作成し、全依存関係をインストール
```

#### エンドユーザー向け（PyPI から）

用途に応じて **スタンドアロン版** または **分散版** を選択できます。

**Agent-Kernel スタンドアロン版**

```bash
uv add agentkernel-standalone
```

👉 詳しい使い方と例は [スタンドアロン版 README](examples/standalone_test/README.md) をご覧ください。

**Agent-Kernel 分散版**

```bash
uv add agentkernel-distributed
```

> 注: 分散版パッケージは **Ray** に依存しており、自動的にインストールされます。

👉 詳しい使い方と例は [分散版 README](examples/distributed_test/README.md) をご覧ください。

#### オプション機能のインストール

`agentkernel-standalone` と `agentkernel-distributed` の両方で、Web サービスやストレージソリューション向けのオプション依存関係をサポートしています。必要に応じてインストールできます。

- `web` → `aiohttp`, `fastapi`, `uvicorn` をインストール
- `storages` → `asyncpg`, `pymilvus`, `redis` をインストール
- `all` → `web` と `storages` の両方をインストール

これらのオプションをインストールするには、角括弧 `[]` を使用します。例:

```bash
# スタンドアロン版に Web 機能を追加
uv add "agentkernel-standalone[web]"

# 分散版にストレージ機能を追加
uv add "agentkernel-distributed[storages]"

# 分散版に全オプション機能を追加
uv add "agentkernel-distributed[all]"
```

### 3. （オプション）Society-Panel の起動

Society-Panel は、シミュレーションの設定・デプロイ・監視を視覚的に行える Web ベースのコントロールパネルです。

1.  **パネルを起動:**
    提供されているスタートアップスクリプトを使用して、アプリケーションスタック全体（バックエンド + UI）を起動します。**スクリプトが必要な依存関係を自動的にチェック・インストールするため、手動での環境構築は不要です。**

    - **Linux/macOS:**

      ```bash
      # 実行権限を付与（初回のみ）
      chmod +x scripts/start_society_panel.sh
      ./scripts/start_society_panel.sh
      ```

    - **Windows:**
      ```bash
      scripts\start_society_panel.bat
      ```

2.  **UI にアクセス:**
    スクリプトがサービスの起動を確認したら、ブラウザで以下にアクセスします:
    **`http://localhost:5174`**

パネルから、カスタムコードパッケージのアップロード、グラフィカルインターフェースでの設定ファイル編集、シミュレーションライフサイクルの制御が可能です。パネルと関連サービスをすべてシャットダウンするには、スクリプトを実行したターミナルで `Ctrl+C` を押してください。

## 📂 プロジェクト構成

```
MAS/
├── packages/
│   ├── agentkernel-distributed/   # 分散版（Ray を自動インストール）
│   └── agentkernel-standalone/    # ローカル単一マシン版
│
├── examples/
│   ├── distributed_test/          # 分散版（Ray）の実行例
│   └── standalone_test/           # ローカルスタンドアロン版の実行例
│       └── run_wisdom_experiment.py  # 集合知スケーリング実験ランナー
│
├── society-panel/
│   ├── backend/                   # FastAPI バックエンドサービス
│   │   └── recordings/            # シミュレーション録画データ
│   └── frontend/                  # Vue 3 + Vite フロントエンド
│
├── scripts/                       # 起動スクリプト
│
└── README.md
```

## 🎓 引用

Agent-Kernel を研究で使用された場合は、以下の論文の引用をご検討ください:

```
@misc{mao2025agentkernelmicrokernelmultiagentframework,
      title={Agent-Kernel: A MicroKernel Multi-Agent System Framework for Adaptive Social Simulation Powered by LLMs},
      author={Yuren Mao and Peigen Liu and Xinjian Wang and Rui Ding and Jing Miao and Hui Zou and Mingjie Qi and Wanxiang Luo and Longbin Lai and Kai Wang and Zhengping Qian and Peilun Yang and Yunjun Gao and Ying Zhang},
      year={2025},
      eprint={2512.01610},
      archivePrefix={arXiv},
      primaryClass={cs.MA},
      url={https://arxiv.org/abs/2512.01610},
}
```

## 🤝 コントリビューター

Agent-Kernel に貢献してくださったすべての開発者に感謝します:

<a href="https://github.com/ZJU-LLMs/Agent-Kernel/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ZJU-LLMs/Agent-Kernel&v=1" width=400 />
</a>

_Pull Request を通じてコントリビューターになることを歓迎します！_

## 📜 ライセンス

本プロジェクトは Apache 2.0 ライセンスの下で公開されています。
