import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Helper: build a minimal mock agent wiring for plugin tests
# ---------------------------------------------------------------------------

def _make_mock_agent(agent_id="agent_01"):
    """Return (agent, controller, state_plug) mocks wired together."""
    controller = MagicMock()
    controller.run_environment = AsyncMock(return_value={})
    controller.run_action = AsyncMock()

    state_plug = MagicMock()
    state_plug.set_state = AsyncMock()
    state_plug.get_state = AsyncMock(return_value=None)

    state_comp = MagicMock()
    state_comp._plugin = state_plug

    plan_plug = MagicMock()
    plan_plug.plan = []

    plan_comp = MagicMock()
    plan_comp._plugin = plan_plug

    profile_plug = MagicMock()
    profile_plug.get_profile = AsyncMock(return_value="test")

    profile_comp = MagicMock()
    profile_comp._plugin = profile_plug

    perceive_plug = MagicMock()
    perceive_plug.surrounding_agents = []
    perceive_plug.current_position = [150, 150]
    perceive_plug.last_tick_messages = []
    perceive_plug.friends = []
    perceive_plug.own_status = {}

    perceive_comp = MagicMock()
    perceive_comp._plugin = perceive_plug

    def get_component(name):
        return {
            "plan": plan_comp,
            "state": state_comp,
            "profile": profile_comp,
            "perceive": perceive_comp,
        }[name]

    agent = MagicMock()
    agent.agent_id = agent_id
    agent.controller = controller
    agent.get_component = get_component
    agent.model = MagicMock()
    agent.model.chat = AsyncMock(return_value='{"action":"move","target":[100,100]}')

    component = MagicMock()
    component.agent = agent

    return agent, controller, state_plug, plan_plug, component


# ===========================================================================
# EasyPerceivePlugin tests
# ===========================================================================

class TestEasyPerceivePlugin:
    def test_own_status_initialized(self):
        """own_status attribute should exist and default to empty dict."""
        from examples.standalone_test.plugins.agent.perceive.EasyPerceivePlugin import EasyPerceivePlugin
        plugin = EasyPerceivePlugin()
        assert hasattr(plugin, "own_status")
        assert plugin.own_status == {}


# ===========================================================================
# EasyInvokePlugin tests
# ===========================================================================

class TestEasyInvokePlugin:

    def _make_invoke_plugin(self):
        from examples.standalone_test.plugins.agent.invoke.EasyInvokePlugin import EasyInvokePlugin
        agent, controller, state_plug, plan_plug, component = _make_mock_agent()
        plugin = EasyInvokePlugin()
        plugin._component = component
        # Manually wire fields that init() would set
        plugin.agent_id = agent.agent_id
        plugin.plan_comp = agent.get_component("plan")
        plugin.plan_plug = plan_plug
        plugin.controller = controller
        plugin.state_plug = state_plug
        return plugin, controller, state_plug, plan_plug

    @pytest.mark.asyncio
    async def test_rest_action(self):
        """rest action should call _update_status with energy +20, stress -10."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "rest"}]
        # Return high energy so forced-rest does not trigger
        controller.run_environment = AsyncMock(return_value={"energy": 70})

        await plugin.execute(current_tick=1)

        # _update_status calls run_environment("status", "update_status", ...)
        calls = controller.run_environment.call_args_list
        update_calls = [c for c in calls if c[0][0] == "status" and c[0][1] == "update_status"]
        assert len(update_calls) == 1
        assert update_calls[0][0][3] == {"energy": 20, "stress": -10}

    @pytest.mark.asyncio
    async def test_give_clamps_amount(self):
        """give action should clamp amount to [1, 500]."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "give", "target": "agent_02", "amount": 9999}]
        controller.run_environment = AsyncMock(return_value={"energy": 70})

        await plugin.execute(current_tick=1)

        # Find transfer_money call
        calls = controller.run_environment.call_args_list
        transfer_calls = [c for c in calls if len(c[0]) >= 2 and c[0][1] == "transfer_money"]
        assert len(transfer_calls) == 1
        # amount argument should be clamped to 500
        assert transfer_calls[0][0][4] == 500

    @pytest.mark.asyncio
    async def test_help_updates_both_statuses(self):
        """help action should update status for both self and target."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "help", "target": "agent_02"}]
        controller.run_environment = AsyncMock(return_value={"energy": 70})

        await plugin.execute(current_tick=1)

        calls = controller.run_environment.call_args_list
        update_calls = [c for c in calls if c[0][0] == "status" and c[0][1] == "update_status"]
        # Should have 2 update_status calls: one for self, one for target
        assert len(update_calls) == 2
        agent_ids_updated = [c[0][2] for c in update_calls]
        assert "agent_01" in agent_ids_updated
        assert "agent_02" in agent_ids_updated

    @pytest.mark.asyncio
    async def test_forced_rest_on_low_energy(self):
        """When energy < 15, execute() should force rest and return early."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "move", "target": [200, 200]}]
        # Return low energy from status check
        controller.run_environment = AsyncMock(return_value={"energy": 10})

        await plugin.execute(current_tick=1)

        # Should have recorded last_action as rest
        state_plug.set_state.assert_called_once_with("last_action", {"action": "rest"})
        # Should NOT have called update_agent_position (move was skipped)
        calls = controller.run_environment.call_args_list
        space_calls = [c for c in calls if c[0][0] == "space"]
        assert len(space_calls) == 0

    @pytest.mark.asyncio
    async def test_unknown_action_does_not_crash(self):
        """Unknown action types should be logged but not raise."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "dance"}]
        controller.run_environment = AsyncMock(return_value={"energy": 70})

        # Should not raise
        await plugin.execute(current_tick=1)

    @pytest.mark.asyncio
    async def test_last_action_recorded_in_state(self):
        """After executing a plan, last_action should be set in state."""
        plugin, controller, state_plug, plan_plug = self._make_invoke_plugin()
        plan_plug.plan = [{"action": "rest"}]
        controller.run_environment = AsyncMock(return_value={"energy": 70})

        await plugin.execute(current_tick=1)

        state_plug.set_state.assert_called_with("last_action", {"action": "rest"})
