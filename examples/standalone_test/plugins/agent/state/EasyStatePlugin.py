import json
from typing import Dict, Any, Optional
from agentkernel_standalone.toolkit.logger import get_logger
from agentkernel_standalone.mas.agent.base.plugin_base import StatePlugin

logger = get_logger(__name__)

class EasyStatePlugin(StatePlugin):
    def __init__(self, state_data: Optional[Dict[str, Any]] = None):
        super().__init__()
        # state_data is the specific state maintained by this plugin
        self._state_data: Dict[str, Any] = state_data if state_data is not None else {}
        self.agent_id = None

    async def init(self):
        self.agent_id = self._component.agent.agent_id

    async def execute(self, current_tick: int):
        perceive_comp = self._component.agent.get_component("perceive")
        perceive_plug = perceive_comp._plugin

        # Accumulate conversation history (sliding window of 20)
        history = self._state_data.get("conversation_history", [])
        for msg in perceive_plug.last_tick_messages:
            history.append({
                "tick": current_tick,
                "from": msg.get("from_id", ""),
                "content": msg.get("content", ""),
            })
        if len(history) > 20:
            history = history[-20:]
        self._state_data["conversation_history"] = history

        # Track recent conversation partners
        recent_partners = self._state_data.get("recent_partners", [])
        for msg in perceive_plug.last_tick_messages:
            partner = msg.get("from_id", "")
            if partner and partner not in recent_partners:
                recent_partners.append(partner)
        if len(recent_partners) > 10:
            recent_partners = recent_partners[-10:]
        self._state_data["recent_partners"] = recent_partners

        logger.info(f"Agent {self.agent_id} state updated: {len(history)} history entries, {len(recent_partners)} recent partners.")

    async def set_state(self, key: str, value: Any):
        self._state_data[key] = value

    async def get_state(self, key: str) -> Any:
        return self._state_data.get(key)
