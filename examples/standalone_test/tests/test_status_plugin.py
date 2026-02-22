import pytest
import pytest_asyncio
from examples.standalone_test.plugins.environment.status.EasyStatusPlugin import EasyStatusPlugin


@pytest.fixture
def plugin_empty():
    """Plugin with no initial statuses."""
    return EasyStatusPlugin()


@pytest.fixture
def plugin_with_data():
    """Plugin pre-loaded with two agents."""
    return EasyStatusPlugin(statuses={
        "agent_1": {"energy": 80, "happiness": 60, "stress": 40, "socialization": 55, "money": 500},
        "agent_2": {"energy": 50, "happiness": 30, "stress": 70, "socialization": 20, "money": 2000},
    })


@pytest.mark.asyncio
async def test_get_status_default(plugin_empty):
    """Unknown agent should receive DEFAULT_STATUS."""
    status = await plugin_empty.get_status("unknown_agent")
    assert status == EasyStatusPlugin.DEFAULT_STATUS


@pytest.mark.asyncio
async def test_get_status_initialized(plugin_with_data):
    """Agent initialised via constructor should return its values."""
    status = await plugin_with_data.get_status("agent_1")
    assert status["energy"] == 80
    assert status["happiness"] == 60
    assert status["stress"] == 40
    assert status["socialization"] == 55
    assert status["money"] == 500


@pytest.mark.asyncio
async def test_update_status_clamp_upper(plugin_with_data):
    """Non-money values must be clamped at 100."""
    await plugin_with_data.update_status("agent_1", {"energy": 100})
    status = await plugin_with_data.get_status("agent_1")
    assert status["energy"] == 100  # 80 + 100 -> clamped to 100


@pytest.mark.asyncio
async def test_update_status_clamp_lower(plugin_with_data):
    """Non-money values must be clamped at 0."""
    await plugin_with_data.update_status("agent_2", {"happiness": -100})
    status = await plugin_with_data.get_status("agent_2")
    assert status["happiness"] == 0  # 30 + (-100) -> clamped to 0


@pytest.mark.asyncio
async def test_update_status_money_no_upper_clamp(plugin_with_data):
    """Money has no upper limit."""
    await plugin_with_data.update_status("agent_2", {"money": 100000})
    status = await plugin_with_data.get_status("agent_2")
    assert status["money"] == 102000  # 2000 + 100000


@pytest.mark.asyncio
async def test_transfer_money_success(plugin_with_data):
    """Successful transfer deducts from sender and credits receiver."""
    result = await plugin_with_data.transfer_money("agent_2", "agent_1", 300)
    assert result is True
    s1 = await plugin_with_data.get_status("agent_1")
    s2 = await plugin_with_data.get_status("agent_2")
    assert s1["money"] == 800   # 500 + 300
    assert s2["money"] == 1700  # 2000 - 300


@pytest.mark.asyncio
async def test_transfer_money_insufficient(plugin_with_data):
    """Transfer with insufficient funds returns False and leaves balances unchanged."""
    result = await plugin_with_data.transfer_money("agent_1", "agent_2", 9999)
    assert result is False
    s1 = await plugin_with_data.get_status("agent_1")
    s2 = await plugin_with_data.get_status("agent_2")
    assert s1["money"] == 500
    assert s2["money"] == 2000


@pytest.mark.asyncio
async def test_apply_tick_decay(plugin_with_data):
    """apply_tick_decay should add 3 to energy and subtract 2 from stress for all agents."""
    await plugin_with_data.apply_tick_decay()
    s1 = await plugin_with_data.get_status("agent_1")
    s2 = await plugin_with_data.get_status("agent_2")
    assert s1["energy"] == 83   # 80 + 3
    assert s1["stress"] == 38   # 40 - 2
    assert s2["energy"] == 53   # 50 + 3
    assert s2["stress"] == 68   # 70 - 2
