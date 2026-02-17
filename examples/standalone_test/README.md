# Introduction
This example demonstrates how to build a simple Multi-Agent System using Agent-Kernel, designed to help users understand the execution flow and facilitate future extensions.

To simplify the process, we have provided basic implementations for five core plugins: Perceive, Plan, Invoke, Communication, and Space. The remaining plugins are structured as placeholders (using pass) to allow for easy customization and expansion by the user.

# Quick Start
1. Set your API key using one of the following methods:

    **Option A: `.env` file (Recommended)**

    Create a `.env` file in the repository root:
    ```
    OPENAI_API_KEY=sk-your-api-key
    ```

    **Option B: Environment variable**
    ```bash
    export OPENAI_API_KEY=sk-your-api-key
    ```

    **Option C: Direct YAML configuration**

    Edit **`examples/standalone_test/configs/models_config.yaml`** and add the `api_key` field:
    ```yaml
    - name: OpenAIProvider
      model: gpt-4o-mini
      api_key: "sk-your-api-key"
      base_url: "https://api.openai.com/v1"
      capabilities: ["chat"]
    ```

    > The default configuration uses `gpt-4o-mini` and the OpenAI API. If `api_key` is omitted from the YAML, it falls back to the `OPENAI_API_KEY` environment variable.

2. Install the required dependencies:
    ```bash
    # From the repository root
    uv sync --all-extras
    ```

3. Run
    ```bash
    cd Agent-Kernel
    uv run python -m examples.standalone_test.run_simulation
    ```
