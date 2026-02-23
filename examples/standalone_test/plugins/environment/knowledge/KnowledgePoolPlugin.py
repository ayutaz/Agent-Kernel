import random
import math
from typing import Dict, Any, Set, List, Optional
from agentkernel_standalone.mas.environment.base.plugin_base import GenericPlugin
from agentkernel_standalone.toolkit.logger import get_logger

logger = get_logger(__name__)


class KnowledgePoolPlugin(GenericPlugin):
    """Environment plugin managing knowledge fragments for Wisdom of Crowds experiment."""

    COMPONENT_TYPE = "knowledge"

    def __init__(self, fragment_count: int = 20, discovery_distance: float = 30.0,
                 map_size: int = 300, seed: int = 42):
        super().__init__()
        self.fragment_count = fragment_count
        self.discovery_distance = discovery_distance
        self.map_size = map_size

        # Generate random fragment positions
        rng = random.Random(seed)
        self.fragments: Dict[str, Dict[str, Any]] = {}
        for i in range(fragment_count):
            fid = f"F{i}"
            self.fragments[fid] = {
                "id": fid,
                "position": [rng.randint(0, map_size), rng.randint(0, map_size)],
                "clue": f"Knowledge fragment #{i}",
            }

        # Per-agent knowledge sets
        self._agent_knowledge: Dict[str, Set[str]] = {}
        # For velocity calculation
        self._prev_total_knowledge: int = 0

        logger.info(f"KnowledgePoolPlugin initialized with {fragment_count} fragments on {map_size}x{map_size} map.")

    async def discover_nearby(self, agent_id: str, agent_position: list) -> List[Dict[str, Any]]:
        """Discover knowledge fragments within discovery_distance of agent's position."""
        if agent_id not in self._agent_knowledge:
            self._agent_knowledge[agent_id] = set()

        newly_found = []
        ax, ay = agent_position[0], agent_position[1]
        for fid, frag in self.fragments.items():
            if fid in self._agent_knowledge[agent_id]:
                continue
            fx, fy = frag["position"]
            dist = math.sqrt((ax - fx) ** 2 + (ay - fy) ** 2)
            if dist <= self.discovery_distance:
                self._agent_knowledge[agent_id].add(fid)
                newly_found.append(frag)

        if newly_found:
            logger.info(f"Agent {agent_id} discovered {len(newly_found)} new fragments: {[f['id'] for f in newly_found]}")
        return newly_found

    async def share_knowledge(self, from_id: str, to_id: str, fragment_ids: list) -> int:
        """Transfer knowledge from one agent to another. Returns count of newly transferred fragments."""
        if from_id not in self._agent_knowledge:
            self._agent_knowledge[from_id] = set()
        if to_id not in self._agent_knowledge:
            self._agent_knowledge[to_id] = set()

        transferred = 0
        for fid in fragment_ids:
            if fid in self._agent_knowledge[from_id] and fid not in self._agent_knowledge[to_id]:
                self._agent_knowledge[to_id].add(fid)
                transferred += 1

        if transferred > 0:
            logger.info(f"Agent {from_id} shared {transferred} fragments with {to_id}")
        return transferred

    async def get_agent_knowledge(self, agent_id: str) -> set:
        """Return the set of fragment IDs known by an agent."""
        return set(self._agent_knowledge.get(agent_id, set()))

    async def get_agent_knowledge_count(self, agent_id: str) -> int:
        """Return the number of fragments known by an agent."""
        return len(self._agent_knowledge.get(agent_id, set()))

    async def get_collective_metrics(self) -> Dict[str, Any]:
        """Calculate and return collective knowledge metrics."""
        total_fragments = self.fragment_count

        # All known fragments across all agents
        all_known = set()
        individual_counts = []
        for agent_id, knowledge in self._agent_knowledge.items():
            all_known.update(knowledge)
            individual_counts.append(len(knowledge))

        if not individual_counts:
            individual_counts = [0]

        global_coverage = len(all_known) / total_fragments if total_fragments > 0 else 0.0
        avg_knowledge = sum(individual_counts) / len(individual_counts)
        max_knowledge = max(individual_counts)
        fully_informed = sum(1 for c in individual_counts if c >= total_fragments)

        # Gini coefficient
        knowledge_gini = self._calc_gini(individual_counts)

        # Knowledge velocity
        current_total = sum(individual_counts)
        velocity = current_total - self._prev_total_knowledge
        self._prev_total_knowledge = current_total

        return {
            "global_coverage": round(global_coverage, 4),
            "avg_individual_knowledge": round(avg_knowledge, 2),
            "max_individual_knowledge": max_knowledge,
            "fully_informed_agents": fully_informed,
            "knowledge_gini": round(knowledge_gini, 4),
            "knowledge_velocity": velocity,
            "total_fragments": total_fragments,
            "agent_count": len(self._agent_knowledge),
        }

    @staticmethod
    def _calc_gini(values: List[int]) -> float:
        """Calculate Gini coefficient for a list of values."""
        if not values or sum(values) == 0:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        cumsum = 0
        weighted_sum = 0
        for i, v in enumerate(sorted_vals):
            cumsum += v
            weighted_sum += (i + 1) * v
        mean = cumsum / n
        if mean == 0:
            return 0.0
        return (2.0 * weighted_sum) / (n * cumsum) - (n + 1) / n
