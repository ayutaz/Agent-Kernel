from typing import Dict, Any, Optional
from agentkernel_standalone.mas.environment.base.plugin_base import GenericPlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class EasyStatusPlugin(GenericPlugin):
    """Dynamic status environment plugin managing energy/happiness/stress/socialization/money per agent."""

    COMPONENT_TYPE = "status"

    DEFAULT_STATUS = {
        "energy": 70,
        "happiness": 50,
        "stress": 30,
        "socialization": 50,
        "money": 1000,
    }

    def __init__(self, statuses: Optional[Dict[str, Any]] = None):
        super().__init__()
        self._statuses: Dict[str, Dict[str, int]] = {}
        if statuses:
            for agent_id, data in statuses.items():
                self._statuses[agent_id] = {
                    "energy": data.get("energy", self.DEFAULT_STATUS["energy"]),
                    "happiness": data.get("happiness", self.DEFAULT_STATUS["happiness"]),
                    "stress": data.get("stress", self.DEFAULT_STATUS["stress"]),
                    "socialization": data.get("socialization", self.DEFAULT_STATUS["socialization"]),
                    "money": data.get("money", self.DEFAULT_STATUS["money"]),
                }
        logger.info(f"EasyStatusPlugin initialized with {len(self._statuses)} agents.")

    async def get_status(self, agent_id: str) -> Dict[str, int]:
        """Return a copy of one agent's status. Creates default if missing."""
        if agent_id not in self._statuses:
            self._statuses[agent_id] = dict(self.DEFAULT_STATUS)
        return dict(self._statuses[agent_id])

    async def get_all_statuses(self) -> Dict[str, Dict[str, int]]:
        """Return a copy of all agent statuses (for recording)."""
        return {aid: dict(s) for aid, s in self._statuses.items()}

    async def update_status(self, agent_id: str, changes: Dict[str, int]) -> None:
        """Apply delta changes. Values clamped to [0,100] (money: [0, inf))."""
        if agent_id not in self._statuses:
            self._statuses[agent_id] = dict(self.DEFAULT_STATUS)
        for key, delta in changes.items():
            if key in self._statuses[agent_id]:
                old_val = self._statuses[agent_id][key]
                new_val = old_val + delta
                if key == "money":
                    new_val = max(0, new_val)
                else:
                    new_val = max(0, min(100, new_val))
                self._statuses[agent_id][key] = new_val

    async def transfer_money(self, from_id: str, to_id: str, amount: int) -> bool:
        """Transfer money between agents. Returns False if insufficient funds."""
        if from_id not in self._statuses:
            self._statuses[from_id] = dict(self.DEFAULT_STATUS)
        if to_id not in self._statuses:
            self._statuses[to_id] = dict(self.DEFAULT_STATUS)
        if self._statuses[from_id]["money"] < amount:
            return False
        self._statuses[from_id]["money"] -= amount
        self._statuses[to_id]["money"] += amount
        return True

    async def apply_tick_decay(self) -> None:
        """Per-tick natural changes: energy +1, stress -1, happiness -2, socialization -3, money -15."""
        for agent_id in self._statuses:
            s = self._statuses[agent_id]
            # Energy: slow natural recovery
            s["energy"] = min(100, s["energy"] + 1)
            # Stress: slow natural decay
            s["stress"] = max(0, s["stress"] - 1)
            # Happiness: natural decay (prevents saturation)
            s["happiness"] = max(0, s["happiness"] - 2)
            # Socialization: natural decay (requires ongoing interaction)
            s["socialization"] = max(0, s["socialization"] - 3)
            # Money: living cost
            s["money"] = max(0, s["money"] - 15)
