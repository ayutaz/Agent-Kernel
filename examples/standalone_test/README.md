# はじめに
この例では、Agent-Kernel を使ったシンプルなマルチエージェントシステムの構築方法を示します。実行フローの理解と将来の拡張を容易にするために設計されています。

以下のプラグインの実装例を提供しています:
- **エージェント**: Perceive, State, Plan, Invoke, Reflect, Profile
- **アクション**: Communication
- **環境**: Space, Relation, Status, Knowledge, Survey

また、集合知スケーリング実験（Wisdom of Crowds）用の拡張プラグインも含まれています:
- **Wisdomエージェント**: WisdomPerceive（知識発見）, WisdomPlan（知識共有プロンプト）, WisdomInvoke（share_knowledgeアクション）
- **Knowledge環境**: KnowledgePoolPlugin（知識断片管理・集団指標計算）
- **Surveyエージェント**: SurveyPerceive（地域観測）, SurveyPlan（災害対応プロンプト）, SurveyInvoke（share_observationアクション）
- **Survey環境**: RegionalSurveyPlugin（地域属性管理・集団推定精度計算）

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

## 災害対応サーベイ実験（Disaster Response Survey）

地震後の5つの避難候補地を多様な専門家チームで評価する集合知実験です。各専門家は5属性（構造安全性・水/衛生・医療アクセス・物資経路・収容力）のうち**2つのみ**観測可能で、個体では原理的に正確な評価ができません。

### シナリオ設計

- **5つの避難候補地**: Riverside Park, Central School, North Hospital, Market Square, Industrial Complex
- **5つの専門家（リング構造）**: structural_engineer, medical_officer, logistics_coordinator, safety_inspector, community_liaison
- **各候補地の5属性値**: シードから乱数生成（合計60-90の範囲）
- **観測ノイズ**: 真値 ± uniform(-5, +5)、[0, 20]にクリップ（hashlib.sha256で決定論的）

### 実験条件

| 群 | N | シード | 合計回数 |
|---|---|--------|---------|
| 実験群（混合専門家） | 10, 20, 40, 60, 80, 120 | 42, 123, 456 | 18回 |
| 対照群（全員structural_engineer） | 10, 40, 120 | 42, 123, 456 | 9回 |

### 測定指標

| 指標 | 説明 |
|---|---|
| `collective_rmse` | 全エージェント推定の平均 vs 真値の二乗平均平方根誤差 |
| `avg_individual_rmse` | エージェント個々のRMSEの平均 |
| `diversity_bonus` | avg_individual_rmse - collective_rmse（集団の利得） |
| `attribute_coverage` | 観測済み属性-候補地ペア / 全25ペア |
| `estimate_correlation` | エージェント推定値のペアワイズPearson相関の平均 |

### 実行

```bash
cd Agent-Kernel
uv run python -m examples.standalone_test.run_wisdom_experiment survey
```

結果は `society-panel/backend/recordings/` に `survey_N{n}_S{seed}_*.json`（個別）と `survey_scaling_results_*.json`（集約）として保存されます。
