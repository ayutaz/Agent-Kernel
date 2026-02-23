import json
import json_repair
from typing import Dict, Any
from agentkernel_standalone.mas.agent.base.plugin_base import PlanPlugin
from agentkernel_standalone.mas.agent.components import *
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class WisdomPlanPlugin(PlanPlugin):
    """Plan plugin for Wisdom of Crowds experiment with knowledge sharing."""

    def __init__(self):
        super().__init__()
        self.plan = []
        logger.info("WisdomPlanPlugin initialized")

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

        # Build nearby agent info with status (limit to 10)
        nearby_info = []
        for a in could_see_agents[:10]:
            st = a.get("status", {})
            info = {"id": a["id"], "energy": st.get("energy", "?"), "stress": st.get("stress", "?"), "happiness": st.get("happiness", "?")}
            nearby_info.append(info)

        nearby_ids = {a["id"] for a in could_see_agents}
        friend_details = []
        for fid in friends:
            if fid in nearby_ids:
                friend_details.append(f"{fid} (nearby!)")
            else:
                friend_details.append(f"{fid} (far away)")

        # Status display
        energy = status.get("energy", 70)
        happiness = status.get("happiness", 50)
        stress = status.get("stress", 30)
        socialization = status.get("socialization", 50)
        money = status.get("money", 1000)

        energy_warn = " ⚠ LOW ENERGY!" if energy < 20 else ""
        stress_warn = " ⚠ HIGH STRESS!" if stress > 70 else ""

        reflection_line = f'\nYour reflection from last tick: "{last_reflection}"' if last_reflection else ""

        # --- Knowledge info (NEW) ---
        my_knowledge = getattr(self.perceive_plug, 'my_knowledge', [])
        nearby_knowledge_counts = getattr(self.perceive_plug, 'nearby_knowledge_counts', [])
        total_fragments = 20  # default
        knowledge_count = len(my_knowledge)
        knowledge_list = json.dumps(sorted(my_knowledge))

        # Find nearby agents who might benefit from sharing
        nearby_with_less = []
        nearby_with_more = []
        for nk in nearby_knowledge_counts:
            if nk["knowledge"] < knowledge_count:
                nearby_with_less.append(nk)
            elif nk["knowledge"] > knowledge_count:
                nearby_with_more.append(nk)

        prompt = f'''You are {name}, a {occupation}. {personality}.
Your goal: {goal}

You are on a 300x300 2D map at position {json.dumps(current_position)}.
Nearby agents (with their status): {json.dumps(nearby_info)}
Your friends: {json.dumps(friend_details) if friend_details else "None"}
People you recently talked to: {json.dumps(recent_partners)}
Recent conversation history: {json.dumps(conversation_history[-5:])}

Your current status:
- Energy: {energy}{energy_warn}
- Happiness: {happiness}
- Stress: {stress}{stress_warn}
- Socialization: {socialization}
- Money: {money}
{reflection_line}

=== KNOWLEDGE MISSION ===
There are {total_fragments} knowledge fragments scattered across the map.
Your known fragments: {knowledge_list} ({knowledge_count}/{total_fragments})
Nearby agents with FEWER fragments than you: {json.dumps(nearby_with_less)}
Nearby agents with MORE fragments than you: {json.dumps(nearby_with_more)}

Available actions (choose ONE):
1. {{"action":"move", "target":[x, y]}} — Move to a new position. Cost: -5 energy
2. {{"action":"chat", "target":"agent_id", "content":"message"}} — Talk to a nearby agent. Cost: -5 energy, +1 stress, +5 socialization, +3 happiness
3. {{"action":"rest"}} — Rest to recover. Effect: +20 energy, -10 stress
4. {{"action":"give", "target":"agent_id", "amount":N}} — Give money (1-500) to nearby agent. Effect: +5 happiness, +5 socialization
5. {{"action":"help", "target":"agent_id"}} — Help a nearby agent. Cost: -3 energy. Effect: +8 happiness, +5 socialization. Target gets: -15 stress, +10 happiness
6. {{"action":"share_knowledge", "target":"agent_id"}} — Share ALL your knowledge fragments with a nearby agent. Cost: -3 energy, +5 happiness, +5 socialization

IMPORTANT rules:
- If energy < 15, you MUST choose "rest"
- If energy < 40, strongly consider resting before it gets critical
- PRIORITY: Collecting and sharing knowledge is your PRIMARY mission!
- If you have fragments that a nearby agent lacks, use share_knowledge with them
- If a nearby agent has more fragments than you, chat with them to coordinate
- Move to UNEXPLORED areas (away from your current position) to discover new fragments
- Fragments are found automatically when you are within 30 units of them
- Balance exploration (move to find fragments) and sharing (share_knowledge with nearby agents)
- Keep chat content under 20 words
- Vary your actions — don't repeat the same action every tick

Respond with ONE JSON action:'''

        model_response = await self.model.chat(prompt)
        logger.info(f"Agent {self.agent_id} has planned its next step: {model_response}.")
        self.plan.append(json_repair.loads(model_response))
