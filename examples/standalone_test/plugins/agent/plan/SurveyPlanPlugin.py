import json
import json_repair
from typing import Dict, Any
from agentkernel_standalone.mas.agent.base.plugin_base import PlanPlugin
from agentkernel_standalone.mas.agent.components import *
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)

OCCUPATION_ATTRIBUTES = {
    "structural_engineer": ["structural", "water"],
    "medical_officer": ["water", "medical"],
    "logistics_coordinator": ["medical", "supply"],
    "safety_inspector": ["supply", "shelter"],
    "community_liaison": ["shelter", "structural"],
}

REGION_COORDS = {
    "riverside_park": {"name": "Riverside Park", "center": [50, 50]},
    "central_school": {"name": "Central School", "center": [250, 50]},
    "north_hospital": {"name": "North Hospital", "center": [150, 150]},
    "market_square": {"name": "Market Square", "center": [50, 250]},
    "industrial_complex": {"name": "Industrial Complex", "center": [250, 250]},
}


class SurveyPlanPlugin(PlanPlugin):
    """Plan plugin for disaster response survey experiment."""

    def __init__(self):
        super().__init__()
        self.plan = []
        logger.info("SurveyPlanPlugin initialized")

    async def init(self):
        self.agent_id = self._component.agent.agent_id
        self.model = self._component.agent.model
        self.perceive_comp: PerceiveComponent = self._component.agent.get_component("perceive")
        self.perceive_plug = self.perceive_comp._plugin

    async def execute(self, current_tick: int) -> Dict[str, Any]:
        self.plan.clear()
        could_see_agents = self.perceive_plug.surrounding_agents
        current_position = self.perceive_plug.current_position

        status = getattr(self.perceive_plug, 'own_status', {})

        # Get profile
        profile_plug = self._component.agent.get_component("profile")._plugin
        name = await profile_plug.get_profile("name") or self.agent_id
        occupation = await profile_plug.get_profile("occupation") or ""

        # Get accumulated state
        state_plug = self._component.agent.get_component("state")._plugin
        conversation_history = await state_plug.get_state("conversation_history") or []
        last_reflection = await state_plug.get_state("last_reflection") or ""

        # Survey-specific data from perceive
        observation_summary = getattr(self.perceive_plug, 'observation_summary', {})
        estimates = getattr(self.perceive_plug, 'estimates', {})
        unvisited_regions = getattr(self.perceive_plug, 'unvisited_regions', [])

        # Occupation attributes
        my_attrs = OCCUPATION_ATTRIBUTES.get(occupation, ["unknown", "unknown"])

        # Status display
        energy = status.get("energy", 70)
        stress = status.get("stress", 30)

        # Build candidate sites list
        sites_lines = []
        for rid, rinfo in REGION_COORDS.items():
            sites_lines.append(f"- {rinfo['name']} at {rinfo['center']}")
        sites_text = "\n".join(sites_lines)

        # Build observations text (only show regions with actual observations)
        obs_lines = []
        if observation_summary:
            for rid, rdata in observation_summary.items():
                n_attrs = rdata.get("n_attrs", 0)
                if n_attrs == 0:
                    continue
                rname = rdata.get("name", rid)
                attrs = rdata.get("observed_attrs", {})
                est = rdata.get("estimated_total")
                attr_parts = [f"{k}={v}" for k, v in attrs.items()]
                est_str = f"{est:.0f}" if est is not None else "?"
                obs_lines.append(f"{rname}: {', '.join(attr_parts)} (estimated total: {est_str}, {n_attrs}/5 attrs)")
        obs_text = "\n".join(obs_lines) if obs_lines else "No observations yet"

        # Build estimates text
        est_lines = []
        for rid, rinfo in REGION_COORDS.items():
            est_val = estimates.get(rid)
            if est_val is not None:
                est_lines.append(f"- {rinfo['name']}: {est_val:.0f}")
        estimates_text = "\n".join(est_lines) if est_lines else "No estimates yet"

        # Build recent context
        recent_convos = conversation_history[-3:] if conversation_history else []
        context_text = ""
        if recent_convos:
            context_text = f"\n=== RECENT CONVERSATIONS ===\n{json.dumps(recent_convos)}\n"
        if last_reflection:
            context_text += f"\nYour reflection: \"{last_reflection}\"\n"

        # Build unvisited sites text
        if unvisited_regions:
            unvisited_lines = []
            for rid in unvisited_regions:
                rinfo = REGION_COORDS.get(rid, {"name": rid, "center": [150, 150]})
                unvisited_lines.append(f"- {rinfo['name']} at {rinfo['center']}")
            unvisited_text = "\n".join(unvisited_lines)
        else:
            unvisited_text = "All sites visited!"

        # Build nearby specialists text
        if could_see_agents:
            nearby_lines = []
            for a in could_see_agents[:10]:
                aid = a["id"]
                pos = a.get("position", [0, 0])
                # Try to get occupation from status or default
                a_occ = a.get("occupation", "unknown")
                if a_occ == "unknown":
                    a_st = a.get("status", {})
                    a_occ = a_st.get("occupation", "unknown")
                nearby_lines.append(f"- {aid} ({a_occ}) at {pos}")
            nearby_text = "\n".join(nearby_lines)
        else:
            nearby_text = "No one nearby"

        prompt = f'''You are {name}, a {occupation} deployed for post-earthquake evacuation site assessment.

=== MISSION ===
Evaluate 5 candidate evacuation sites to determine the safest location for survivors.
Your expertise allows you to assess: {my_attrs[0]} and {my_attrs[1]} only.
You CANNOT assess the other 3 attributes — you need other specialists for that.

=== CANDIDATE SITES ===
{sites_text}

=== YOUR OBSERVATIONS ===
{obs_text}

=== YOUR ESTIMATES (total score per site, true range 60-90) ===
{estimates_text}
{context_text}
=== UNVISITED SITES ===
{unvisited_text}

=== NEARBY SPECIALISTS ===
{nearby_text}

=== STATUS ===
Energy: {energy}, Stress: {stress}, Position: {json.dumps(current_position)}

Available actions (choose ONE):
1. {{"action":"move","target":[x,y]}} — Move to a site (auto-observe on arrival). Cost: -5 energy
2. {{"action":"share_observation","target":"agent_id"}} — Share your data with a nearby specialist. Cost: -3 energy
3. {{"action":"chat","target":"agent_id","content":"msg"}} — Coordinate with nearby specialist. Cost: -5 energy
4. {{"action":"rest"}} — Rest. Effect: +20 energy, -10 stress

STRATEGY GUIDELINES:
- Visit unobserved sites first (your data is most valuable where no one has measured yet)
- Share observations with specialists who have DIFFERENT expertise
- If energy < 15, you MUST rest
- Keep chat under 20 words

Respond with a single JSON action:'''

        model_response = await self.model.chat(prompt)
        logger.info(f"Agent {self.agent_id} has planned its next step: {model_response}.")
        self.plan.append(json_repair.loads(model_response))
