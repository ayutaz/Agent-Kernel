from typing import Dict, Any, Optional, List, Tuple
import math
from agentkernel_standalone.types.schemas.message import Message
from agentkernel_standalone.mas.agent.base.plugin_base import PerceivePlugin
from agentkernel_standalone.mas.agent.components import *
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class WisdomPerceivePlugin(PerceivePlugin):
    """Perceive plugin with knowledge discovery for Wisdom of Crowds experiment."""

    def __init__(self):
        super().__init__()
        self.global_tick = 0
        self.received_messages = []
        self.last_tick_messages = []
        self.surrounding_agents = []
        self.friends = []
        self.own_status = {}
        self.my_knowledge = []  # List of fragment IDs this agent knows
        self.my_knowledge_details = []  # List of {"id": "F0", "clue": "..."} for prompt
        self.nearby_knowledge_counts = []  # List of {"id": "agent_name", "knowledge": count}
        logger.info("WisdomPerceivePlugin initialized.")

    async def init(self):
        self.controller = self._component.agent.controller
        self.agent_id = self._component.agent.agent_id
        self.plan_comp = self._component.agent.get_component("plan")

    async def execute(self, current_tick: int):
        # --- Same as EasyPerceivePlugin ---
        agent_info = await self.controller.run_environment("space", "get_agent", self.agent_id)
        self.current_position = agent_info["position"]
        self.last_tick_messages = self.received_messages
        self.received_messages = []
        logger.info(f"Agent {self.agent_id} is at position {self.current_position}, at last tick, there are {len(self.last_tick_messages)} messages.")

        could_see_distance = 50
        self.surrounding_agents = []
        self.all_agents = await self.controller.run_environment("space", "get_all_agents")
        for agent in self.all_agents:
            if agent["id"] != self.agent_id:
                if math.sqrt(
                    (agent["position"][0] - self.current_position[0]) ** 2 +
                    (agent["position"][1] - self.current_position[1]) ** 2
                ) <= could_see_distance:
                    self.surrounding_agents.append(agent)

        logger.info(f"Agent {self.agent_id} looked around, and found {len(self.surrounding_agents)} agents.")

        # Enrich nearby agents with status (max 10)
        for agent in self.surrounding_agents[:10]:
            try:
                st = await self.controller.run_environment("status", "get_status", agent["id"])
                agent["status"] = st
            except Exception:
                pass

        # Fetch friend list
        try:
            self.friends = await self.controller.run_environment("relation", "get_friends", self.agent_id)
        except Exception:
            self.friends = []

        # Fetch own status
        try:
            self.own_status = await self.controller.run_environment("status", "get_status", self.agent_id)
        except Exception:
            self.own_status = {}

        # --- Knowledge discovery (NEW) ---
        try:
            newly_found = await self.controller.run_environment(
                "knowledge", "discover_nearby", self.agent_id, self.current_position
            )
            if newly_found:
                logger.info(f"Agent {self.agent_id} discovered {len(newly_found)} new knowledge fragments!")
        except Exception as e:
            logger.warning(f"Agent {self.agent_id}: knowledge discovery failed: {e}")

        # Get own knowledge set
        try:
            my_knowledge_set = await self.controller.run_environment(
                "knowledge", "get_agent_knowledge", self.agent_id
            )
            self.my_knowledge = list(my_knowledge_set)
        except Exception:
            self.my_knowledge = []

        # Build knowledge details for prompt (fragment ID + clue)
        # We need to access the knowledge plugin to get clue text
        # Use a simple format: the fragment ID list is enough for sharing
        self.my_knowledge_details = []
        try:
            for fid in sorted(self.my_knowledge):
                self.my_knowledge_details.append(fid)
        except Exception:
            pass

        # Get nearby agents' knowledge counts
        self.nearby_knowledge_counts = []
        for agent in self.surrounding_agents[:10]:
            try:
                count = await self.controller.run_environment(
                    "knowledge", "get_agent_knowledge_count", agent["id"]
                )
                self.nearby_knowledge_counts.append({"id": agent["id"], "knowledge": count})
            except Exception:
                pass

    async def get_received_messages(self) -> list:
        return list(self.received_messages)

    async def add_message(self, message: Message):
        logger.info(f"Agent {self.agent_id} received message from {message.from_id}: {message.content}")
        copyed_message = {"from_id": message.from_id, "kind": message.kind, "content": message.content}
        self.received_messages.append(copyed_message)
        logger.info(f"Agent {self.agent_id} stored message: {copyed_message}")
