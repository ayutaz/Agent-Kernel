import json
import textwrap
import asyncio
from typing import List, Dict, Any
import json_repair
from agentkernel_standalone.mas.agent.base.plugin_base import PlanPlugin
from agentkernel_standalone.mas.agent.components import *
from agentkernel_standalone.toolkit.logger import get_logger


logger = get_logger(__name__)

class EasyPlanPlugin(PlanPlugin):
    """
    A plan plugin that generates a plan for the next tick using personality,
    relationships, conversation history, and diversity instructions.
    """

    def __init__(self):
        super().__init__()
        self.plan = []
        logger.info("EasyPlanPlugin initialized")

    async def init(self):
        self.agent_id = self._component.agent.agent_id
        self.model = self._component.agent.model
        self.perceive_comp: PerceiveComponent = self._component.agent.get_component("perceive")
        self.perceive_plug = self.perceive_comp._plugin

    async def execute(self, current_tick: int) -> Dict[str, Any]:
        self.plan.clear()
        could_see_agents = self.perceive_plug.surrounding_agents
        current_position = self.perceive_plug.current_position
        chat_history = self.perceive_plug.last_tick_messages
        friends = getattr(self.perceive_plug, 'friends', [])

        # Get own status from perceive
        status = getattr(self.perceive_plug, 'own_status', {})

        # Get profile
        profile_plug = self._component.agent.get_component("profile")._plugin
        name = await profile_plug.get_profile("name") or self.agent_id
        personality = await profile_plug.get_profile("personality") or ""
        occupation = await profile_plug.get_profile("occupation") or ""
        goal = await profile_plug.get_profile("goal") or ""

        # Get accumulated state
        state_plug = self._component.agent.get_component("state")._plugin
        conversation_history = await state_plug.get_state("conversation_history") or []
        recent_partners = await state_plug.get_state("recent_partners") or []
        last_reflection = await state_plug.get_state("last_reflection") or ""

        # Build nearby agent names (limit to 10)
        nearby_names = [a["id"] for a in could_see_agents[:10]]

        # Status display with warnings
        energy = status.get("energy", 70)
        happiness = status.get("happiness", 50)
        stress = status.get("stress", 30)
        socialization = status.get("socialization", 50)
        money = status.get("money", 1000)

        energy_warn = " ⚠ LOW ENERGY!" if energy < 20 else ""
        stress_warn = " ⚠ HIGH STRESS!" if stress > 70 else ""

        reflection_line = f'\nYour reflection from last tick: "{last_reflection}"' if last_reflection else ""

        prompt = f'''You are {name}, a {occupation}. {personality}.
Your goal: {goal}

You are on a 300x300 2D map at position {json.dumps(current_position)}.
Nearby agents: {json.dumps(nearby_names)}
Your friends: {json.dumps(friends)}
People you recently talked to: {json.dumps(recent_partners)}
Recent conversation history: {json.dumps(conversation_history[-5:])}

Your current status:
- Energy: {energy}{energy_warn}
- Happiness: {happiness}
- Stress: {stress}{stress_warn}
- Socialization: {socialization}
- Money: {money}
{reflection_line}

Available actions (choose ONE):
1. {{"action":"move", "target":[x, y]}} — Move to position. Cost: -5 energy
2. {{"action":"chat", "target":"agent_id", "content":"message"}} — Talk to nearby agent. Cost: -2 energy, +5 socialization, +3 happiness
3. {{"action":"rest"}} — Rest to recover. Effect: +20 energy, -10 stress
4. {{"action":"give", "target":"agent_id", "amount":N}} — Give money (1-500) to agent. Cost: +2 happiness, +3 socialization
5. {{"action":"help", "target":"agent_id"}} — Help a stressed agent. Cost: -3 energy, +5 happiness. Target gets: -15 stress, +10 happiness

Rules:
- If energy < 15, you MUST choose "rest"
- If you see a friend nearby, prioritize talking to them
- Avoid repeating the same conversation partner as last tick
- If no one interesting is nearby, move to explore
- Keep chat content under 20 words
- As a {occupation}, lean into your role (merchants: give, healers: help, socialites: chat, explorers: move)

Respond with ONE JSON action:'''

        model_response = await self.model.chat(prompt)
        logger.info(f"Agent {self.agent_id} has planned its next step: {model_response}.")
        self.plan.append(json_repair.loads(model_response))
