from agentkernel_standalone.mas.agent.base.plugin_base import InvokePlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)

class EasyInvokePlugin(InvokePlugin):
    """
    Do what EasyPlanPlugin ask to do.
    """
    def __init__(self):
        super().__init__()
        self.agent_id = None
        self.plan_comp = None
        self.plans = []
        self.controller = None
    async def init(self):
        self.agent_id = self._component.agent.agent_id
        self.plan_comp = self._component.agent.get_component('plan')
        self.plan_plug = self.plan_comp._plugin
        self.controller = self._component.agent.controller
    async def execute(self, current_tick: int):

        self.plans = self.plan_plug.plan
        for plan in self.plans:
            try:
                action = plan.get('action', '')
                if action == 'move':
                    target = plan.get('target', [150, 150])
                    x = max(0, min(300, int(target[0])))
                    y = max(0, min(300, int(target[1])))
                    await self.move_to_pos((x, y))
                elif action == 'chat':
                    target_id = plan.get('target', '')
                    content = plan.get('content', '')
                    if target_id and content:
                        await self.chat_with_agent(target_id, content)
                else:
                    logger.warning(f"Agent {self.agent_id}: unknown action '{action}'")
            except Exception as e:
                logger.error(f"Agent {self.agent_id}: error executing plan: {e}")

    async def move_to_pos(self, target: tuple[int, int]):
        await self.controller.run_environment('space', 'update_agent_position',
                                        agent_id = self.agent_id,
                                        new_position = target
                                        )
        logger.info(f'Agent {self._component.agent.agent_id} move to {target}')

    async def chat_with_agent(self, target_id: str, content: str):
        await self.controller.run_action('communication', 'send_message', from_id =self.agent_id, to_id = target_id, content = content)
        logger.info(f'Agent {self._component.agent.agent_id} say to {target_id} : {content}')
