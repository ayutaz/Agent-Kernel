from agentkernel_standalone.mas.agent.base.plugin_base import InvokePlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class EasyInvokePlugin(InvokePlugin):
    """Execute planned actions with status effects."""

    def __init__(self):
        super().__init__()
        self.agent_id = None
        self.plan_comp = None
        self.plans = []
        self.controller = None
        self.sent_messages = []

    async def init(self):
        self.agent_id = self._component.agent.agent_id
        self.plan_comp = self._component.agent.get_component('plan')
        self.plan_plug = self.plan_comp._plugin
        self.controller = self._component.agent.controller
        self.state_plug = self._component.agent.get_component('state')._plugin

    async def execute(self, current_tick: int):
        self.sent_messages = []
        # Energy check — force rest if too low
        try:
            status = await self.controller.run_environment("status", "get_status", self.agent_id)
            if status.get("energy", 70) < 15:
                logger.info(f"Agent {self.agent_id}: energy too low ({status['energy']}), forced rest")
                await self._do_rest()
                await self.state_plug.set_state("last_action", {"action": "rest"})
                return
        except Exception:
            pass

        self.plans = self.plan_plug.plan
        for plan in self.plans:
            try:
                action = plan.get('action', '')
                if action == 'move':
                    target = plan.get('target', [150, 150])
                    x = max(0, min(300, int(target[0])))
                    y = max(0, min(300, int(target[1])))
                    await self._do_move((x, y))
                elif action == 'chat':
                    target_id = plan.get('target', '')
                    content = plan.get('content', '')
                    if target_id and content:
                        await self._do_chat(target_id, content)
                elif action == 'rest':
                    await self._do_rest()
                elif action == 'give':
                    target_id = plan.get('target', '')
                    amount = plan.get('amount', 100)
                    if target_id:
                        await self._do_give(target_id, amount)
                elif action == 'help':
                    target_id = plan.get('target', '')
                    if target_id:
                        await self._do_help(target_id)
                else:
                    logger.warning(f"Agent {self.agent_id}: unknown action '{action}'")

                # Record last action in state
                await self.state_plug.set_state("last_action", plan)
            except Exception as e:
                logger.error(f"Agent {self.agent_id}: error executing plan: {e}")

    async def _update_status(self, agent_id: str, changes: dict):
        """Helper to update status with error handling."""
        try:
            await self.controller.run_environment("status", "update_status", agent_id, changes)
        except Exception as e:
            logger.warning(f"Agent {self.agent_id}: failed to update status for {agent_id}: {e}")

    async def _do_move(self, target: tuple):
        await self.controller.run_environment('space', 'update_agent_position',
                                              agent_id=self.agent_id, new_position=target)
        await self._update_status(self.agent_id, {"energy": -5})
        logger.info(f'Agent {self.agent_id} moved to {target}')

    async def _do_chat(self, target_id: str, content: str):
        await self.controller.run_action('communication', 'send_message',
                                         from_id=self.agent_id, to_id=target_id, content=content)
        await self._update_status(self.agent_id, {"energy": -5, "socialization": 5, "happiness": 3, "stress": 1})
        await self._update_status(target_id, {"socialization": 3, "happiness": 2})
        self.sent_messages.append({"from_id": self.agent_id, "to_id": target_id, "content": content})
        logger.info(f'Agent {self.agent_id} chatted with {target_id}: {content}')

    async def _do_rest(self):
        await self._update_status(self.agent_id, {"energy": 20, "stress": -10})
        logger.info(f'Agent {self.agent_id} rested')

    async def _do_give(self, target_id: str, amount):
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 100
        amount = max(1, min(500, amount))
        try:
            success = await self.controller.run_environment("status", "transfer_money",
                                                            self.agent_id, target_id, amount)
            if success:
                await self._update_status(self.agent_id, {"happiness": 5, "socialization": 5})
                await self._update_status(target_id, {"happiness": 3})
                logger.info(f'Agent {self.agent_id} gave {amount} money to {target_id}')
            else:
                logger.info(f'Agent {self.agent_id} tried to give money to {target_id} but insufficient funds')
        except Exception as e:
            logger.warning(f"Agent {self.agent_id}: give action failed: {e}")

    async def _do_help(self, target_id: str):
        await self._update_status(self.agent_id, {"energy": -3, "happiness": 8, "socialization": 5})
        await self._update_status(target_id, {"stress": -15, "happiness": 10})
        logger.info(f'Agent {self.agent_id} helped {target_id}')
