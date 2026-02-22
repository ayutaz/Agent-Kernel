# はじめに
この例では、Agent-Kernel を使ったシンプルなマルチエージェントシステムの構築方法を示します。実行フローの理解と将来の拡張を容易にするために設計されています。

以下のプラグインの実装例を提供しています:
- **エージェント**: Perceive, State, Plan, Invoke, Reflect, Profile
- **アクション**: Communication
- **環境**: Space, Relation

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
    uv run python -m examples.standalone_test.run_simulation
    ```
