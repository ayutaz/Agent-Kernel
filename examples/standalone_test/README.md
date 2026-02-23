# はじめに
この例では、Agent-Kernel を使ったシンプルなマルチエージェントシステムの構築方法を示します。実行フローの理解と将来の拡張を容易にするために設計されています。

以下のプラグインの実装例を提供しています:
- **エージェント**: Perceive, State, Plan, Invoke, Reflect, Profile
- **アクション**: Communication
- **環境**: Space, Relation, Status, Knowledge

また、集合知スケーリング実験（Wisdom of Crowds）用の拡張プラグインも含まれています:
- **Wisdomエージェント**: WisdomPerceive（知識発見）, WisdomPlan（知識共有プロンプト）, WisdomInvoke（share_knowledgeアクション）
- **Knowledge環境**: KnowledgePoolPlugin（知識断片管理・集団指標計算）

### エージェントプロファイル

各エージェントは `data/agents/profiles.jsonl` で定義されるプロファイルを持ちます。`personality`（性格）、`occupation`（職業）、`goal`（目標）フィールドがLLMプロンプトに注入され、個性的な行動を生成します。

### コンポーネント実行順序

`configs/agents_config.yaml` の `component_order` により、各tickで `perceive → state → plan → invoke → reflect` の順にコンポーネントが実行されます。`state` を `plan` の前に配置することで、計画立案時に最新の状態情報（会話履歴、最近の対話相手）を参照できます。

### シミュレーション録画

シミュレーション実行時、各tickのエージェント位置とメッセージが自動的に録画され、`society-panel/backend/recordings/` に `recording_*.json` として保存されます。また、エージェントの行動軌跡は `trajectory_*.json` として保存されます。

# クイックスタート
1. 以下のいずれかの方法で API キーを設定します:

    **方法 A: `.env` ファイル（推奨）**

    リポジトリルートに `.env` ファイルを作成します:
    ```
    OPENAI_API_KEY=sk-your-api-key
    ```

    **方法 B: 環境変数**
    ```bash
    export OPENAI_API_KEY=sk-your-api-key
    ```

    **方法 C: YAML に直接指定**

    **`examples/standalone_test/configs/models_config.yaml`** を編集し、`api_key` フィールドを追加します:
    ```yaml
    - name: OpenAIProvider
      model: gpt-4o-mini
      api_key: "sk-your-api-key"
      base_url: "https://api.openai.com/v1"
      capabilities: ["chat"]
    ```

    > デフォルト設定では `gpt-4o-mini` と OpenAI API を使用します。YAML で `api_key` を省略した場合、環境変数 `OPENAI_API_KEY` にフォールバックします。

2. 必要な依存関係をインストールします:
    ```bash
    # リポジトリルートから実行
    uv sync --all-extras
    ```

3. 実行
    ```bash
    cd Agent-Kernel
    # 基本シミュレーション
    uv run python -m examples.standalone_test.run_simulation
    ```

## 集合知スケーリング実験（Wisdom of Crowds）

個体では解けないが集団なら解けるタスクを導入し、エージェント数とパフォーマンスの関係（スケーリング則）を測定する実験です。

- 300x300マップ上に20個の「知識断片」をランダム配置
- 各エージェントは視認距離30以内の断片のみ発見可能
- `share_knowledge` アクションで他エージェントに知識を伝播
- 6条件（N=10, 20, 40, 60, 80, 120）× 3シード = 18回のシミュレーションを自動実行

### 測定指標

| 指標 | 説明 |
|---|---|
| `global_coverage` | 全断片のうち少なくとも1体が発見した割合 |
| `avg_individual_knowledge` | エージェント1体あたりの平均知識数 |
| `fully_informed_agents` | 全断片を知っているエージェント数 |
| `convergence_tick` | global_coverageが100%に到達したtick |
| `knowledge_gini` | 知識分布のジニ係数（格差） |
| `knowledge_velocity` | tick毎の知識拡散速度 |

### 実行

```bash
cd Agent-Kernel
uv run python -m examples.standalone_test.run_wisdom_experiment
```

結果は `society-panel/backend/recordings/` に `wisdom_N{n}_S{seed}_*.json`（個別）と `wisdom_scaling_results_*.json`（集約）として保存されます。
