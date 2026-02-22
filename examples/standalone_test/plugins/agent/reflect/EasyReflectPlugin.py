from typing import Dict, Any

from agentkernel_standalone.mas.agent.base.plugin_base import ReflectPlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class EasyReflectPlugin(ReflectPlugin):
    """Generate a 1-sentence diary entry via LLM after each tick."""

    def __init__(self):
        super().__init__()
        self.agent_id = None

    async def init(self):
        self.agent_id = self._component.agent.agent_id
        self.model = self._component.agent.model
        self.state_plug = self._component.agent.get_component("state")._plugin

    async def execute(self, current_tick: int) -> Dict[str, Any]:
        try:
            last_action = await self.state_plug.get_state("last_action")
            if not last_action:
                await self.state_plug.set_state("last_reflection", "")
                return

            action_type = last_action.get("action", "unknown")
            target = last_action.get("target", "")
            content = last_action.get("content", "")

            if action_type == "chat" and target:
                action_summary = f"I chatted with {target}: {content}"
            elif action_type == "move":
                action_summary = f"I moved to position {target}"
            elif action_type == "rest":
                action_summary = "I rested to recover energy"
            elif action_type == "give" and target:
                amount = last_action.get("amount", 0)
                action_summary = f"I gave {amount} money to {target}"
            elif action_type == "help" and target:
                action_summary = f"I helped {target} reduce their stress"
            else:
                action_summary = f"I did '{action_type}'"

            prompt = f"""You are an agent reflecting on your action. Write a 1-sentence diary entry (max 20 words).
Action: {action_summary}
Diary entry:"""

            response = await self.model.chat(prompt)
            diary = response.strip().strip('"').strip("'")
            if len(diary) > 200:
                diary = diary[:200]

            await self.state_plug.set_state("last_reflection", diary)
            logger.info(f"Agent {self.agent_id} reflects: {diary}")
        except Exception as e:
            logger.warning(f"Agent {self.agent_id} reflection failed: {e}")
            try:
                await self.state_plug.set_state("last_reflection", "")
            except Exception:
                pass
