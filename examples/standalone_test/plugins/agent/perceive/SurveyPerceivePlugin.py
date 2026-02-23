from typing import Dict, Any, Optional, List, Tuple
import math
from agentkernel_standalone.types.schemas.message import Message
from agentkernel_standalone.mas.agent.base.plugin_base import PerceivePlugin
from agentkernel_standalone.mas.agent.components import *
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


ALL_REGION_IDS = ["riverside_park", "central_school", "north_hospital", "market_square", "industrial_complex"]


class SurveyPerceivePlugin(PerceivePlugin):
    """Perceive plugin for disaster response survey experiment."""

    def __init__(self):
        super().__init__()
        self.global_tick = 0
        self.received_messages = []
        self.last_tick_messages = []
        self.surrounding_agents = []
        self.friends = []
        self.own_status = {}
        # Survey-specific
        self.observation_summary = {}
        self.new_observation = None
        self.estimates = {}
        self.unvisited_regions = []
        self.occupation = ""
        logger.info("SurveyPerceivePlugin initialized.")

    async def init(self):
        self.controller = self._component.agent.controller
        self.agent_id = self._component.agent.agent_id
        self.plan_comp = self._component.agent.get_component("plan")

    async def execute(self, current_tick: int):
        # 1. Get position from space
        agent_info = await self.controller.run_environment("space", "get_agent", self.agent_id)
        self.current_position = agent_info["position"]
        self.last_tick_messages = self.received_messages
        self.received_messages = []
        logger.info(f"Agent {self.agent_id} is at position {self.current_position}, at last tick, there are {len(self.last_tick_messages)} messages.")

        # 2. Get surrounding agents within distance 50
        could_see_distance = 50
        self.surrounding_agents = []
        self.all_agents = await self.controller.run_environment("space", "get_all_agents")
        for agent in self.all_agents:
            if agent["id"] != self.agent_id:
                dist = math.sqrt(
                    (agent["position"][0] - self.current_position[0]) ** 2 +
                    (agent["position"][1] - self.current_position[1]) ** 2
                )
                if dist <= could_see_distance:
                    self.surrounding_agents.append(agent)

        logger.info(f"Agent {self.agent_id} looked around, and found {len(self.surrounding_agents)} agents.")

        # 3. Enrich nearby agents with status and occupation (max 10)
        for agent in self.surrounding_agents[:10]:
            try:
                st = await self.controller.run_environment("status", "get_status", agent["id"])
                agent["status"] = st
            except Exception:
                pass
            # Get occupation from the agent's profile component
            try:
                occ = await self.controller.run_agent_method(agent["id"], "profile", "get_profile", "occupation")
                agent["occupation"] = occ or "unknown"
            except Exception:
                agent["occupation"] = "unknown"

        # 4. Fetch friend list
        try:
            self.friends = await self.controller.run_environment("relation", "get_friends", self.agent_id)
        except Exception:
            self.friends = []

        # 5. Fetch own status
        try:
            self.own_status = await self.controller.run_environment("status", "get_status", self.agent_id)
        except Exception:
            self.own_status = {}

        # 6. Get own occupation from profile
        try:
            profile_plug = self._component.agent.get_component("profile")._plugin
            self.occupation = await profile_plug.get_profile("occupation") or ""
        except Exception:
            self.occupation = ""

        # 7. Observe region (auto-observe when within radius)
        self.new_observation = None
        try:
            obs = await self.controller.run_environment(
                "survey", "observe_region", self.agent_id, self.current_position, self.occupation
            )
            if obs:
                self.new_observation = obs
                logger.info(f"Agent {self.agent_id} observed {obs['region_name']}: {obs['observations']}")
        except Exception as e:
            logger.warning(f"Agent {self.agent_id}: survey observation failed: {e}")

        # 8. Get observation summary
        try:
            self.observation_summary = await self.controller.run_environment(
                "survey", "get_agent_observation_summary", self.agent_id
            )
        except Exception:
            self.observation_summary = {}

        # 9. Get estimates
        try:
            self.estimates = await self.controller.run_environment(
                "survey", "get_agent_estimates", self.agent_id
            )
        except Exception:
            self.estimates = {}

        # 10. Calculate unvisited regions (only count as visited if n_attrs > 0)
        visited_regions = set()
        if self.observation_summary:
            for rid, rdata in self.observation_summary.items():
                if rdata.get("n_attrs", 0) > 0:
                    visited_regions.add(rid)
        self.unvisited_regions = [rid for rid in ALL_REGION_IDS if rid not in visited_regions]

    async def get_received_messages(self) -> list:
        return list(self.received_messages)

    async def add_message(self, message: Message):
        logger.info(f"Agent {self.agent_id} received message from {message.from_id}: {message.content}")
        copyed_message = {"from_id": message.from_id, "kind": message.kind, "content": message.content}
        self.received_messages.append(copyed_message)
        logger.info(f"Agent {self.agent_id} stored message: {copyed_message}")
