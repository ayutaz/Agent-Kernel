import pytest
from unittest.mock import AsyncMock, MagicMock

from examples.standalone_test.plugins.agent.reflect.EasyReflectPlugin import (
    EasyReflectPlugin,
)


def _make_plugin(last_action=None, chat_response="A short diary entry."):
    """Create an EasyReflectPlugin with mocked dependencies."""
    plugin = EasyReflectPlugin()

    # Mock state plugin with in-memory store
    state_store = {}
    if last_action is not None:
        state_store["last_action"] = last_action

    state_plug = AsyncMock()
    state_plug.get_state = AsyncMock(side_effect=lambda key: state_store.get(key))
    state_plug.set_state = AsyncMock(
        side_effect=lambda key, value: state_store.__setitem__(key, value)
    )

    # Mock model
    model = AsyncMock()
    model.chat = AsyncMock(return_value=chat_response)

    # Wire up plugin internals without calling init()
    plugin.agent_id = "agent_test"
    plugin.model = model
    plugin.state_plug = state_plug

    return plugin, state_plug, model, state_store


@pytest.mark.asyncio
async def test_reflect_no_last_action():
    """When last_action is None, last_reflection should be set to empty string."""
    plugin, state_plug, model, state_store = _make_plugin(last_action=None)

    await plugin.execute(current_tick=1)

    state_plug.set_state.assert_any_await("last_reflection", "")
    model.chat.assert_not_awaited()


@pytest.mark.asyncio
async def test_reflect_chat_action():
    """Chat action should produce a summary mentioning the target and content."""
    action = {"action": "chat", "target": "agent_02", "content": "Hello there!"}
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response="Had a pleasant conversation today."
    )

    await plugin.execute(current_tick=1)

    # Verify the prompt sent to the model contains the chat summary
    call_args = model.chat.call_args[0][0]
    assert "I chatted with agent_02" in call_args
    assert "Hello there!" in call_args

    # Verify diary was saved
    assert state_store["last_reflection"] == "Had a pleasant conversation today."


@pytest.mark.asyncio
async def test_reflect_move_action():
    """Move action should produce a summary mentioning position."""
    action = {"action": "move", "target": "(10, 20)"}
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response="Explored a new area."
    )

    await plugin.execute(current_tick=1)

    call_args = model.chat.call_args[0][0]
    assert "I moved to position (10, 20)" in call_args
    assert state_store["last_reflection"] == "Explored a new area."


@pytest.mark.asyncio
async def test_reflect_rest_action():
    """Rest action should produce a rest summary."""
    action = {"action": "rest"}
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response="Took a well-deserved break."
    )

    await plugin.execute(current_tick=1)

    call_args = model.chat.call_args[0][0]
    assert "I rested to recover energy" in call_args
    assert state_store["last_reflection"] == "Took a well-deserved break."


@pytest.mark.asyncio
async def test_reflect_give_action():
    """Give action should produce a summary mentioning target and amount."""
    action = {"action": "give", "target": "agent_05", "amount": 50}
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response="Felt generous today."
    )

    await plugin.execute(current_tick=1)

    call_args = model.chat.call_args[0][0]
    assert "I gave 50 money to agent_05" in call_args
    assert state_store["last_reflection"] == "Felt generous today."


@pytest.mark.asyncio
async def test_reflect_help_action():
    """Help action should produce a summary mentioning the target."""
    action = {"action": "help", "target": "agent_03"}
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response="Helping others is rewarding."
    )

    await plugin.execute(current_tick=1)

    call_args = model.chat.call_args[0][0]
    assert "I helped agent_03 reduce their stress" in call_args
    assert state_store["last_reflection"] == "Helping others is rewarding."


@pytest.mark.asyncio
async def test_reflect_llm_failure():
    """When the LLM call fails, last_reflection should be set to empty string."""
    action = {"action": "chat", "target": "agent_02", "content": "Hi"}
    plugin, state_plug, model, state_store = _make_plugin(last_action=action)

    model.chat = AsyncMock(side_effect=RuntimeError("LLM unavailable"))

    await plugin.execute(current_tick=1)

    assert state_store["last_reflection"] == ""


@pytest.mark.asyncio
async def test_reflect_diary_truncation():
    """Diary entries longer than 200 characters should be truncated."""
    action = {"action": "rest"}
    long_diary = "A" * 300
    plugin, state_plug, model, state_store = _make_plugin(
        last_action=action, chat_response=long_diary
    )

    await plugin.execute(current_tick=1)

    assert len(state_store["last_reflection"]) == 200
    assert state_store["last_reflection"] == "A" * 200
