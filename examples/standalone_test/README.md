# はじめに
この例では、Agent-Kernel を使ったシンプルなマルチエージェントシステムの構築方法を示します。実行フローの理解と将来の拡張を容易にするために設計されています。

プロセスを簡素化するため、5つのコアプラグイン（Perceive、Plan、Invoke、Communication、Space）の基本実装を提供しています。残りのプラグインはプレースホルダー（pass を使用）として構成されており、ユーザーが自由にカスタマイズ・拡張できます。

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
